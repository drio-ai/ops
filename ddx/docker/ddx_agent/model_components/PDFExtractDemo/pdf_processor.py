
import base64
import json
import logging
import sys
import time
import re
from confluent_kafka import Consumer, KafkaError, KafkaException
from typing import List, Dict, Union
import fitz  # pymupdf
from PDFExtractDemo.extract_helper import *  # Assuming the updated extract_helper.py is in this path
from utils.constants import Model
import pprint
# ------------------------------------------------------------------------------
#               Handles Kafka Consumer logic
# ------------------------------------------------------------------------------

class KafkaConsumerClient:
    """
    A Kafka consumer client for consuming messages from specified topics.

    Methods:
    --------
    consume(consumer: Consumer, topics: List[str], fn: callable) -> Union[Dict[str, str], None]:
        Consumes messages from the given Kafka topics, processes them using the provided function,
        and returns the result.

    shutdown() -> None:
        Stops the consumer loop and shuts down the client.
    """
    def __init__(self) -> None:
        self.running: bool = True

    def consume(self, consumer: Consumer, topics: List[str], fn: callable) -> Union[Dict[str, str], None]:
        try:
            consumer.subscribe(topics)
            while self.running:
                if (msg := consumer.poll(0.1)) is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                         (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    decoded_msg: str = msg.value().decode('utf8')
                    result: Union[Dict[str, str], None] = fn(decoded_msg, msg.topic())
                    return result
        finally:
            consumer.close()
            self.shutdown()

    def shutdown(self) -> None:
        self.running = False

# --------------------------------------------------------------------------------
#               PDF-related module: Handles PDF processing logic
# --------------------------------------------------------------------------------

class PDFProcessor:
    """
    A processor for handling PDF data, decoding, and extracting relevant information.

    Methods:
    --------
    process_message(encoded_pdf: str, filename: str) -> Union[Dict[str, str], None]:
        Decodes the base64-encoded PDF, processes the content, and returns the extracted data
        with the associated filename.

    output_pdf(stream_data: bytes) -> Union[str, None]:
        Processes the PDF stream to extract structured information, including headers and tables,
        and returns it as a JSON string.
    """

    def process_message(self, encoded_pdf: str, filename: str) -> Union[Dict[str, str], None]:
        try:
            if decoded_pdf := base64.b64decode(encoded_pdf):
                if json_str := self.output_pdf(decoded_pdf):
                    output_dict: dict = json.loads(json_str)
                    print(json.dumps(output_dict, indent=4))

                    
                    header_only: str = output_dict.get('header_only', '')
                    header_key: str = output_dict.get('header_key', '')
                    

                    return {
    "filename": filename,
    "processed_data": f"{header_only} {header_key}",
    "main_json": output_dict.get("main_json")
}

                else:
                    logging.error("Processing failed, no output generated.")
                    return None
        except Exception as e:
            logging.error(f"An error occurred in process_message: {e}")
            return None

    def output_pdf(self, stream_data: bytes) -> Union[str, None]:
        try:
            pg_doc_list: List[tuple] = path_to_pg_sec(stream_data, type_='stream')
            pages: List[fitz.Page] = list(fitz.open(stream=stream_data).pages())
            tab_list: List[Union[List, str]] = []
            pg_: int = 0
            for pg, docsec in pg_doc_list:
                if re.match(r'\#{2}([\d\.\;]+)\#{2}', docsec):
                    present_json: List = [i for i in extract_table(docsec=docsec, page=pages[pg])]
                    if pg != pg_:
                        tab_list = traverse_page_from_last_tab(tab_list, pres_tab=present_json)
                    else:
                        tab_list.append(present_json)
                else:
                    text_content: List = [i for i in extract_text(docsec)]
                    tab_list.append(text_content)
                pg_ = pg

            output_dict: dict = {
                'main_json': tab_list,
                'header_key': " ".join([" ".join(get_key_header(j)) for i, j in tab_list]).replace('\n', ' ').replace(':', ' '),
                'header_only': " ".join([" ".join(extract_headers(j)) for i, j in tab_list]).replace(':', '').replace('\n', ' '),
            }
            return json.dumps(output_dict, indent=4)
        except Exception as e:
            logging.error(f"An error occurred in output_pdf: {e}")
            return None

# ------------------------------------------------------------------------------
#        Kafka and PDF integration module: Handles message processing
# ------------------------------------------------------------------------------

def wrapped_process_message(encoded_msg: str, topic: str) -> Union[Dict[str, str], None]:
    """
    Decodes a JSON-encoded message, extracts PDF content, and processes it.

    Parameters:
    -----------
    encoded_msg : str
        The JSON-encoded message containing the filename and encoded PDF content.
    topic : str
        The Kafka topic from which the message was consumed (not used in processing).

    Returns:
    --------
    Union[Dict[str, str], None]
        The processed PDF data with the associated filename, or None if processing fails.
    """
    try:
        start_time = time.time()
        msg_dict = json.loads(encoded_msg)
        filename = msg_dict.get("filename", "")
        encoded_pdf = msg_dict.get("encoded_content", "")

        processor: PDFProcessor = PDFProcessor()
        result = processor.process_message(encoded_pdf, filename)
        end_time = time.time()
        logging.info(f"========== PDF extraction time: {end_time - start_time:.2f} seconds =====")

        return result
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON message: {e}")
        return None

# ----------------------------------------------------------------------
#       Kafka Engine module: Starts the Kafka consumer for PDF processing
# ----------------------------------------------------------------------

def start_pdf_extraction_engine() -> Union[Dict[str, str], None]:
    """
    Initializes and starts the PDF Extraction Engine by consuming messages from a Kafka topic.

    Configures Kafka consumer settings, starts the consumer client, and processes messages
    using the wrapped_process_message function.

    Returns:
    --------
    Union[Dict[str, str], None]
        The processed result from the PDF extraction, or None if an error occurs.
    """
    kafka_conf: dict = {
        'bootstrap.servers': str(Model.IP) + ":" + str(Model.CONSUMER_PORT),
        'group.id': str(Model.GROUP_ID),
        'enable.auto.commit': False,
        'auto.offset.reset': 'latest'
    }
    topic: str = str(Model.TOPIC_NAME)

    try:
        kc: KafkaConsumerClient = KafkaConsumerClient()
        logging.info('------ PDF Extraction Engine Started ------')

        result: Union[Dict[str, str], None] = kc.consume(Consumer(kafka_conf), [topic], wrapped_process_message)
        return result

    except Exception as e:
        logging.error(f"An error occurred in start_pdf_extraction_engine: {e}")
        return None

if __name__ == '__main__':
    result = start_pdf_extraction_engine()
    if result:
        print("")
