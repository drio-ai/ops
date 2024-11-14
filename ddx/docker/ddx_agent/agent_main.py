import asyncio  # Async tasks and event loop management
import json     # JSON handling for data serialization
import logging  # Logging for error and event tracking
import os       # OS environment handling
import signal   # Signal handling for graceful shutdown
import time     # Basic time functions
import uuid     # Unique ID generation
import socket   # Network-related functionalities
import re       # Regular expressions for data processing
from typing import Dict, Optional, List, Any  # Type annotations

# External libraries for JMX and Kafka
from jmxquery import JMXConnection, JMXQuery  # JMX queries for monitoring Kafka
from confluent_kafka import Consumer  # Kafka consumer for anomaly detection
from time import sleep  # Sleep for delaying tasks
from threading import Thread  # Multithreading for concurrent execution

# Project-specific backend and core modules
from backends.drio_backend import Drio  # Backend for DDX registration and configuration
from core.app_urls import STATS  # URL constants for stats endpoint
from core.ws_notify import WSNotify  # WebSocket notifications

# Statistics and anomaly processing
from stats.stats import Stats  # Statistics collection
from stream_processors.anomaly import AnomalyPredictor  # Anomaly detection processing

# Utilities and constants
from utils.constants import Constants  # Constants used throughout the project
from utils.file_utils import log_restart_count, generate_ddx_id, load_properties  # File utilities
from utils.kafka_utils import KafkaConsumerClient  # Kafka utility functions

# Model loading and PDF processing
from model_components.model_config import load_spacy_model, load_bertopic_model  # Model loading
from model_components.PDFExtractDemo.pdf_processor import start_pdf_extraction_engine  # PDF processing

# Logger configuration
LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='/var/log/ddx-agent.out.log', format=LOG_FORMAT, level=logging.INFO)

# IDs and defaults
DDX_ID: str = str(uuid.uuid4())
SERVICE_PROVIDER: str = os.getenv('SERVICE_PROVIDER', 'local')
DDX_INSTANCE_NAME: str = os.getenv('DDX_INSTANCE_NAME', socket.gethostname())

