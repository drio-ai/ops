import json
import logging


class WSNotify:
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    @staticmethod
    def generic_handler(ws_client, frame):
        logging.info(frame.command)  # get commend
        logging.info(frame.headers)  # get headers
        logging.info(frame.body)  # get body

    @staticmethod
    def config_notify_handler(ws_client, frame):
        WSNotify.generic_handler(ws_client, frame)
        d = json.loads(frame.body)
        if d.get('type') == 'CONFIG_NOTIFY':
            logging.info('Sending config get')
            ws_client.send("/app/config", body=json.dumps({'id': '123456789'}))
