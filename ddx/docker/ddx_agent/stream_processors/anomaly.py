import json
import logging
import os
import pickle
import pathlib
import time
from json.decoder import JSONDecodeError

import hdbscan
import pandas as pd

from core.stats_exporter import StatsExporter
from stream_processors.preprocessor import clean_column_names, drop_columns, preprocess_numerical_features, \
    convert_to_category, query_kd_tree


class AnomalyPredictor(StatsExporter):
    def __init__(self, sub_meta, cluster_models, data_source_id):
        super().__init__()
        self.data_source_id = data_source_id
        self.subject_meta_info = {}
        self.hdb_cluster_map = {}
        self.revered_category_mapping = {}
        sub_meta_abs_path = pathlib.Path(__file__).parent.parent / sub_meta
        cluster_models_abs_path = pathlib.Path(__file__).parent.parent / cluster_models
        try:
            with open(sub_meta_abs_path, 'r') as fp:
                self.subject_meta_info = json.load(fp)

            with open(cluster_models_abs_path, 'rb') as fp:
                self.hdb_cluster_map = pickle.load(fp)
        except:
            # TODO: implement specific exception
            raise

    @staticmethod
    def json_to_df_converter(msg):
        json_msg = None
        try:
            json_msg = json.loads(msg)
        except JSONDecodeError as e:
            pass

        return pd.json_normalize(json_msg) if json_msg is not None else None

    def predict(self, msg, topic):
        # pre-processing
        df = self.json_to_df_converter(msg)
        if df is None:
            logging.warning('Unable to decode the json message')
            return

        model = self.hdb_cluster_map.get(topic, {}).get('model', None)
        scale = self.hdb_cluster_map.get(topic, {}).get('scale', None)
        encoder_map = self.hdb_cluster_map.get(topic, {}).get('encoder', None)
        kd_tree = self.hdb_cluster_map.get(topic, {}).get('kd_tree', None)

        if not all([model, scale, encoder_map, kd_tree]):
            logging.error('Error: prediction model/scale/encoder/kd_tree is not available')
            return

        df_copy = df.copy(deep=True)
        original_record = df_copy.to_dict(orient='records')[0]

        # metadata
        metadata = self.subject_meta_info.get(topic, {})
        categorical_columns = metadata.get('categories')
        numerical_features = metadata.get('numerical')

        # cache model metadata
        if self.revered_category_mapping.get(topic) is None:
            self.revered_category_mapping[topic] = {k: {v1: k1 for k1, v1 in v.items()} for k, v in encoder_map.items()}

        if categorical_columns and numerical_features:
            # sanitize data
            df = clean_column_names(df)
            # TODO: remove a column if all the values are empty.
            ignored_columns = set(df.columns.tolist()) - (
                set(categorical_columns).union(set(numerical_features)))
            try:
                df = drop_columns(df, list(ignored_columns))
                # TODO: remove a row if any of the column value is empty
                preprocess_numerical_features(df, numerical_features, scale)
                convert_to_category(df, categorical_columns)
                for col in categorical_columns:
                    df[col] = df[col].replace(encoder_map[col])
            except Exception as e:
                logging.error(f'{str(e)}, ignored below data frame')
                logging.error(original_record)
                return

            # predict
            labels, strengths = hdbscan.approximate_predict(model, df)
            if labels[0] == -1:
                anomaly_stats = {
                    "data_source_id": self.data_source_id,
                    "name": topic,
                    "timestamp": round(time.time() * 1000),
                    "event_type": "Cluster Anomaly",
                    "anomaly_method": "Comparison",
                    "record": original_record
                }
                logging.info("Anomaly detected: ")
                logging.info(json.dumps(original_record, indent=4))
                distances, cluster_indices = query_kd_tree(kd_tree, df, k=3)
                logging.info(f'Distances from cluster points: {distances[0]}')
                logging.info(f'Cluster Indices: {cluster_indices[0]}')
                closest_points = []
                for index in cluster_indices[0]:
                    data_point = {}
                    trained_df = pd.DataFrame(kd_tree.data[index:index + 1], columns=metadata.get('all'))
                    inverse_transformed = scale.inverse_transform(trained_df[numerical_features], copy=True)

                    # categories
                    for cc in categorical_columns:
                        data_point.update(
                            {cc: self.revered_category_mapping[topic].get(cc, {}).get(trained_df[cc].values[0])})

                    # numerical features
                    for idx, nf in enumerate(numerical_features):
                        data_point.update({nf: int(inverse_transformed[0][idx])})

                    closest_points.append(data_point)

                logging.info(f'Closest Points : {closest_points}')
                anomaly_stats.update({'closest_data_points': closest_points})
                cluster_id = os.environ.get('DDX_CLUSTER_ID')
                anomaly_ep = f'resources/ddx-clusters/{cluster_id}/anomalies'
                self.export(anomaly_stats, anomaly_ep)


if __name__ == '__main__':
    from utils.constants import Constants
    from utils.kafka_utils import KafkaConsumerClient
    from confluent_kafka import Consumer
    kc = KafkaConsumerClient()
    conf = {'bootstrap.servers': 'localhost:9092',
            'group.id': 'anomaly_detector',
            'enable.auto.commit': 'false',
            'auto.offset.reset': 'latest'}

    consumer = Consumer(conf)
    kc.consume(consumer, ['SalesforceOrders'],
               AnomalyPredictor(Constants.SUBJECT_METADATA, Constants.CLUSTER_MODELS, 'x').predict)