class DDXAgent:
    def __init__(self) -> None:
        """
        Initializes the DDXAgent with default values, loads properties, and sets up signal handling.
        """
        global DDX_ID
        DDX_ID = generate_ddx_id(DDX_ID)
        log_restart_count()

        # Initialize drio_backend but skip registration for now
        self.drio_backend: Drio = Drio(DDX_ID, DDX_INSTANCE_NAME, SERVICE_PROVIDER)
        
        #-----------------------------------------------------
        #       Registration Block (Commented)
        #-----------------------------------------------------
        """
        try:
            self.drio_backend.pull_config({'secure': True})
            response = self.drio_backend.register_ddx()
            logging.info(f'Registration response: {response}')
            ddx_id = response.get('ddx_instance', {}).get('id')
            if ddx_id:
                DDX_ID = ddx_id
        except Exception as ex:
            logging.error('Registration failed, exiting..')
            sleep(10)
            raise
        """

        # Set ws_endpoint manually if needed or comment this out if ws_client is not required
        ws_endpoint: Optional[str] = os.getenv('WS_URL') or Constants.LOCAL_WS
        self.ws_client: Optional[Any] = None

        if ws_endpoint:
            pass
        else:
            raise Exception('Unable to contact ws endpoint, not defined')

        # Load properties and initialize attributes
        self.properties: Dict[str, Any] = load_properties()
        self.stats_collector: Stats = Stats(self.properties, Constants.AGENT_RESTART_COUNT_STORE,
                                            Constants.SE_RESTART_COUNT_STORE)
        self.kill_now: bool = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        
        #-----------------------------------------------------
        #               Model Loading
        #-----------------------------------------------------
        # Track model load times
        start_time: float = time.time()
        self.ner_model: Any = load_spacy_model()
        ner_model_load_time: float = time.time() - start_time
        logging.info(f"Time taken to load SpaCy NER model: {ner_model_load_time:.2f} seconds")

        start_time = time.time()
        self.topic_processor: Any = load_bertopic_model()
        bertopic_load_time: float = time.time() - start_time
        logging.info(f"Time taken to load BERTopic model: {bertopic_load_time:.2f} seconds")

    #-----------------------------------------------------
    #               Graceful Exit
    #-----------------------------------------------------
    def exit_gracefully(self, *args: Any) -> None:
        """
        Signal handler to set kill_now flag for a graceful shutdown.
        """
        self.kill_now = True

    #-----------------------------------------------------
    #           WebSocket Connection
    #-----------------------------------------------------
    def connect(self) -> None:
        """
        Establishes a WebSocket connection if ws_client is defined.
        """
        try:
            if self.ws_client:
                self.ws_client.connect()
        except Exception as e:
            logging.error(f"Error connecting WebSocket: {e}")

    #-----------------------------------------------------
    #           Statistics Collection
    #-----------------------------------------------------
    def collect_stats(self) -> None:
        """
        Collects and sends stats through the stats collector.
        """
        try:
            self.stats_collector.collect()
        except Exception as e:
            logging.error(f"Error in collect_stats: {e}")

    #----------------------------------------------------
    #           WebSocket Subscription
    #-----------------------------------------------------
    def subscribe(self) -> None:
        """
        Subscribes the WebSocket client to specific topics.
        """
        try:
            if self.ws_client:
                self.ws_client.subscribe('/user/queue/reply', callback=WSNotify.generic_handler)
                self.ws_client.subscribe('/user/queue/errors', callback=WSNotify.generic_handler)
                self.ws_client.subscribe('/topic/notify', callback=WSNotify.config_notify_handler)
        except Exception as e:
            logging.error(f"Error during WebSocket subscription: {e}")

    #-----------------------------------------------------
    #                   Emit Stats
    #-----------------------------------------------------
    def emit(self, **stats: Dict[str, Any]) -> None:
        """
        Emits the stats to the WebSocket endpoint.
        """
        try:
            stats.update({'id': DDX_ID})
            payload: str = json.dumps(stats)
            if self.ws_client:
                self.ws_client.send(STATS, body=payload)
        except Exception as e:
            logging.error(f"Error in emit: {e}")

    #-----------------------------------------------------
    #           Anomaly Detection (Kafka)
    #-----------------------------------------------------
    def anomaly_predict(self) -> None:
        """
        Placeholder for anomaly prediction with Kafka. Currently commented out.
        """
        """
        try:
            kc = KafkaConsumerClient()
            kafka_configs = self.properties.get(Constants.KAFKA_CONFIG_SECTION, {})
            brokers = kafka_configs.get(Constants.KAFKA_ENDPOINTS, '')
            ds_id = kafka_configs.get(Constants.KAFKA_DS_IS)

            monitored_topics = kafka_configs.get(Constants.MONITORED_SUBJECTS, 'SalesforceOrders')
            security_proto = 'PLAINTEXT'
            if kafka_configs.get('kafka.secure', 'True').lower() == 'true':
                security_proto = 'SSL'

            conf = {
                'bootstrap.servers': brokers,
                'group.id': 'anomaly_detector',
                'enable.auto.commit': 'false',
                'auto.offset.reset': 'latest',
                'security.protocol': security_proto,
            }

            consumer = Consumer(conf)
            logging.info('------ Anomaly Detection Engine Started ------')
            kc.consume(consumer, monitored_topics.split(','),
                       AnomalyPredictor(Constants.SUBJECT_METADATA, Constants.CLUSTER_MODELS, ds_id).predict)
        except Exception as e:
            logging.error(f"Error in anomaly_predict: {e}")
        """

    #-----------------------------------------------------
    #                   JMX Query
    #-----------------------------------------------------
    def query_jmx(self, jmx_host: str, jmx_port: int, jmx_username: Optional[str], 
                  jmx_password: Optional[str], queries: List[JMXQuery]) -> Dict[str, Any]:
        """
        Executes JMX queries and returns the results.
        """
        try:
            jmx = JMXConnection(f"service:jmx:rmi:///jndi/rmi://{jmx_host}:{jmx_port}/jmxrmi", jmx_username, jmx_password)
            metrics = jmx.query(queries)

            formatted_metrics: Dict[str, Any] = {}
            for metric in metrics:
                metric_name: str = metric.to_query_string()
                metric_value: Any = metric.value
                formatted_metrics[metric_name] = metric_value
            return formatted_metrics
        except Exception as e:
            logging.error(f"An error occurred in query_jmx: {e}")
            raise RuntimeError(f"An error occurred in query_jmx: {e}")

    #-----------------------------------------------------
    #               Fetch Producer Metrics
    #-----------------------------------------------------
    def get_producer_metrics(self, jmx_host: str, jmx_port: int, jmx_username: Optional[str], 
                             jmx_password: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Retrieves metrics for Kafka producers.
        """
        try:
            queries: List[JMXQuery] = [JMXQuery("kafka.producer:*")]
            return self.query_jmx(jmx_host, jmx_port, jmx_username, jmx_password, queries)
        except RuntimeError as e:
            logging.error(f"Error fetching producer metrics: {e}")
            return None

    #-----------------------------------------------------
    #               Fetch Consumer Metrics
    #-----------------------------------------------------
    def get_consumer_metrics(self, jmx_host: str, jmx_port: int, jmx_username: Optional[str], 
                             jmx_password: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Retrieves metrics for Kafka consumers.
        """
        try:
            queries: List[JMXQuery] = [JMXQuery("kafka.consumer:*")]
            return self.query_jmx(jmx_host, jmx_port, jmx_username, jmx_password, queries)
        except RuntimeError as e:
            logging.error(f"Error fetching consumer metrics: {e}")
            return None

    #-----------------------------------------------------
    #               Fetch Broker Metrics
    #-----------------------------------------------------
    def get_kafka_broker_metrics(self, jmx_host: str, jmx_port: int, jmx_username: Optional[str], 
                                 jmx_password: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Retrieves metrics for Kafka brokers.
        """
        try:
            queries: List[JMXQuery] = [JMXQuery("kafka.server:*")]
            return self.query_jmx(jmx_host, jmx_port, jmx_username, jmx_password, queries)
        except RuntimeError as e:
            logging.error(f"Error fetching Kafka broker metrics: {e}")
            return None

    #-----------------------------------------------------
    #           Convert to Nested JSON
    #-----------------------------------------------------
    def convert_to_nested_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts flat metric data into nested JSON structure.
        """
        nested_data: Dict[str, Any] = {}
        for key, value in data.items():
            parts: List[str] = re.split(r'[:,/=]', key)
            d: Dict[str, Any] = nested_data
            for part in parts[:-1]:
                if part not in d:
                    d[part] = {}
                d = d[part]
            d[parts[-1]] = value
        return nested_data

    #-----------------------------------------------------
    #                      Spacy NER
    #-----------------------------------------------------
    async def spacy_model(self, main_json: List[Dict[str, Any]], nest_number: int = 0) -> Dict[str, Any]:
        """
        Processes main_json using SpaCy NER model.
        """
        try:
            result: Dict[str, Any] = self.ner_model.process_json_data({"main_json": main_json})
            logging.info("SpaCy model processed the main_json.")
            return result
        except Exception as e:
            logging.error(f"Error processing main_json with SpaCy model: {e}")
            return {}

    #   -----------------------------------------------------
    #                 BERTopic Processing
    #   -----------------------------------------------------
    async def process_bertopic(self, header_key: str, filename: str) -> Dict[str, Any]:
        """
        Processes header_key using BERTopic model.
        """
        try:
            topic_result: str = self.topic_processor.process_text(header_key, filename)
            logging.info("BERTopic model processed the header_key.")
            return json.loads(topic_result)
        except Exception as e:
            logging.error(f"Error processing header_key with BERTopic model: {e}")
            return {}

    #----------------------------------------------
    #       Run Synchronous Tasks
    #----------------------------------------------
    async def run_synchronous_tasks(self) -> None:
        """
        Executes PDF extraction, SpaCy, and BERTopic tasks in a loop.
        """
        while not self.kill_now:
            try:
                pdf_data: Dict[str, Any] = start_pdf_extraction_engine()
                if not pdf_data:
                    logging.warning("No PDF data processed; retrying in 30 seconds.")
                    await asyncio.sleep(30)
                    continue

                filename: str = pdf_data.get("filename", "")
                main_json: List[Dict[str, Any]] = pdf_data.get("main_json", [])
                header_key: str = pdf_data.get("processed_data", "")

                spacy_output, bertopic_output = await asyncio.gather(
                    self.spacy_model(main_json),
                    self.process_bertopic(header_key, filename)
                )

                final_output: Dict[str, Any] = {
                    "filename": filename,
                    "spacy_output": spacy_output,
                    "bertopic_output": bertopic_output
                }
                
                logging.info(f"Processed output:\n{json.dumps(final_output, indent=4)}")
                await asyncio.sleep(30)
            except Exception as e:
                logging.error(f"Error during synchronous tasks: {e}")

    #----------------------------------------------
    #           Metrics Collector
    #----------------------------------------------
    async def metrics_collector(self) -> None:
        """
        Periodically collects and logs producer, consumer, or server metrics.
        """
        while True:
            try:
                await asyncio.sleep(Constants.FETCH_INTERVAL)

                if Constants.METRICS_TYPE == 'producer':
                    producer_metrics = self.get_producer_metrics(Constants.IP, Constants.PRODUCER_PORT, Constants.USERNAME, Constants.PASSWORD)
                    if producer_metrics:
                        nested_producer_metrics = self.convert_to_nested_json(producer_metrics)
                        print(json.dumps(nested_producer_metrics, indent=4))

                elif Constants.METRICS_TYPE == 'consumer':
                    consumer_metrics = self.get_consumer_metrics(Constants.IP, Constants.CONSUMER_PORT, Constants.USERNAME, Constants.PASSWORD)
                    if consumer_metrics:
                        nested_consumer_metrics = self.convert_to_nested_json(consumer_metrics)
                        print(json.dumps(nested_consumer_metrics, indent=4))

                elif Constants.METRICS_TYPE == 'server':
                    kafka_metrics = self.get_kafka_broker_metrics(Constants.IP, Constants.SERVER_PORT, Constants.USERNAME, Constants.PASSWORD)
                    if kafka_metrics:
                        nested_kafka_metrics = self.convert_to_nested_json(kafka_metrics)
                        print(json.dumps(nested_kafka_metrics, indent=4))

            except Exception as e:
                logging.error(f"An error occurred in metrics_collector: {e}")

    #----------------------------------------------
    #                   Run
    #----------------------------------------------
    async def run(self) -> None:
        """
        Main run method to start synchronous tasks and metrics collection.
        """
        await asyncio.gather(
            self.run_synchronous_tasks(),
            self.metrics_collector()
        )

if __name__ == '__main__':
    agent: DDXAgent = DDXAgent()
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        pass

    # Run anomaly prediction in a separate thread
    t_anomaly: Thread = Thread(target=agent.anomaly_predict)
    t_anomaly.daemon = True
    t_anomaly.start()

    last_stats_collect: int = 0
    while not agent.kill_now:
        now: int = int(time.time())
        if now - last_stats_collect > 20:
            t_stats: Thread = Thread(target=agent.collect_stats)
            t_stats.daemon = True
            t_stats.start()
            last_stats_collect = now
        sleep(5)
    else:
        agent.drio_backend.deregister_ddx()
