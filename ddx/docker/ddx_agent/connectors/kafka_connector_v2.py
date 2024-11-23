from confluent_kafka import ConsumerGroupState
from confluent_kafka.admin import AdminClient
from gevent.time import sleep

LOCAL_BOOTSTRAP_SERVERS = 'localhost:9092'


class KafkaConnect:
    def __init__(self, kwargs):
        if kwargs.get('bootstrap.servers') is None:
            kwargs['bootstrap.servers'] = LOCAL_BOOTSTRAP_SERVERS

        self.admin_client = AdminClient(kwargs)

    def get_consumer_info(self):
        consumer_group_info = []
        consumer_group_ids = []

        fs = self.admin_client.list_consumer_groups()

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

        if not consumer_group_ids:
            return consumer_group_info

        fs_map = self.admin_client.describe_consumer_groups(consumer_group_ids)
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

    def get_topic_info(self):
        return [{'name': name, 'partition_count': len(topic_meta.partitions)} for name, topic_meta in
                self.admin_client.list_topics().topics.items()]
