from time import sleep

from confluent_kafka import Producer
import socket
import pandas
import json
import argparse


def produce(topic, data):
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': socket.gethostname()
    }
    producer = Producer(conf)
    producer.produce(topic, key="id", value=data)
    producer.flush()


def load_msg_from_excel(path):
    excel_data_df = pandas.read_excel(path)
    json_str = excel_data_df.to_json(orient='records')
    data_list = json.loads(json_str)
    return data_list


if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-p", "--path", help="Path to excel file")
    parser.add_argument("-t", "--topic", help="kafka topic")

    # Read arguments from command line
    args = parser.parse_args()

    if args.path and args.topic:
        print(f'Excel path: {args.path}')
        records = load_msg_from_excel(args.path)
        for r in records:
            print(json.dumps(r))
            produce(args.topic, json.dumps(r))
            sleep(3)
    else:
        print('Missing excel file path or kafka topic')
        exit(0)
