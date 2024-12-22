import sys

from confluent_kafka import ConsumerGroupState, KafkaError, KafkaException
from confluent_kafka.admin import AdminClient
from time import sleep


class KafkaConsumerClient:
    def __init__(self):
        self.running = True

    def consume(self, consumer, topics, fn):
        try:
            consumer.subscribe(topics)
            while self.running:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                         (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    decoded_msg = msg.value().decode('utf8')
                    fn(decoded_msg, msg.topic())
        finally:
            # Close down consumer to commit final offsets.
            consumer.close()

    def shutdown(self):
        self.running = False


def get_consumer_info(admin_client):
    consumer_group_info = []
    consumer_group_ids = []

    fs = admin_client.list_consumer_groups()

    while not fs.done() and not fs.cancelled():
        sleep(0.5)
    else:
        try:
            cg = fs.result()
            # print(cg.valid)
            for cg_obj in cg.valid:
                # print(cg_obj.group_id)
                # print(cg_obj.state)
                if cg_obj.state == ConsumerGroupState.STABLE:
                    consumer_group_ids.append(cg_obj.group_id)
        except Exception as e:
            raise

    fs_map = admin_client.describe_consumer_groups(consumer_group_ids)
    for name, fs in fs_map.items():
        while not fs.done() and not fs.cancelled():
            sleep(0.5)
        else:
            try:
                des = fs.result()
                for m in des.members:
                    # print('--------------------')
                    # print(m.client_id)
                    # print(m.host)
                    for tp in m.assignment.topic_partitions:
                        c_info = {
                            'topic': tp.topic,
                            'partition': tp.partition,
                            'consumer_group': m.client_id,
                            'consumer_host': m.host
                        }
                        consumer_group_info.append(c_info)
                        # print(tp.topic, tp.partition)
            except Exception as e:
                raise

    return consumer_group_info


def get_topic_info(admin_client):
    return [{'topic': name, 'partition_count': len(topic_meta.partitions)} for name, topic_meta in
            ac.list_topics().topics.items()]


if __name__ == '__main__':
    ac = AdminClient({'bootstrap.servers': '127.0.0.1:9092'})
    # print(get_consumer_info(ac))
    print(get_topic_info(ac))
