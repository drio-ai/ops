import configparser
import json
import logging
import os

from connectors.kafka_connector_v2 import KafkaConnect
from connectors.supervisor_connector import SupervisorConnector
from connectors.schema_registry_connector import SRConnect
from core.stats_exporter import StatsExporter
from utils.constants import Constants
from utils.file_utils import write_config_to_file


class Stats(StatsExporter):
    def __init__(self, prop, agent_re_count_store, se_re_count_store):
        super().__init__()
        self.agent_re_count_store = agent_re_count_store
        self.se_re_count_store = se_re_count_store
        self.prop = prop

        # process params
        kafka_brokers = os.environ.get('BOOTSTRAP_SERVERS')
        # sr_endpoint = os.environ.get('SCHEMA_REGISTRY')
        security_proto = 'PLAINTEXT'

        if prop and Constants.KAFKA_CONFIG_SECTION in prop:
            logging.info(f'loaded properties from file {Constants.PROPERTIES_FILE_NAME}')
            self.kafka_properties = prop[Constants.KAFKA_CONFIG_SECTION]
            kafka_brokers = self.kafka_properties.get(Constants.KAFKA_ENDPOINTS, '')
            logging.info("kafka_brokers {} ".format(kafka_brokers))

            if self.kafka_properties.get('kafka.secure', 'True').lower() == 'true':
                security_proto = 'SSL'

            # schema registry not required for now
            # sr_endpoint = prop.get(const.SR_ENDPOINTS, sr_endpoint)
            # logging.info("sr_endpoint {} ".format(sr_endpoint))

        try:
            self.kafka_connector = KafkaConnect({
                'security.protocol': security_proto,
                'bootstrap.servers': kafka_brokers
            })
            # self.sr_connector = SRConnect(sr_endpoint) # schema registry not required for now
            self.supervisor_connector = SupervisorConnector(self.agent_re_count_store, self.se_re_count_store)
        except Exception as ex:
            # if not able to connect to customer Kafka, don't come up.
            # let the supervisord handle the process restart.
            logging.error(f'Unable to connect to Kafka {kafka_brokers}')
            raise

    def collect(self):
        logging.info('collecting kafka stats ...')
        try:
            topic_info = self.kafka_connector.get_topic_info()

            # When a new topic is discovered, pass it to streaming engine as well
            topic_list = [stat.get('name') for stat in topic_info if stat.get('name') is not None]
            topics = list(filter(lambda x: not x.startswith('_'), topic_list))
            is_diff = self.diff_datasets(topics)
            if is_diff:
                self.reload_stream_engine(topics)

            consumer_info = self.kafka_connector.get_consumer_info()
            # schemas = self.sr_connector.get_schema_stats()  # schema registry not required for now

            # supervisor
            system = self.supervisor_connector.get_process_stats(processes=['ddx:ddx-agent', 'ddx:stream-engine'])
            stats = {
                'data_source_id': self.kafka_properties.get('kafka.id'),
                'topics': topic_list,
                'topics_details': topic_info,
                'consumer_details': consumer_info,
                'ddx_process_details': system,
                # 'schemas': schemas,  # schema registry not required for now
            }

            # export the stats to the controller
            cluster_id = os.environ.get('DDX_CLUSTER_ID')
            self.export(stats, f'resources/ddx-clusters/{cluster_id}/datasets')

            # TODO: Emit to WS
            # agent.emit(**stats)

            # log it
            logging.info('----------------------- start ----------------------')
            logging.info(json.dumps(stats, indent=4))
            logging.info('----------------------- end ------------------------')
        except Exception as ex:
            logging.error('Failed to collect stats ', ex)

    def reload_stream_engine(self, topics):
        topic_str = ','.join(topics)
        self.prop[Constants.KAFKA_CONFIG_SECTION][Constants.KAFKA_DATASET_CONFIG] = topic_str
        config = configparser.ConfigParser()
        config.read_dict(self.prop)
        write_config_to_file(config, Constants.PROPERTIES_FILE_NAME)
        self.supervisor_connector.reload_process('ddx:stream-engine')

    @staticmethod
    def diff_datasets(topics):
        stored_datasets_str = os.environ.get(Constants.KAFKA_JSON_DATASETS, None)
        if stored_datasets_str is None:
            os.environ[Constants.KAFKA_JSON_DATASETS] = ','.join(topics)
            return True
        else:
            stored_datasets = stored_datasets_str.split(',')
            if set(stored_datasets) != set(topics):
                os.environ[Constants.KAFKA_JSON_DATASETS] = ','.join(topics)
                return True

        return False
