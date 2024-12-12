import configparser
import logging
import os
import traceback
import json

from utils.constants import Constants as const


def get_file_contents(file_name):
    try:
        with open(file_name, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        logging.error("Obtained exception while reading file : {}".format(file_name))
        logging.error(e)
        logging.error(traceback.format_exc())


def write_to_file(file_name, file_content):
    try:
        with open(file_name, 'w') as properties_file:
            properties_file.write(file_content)
    except IOError as e:
        logging.error("Error writing to properties file: {}".format(e))


def write_config_to_file(config, file_name):
    try:
        with open(file_name, 'w') as properties_file:
            config.write(properties_file)
    except IOError as e:
        logging.error("Error writing to properties file : {}".format(e))


def log_restart_count():
    if os.path.isfile(const.AGENT_RESTART_COUNT_STORE):
        with open(const.AGENT_RESTART_COUNT_STORE, 'r+') as f:
            restart_count = f.read()
            f.seek(0)
            f.write(str(int(restart_count) + 1))
            f.truncate()
    else:
        with open(const.AGENT_RESTART_COUNT_STORE, 'w') as f:
            f.write(str(0))


def generate_ddx_id(ddx_id):
    if os.path.isfile(const.DDX_ID_STORE):
        with open(const.DDX_ID_STORE, 'r') as f:
            ddx_id = f.read()
            ddx_id = ddx_id.rstrip()
    else:
        with open(const.DDX_ID_STORE, 'w') as f:
            f.write(ddx_id)

    return ddx_id


def flatten_dict(dictionary, parent_key='', sep='.'):
    flattened = {}
    for key, value in dictionary.items():
        new_key = f'{parent_key}{sep}{key}' if parent_key else key
        if isinstance(value, dict):
            flattened.update(flatten_dict(value, new_key, sep=sep))
        else:
            flattened[new_key] = str(value)
    return flattened


def process_config_json(config_json, filters=None):
    if filters is None:
        filters = {}

    def apply_filters(ds):
        for k, v in filters.items():
            # TODO: Need to fix the object match (True is not False, None is None etc).
            #  str conversion and comparison is not a good idea.
            if str(ds.get(k, '')) != str(v):
                return False
        return True

    data_sources = config_json['data_sources']
    if not data_sources:
        logging.error("config does not contain data source information, exiting...")
        return

    filtered_ds = list(filter(apply_filters, data_sources))
    logging.info(f'Filtered Data Source: {filtered_ds}')
    if not filtered_ds:
        filtered_ds = data_sources

    config = configparser.ConfigParser()
    flattened_data_sources = [flatten_dict(data_source) for data_source in filtered_ds]
    for i, flattened_data in enumerate(flattened_data_sources):
        kind = flattened_data.get('kind')
        section_name = f'data_source_{kind}' if kind else f'data_source'
        config.add_section(section_name)

        for key, value in flattened_data.items():
            key = key.replace('_', '.')
            config.set(section_name, f'{kind}.{key}', value)

    return config


def load_properties():
    properties = {}
    try:
        config = configparser.ConfigParser()
        config.read(const.PROPERTIES_FILE_NAME)
        for section in config.sections():
            properties[section] = {}
            for key, value in config.items(section):
                properties[section][key] = value
    except FileNotFoundError:
        logging.info(f"Error: Properties file not found at {const.PROPERTIES_FILE_NAME}")
    return properties

def read_and_print_json(file_path,metrics_type):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            kafka_metrics = data.get("kafkaMetrics")
            broker_metrics = kafka_metrics.get(metrics_type)
            metrics_hash = {}  
            print("Broker Metrics are .....")
            for category, metrics in broker_metrics.items():
                values_array = []  
                for metric_description, metric_name in metrics.items():
                    values_array.append(metric_name) 
                metrics_hash[category] = values_array  
            print(metrics_hash)  
    except Exception as e:
        print(f"An error occurred while reading the JSON file: {e}")

