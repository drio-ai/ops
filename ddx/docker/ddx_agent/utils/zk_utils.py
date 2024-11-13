import json

import redis
from kazoo.client import KazooClient
from time import sleep

from singleton_decorator import singleton


@singleton
class TopicHolder:
    def __init__(self):
        self._topics = set()

    def is_changed(self, new):
        if not self._topics:
            self._topics = set(new)
            return None, None

        diff = set(new) - self._topics
        if diff:
            self._topics = set(new)
            return 'create', list(diff)[0]

        diff = self._topics - set(new)
        if diff:
            self._topics = set(new)
            return 'delete', list(diff)[0]

        return None, None


class KafkaAdminEventNotifier:
    _topic_holder = TopicHolder()

    def __init__(self, zk_hosts='127.0.0.1:2181', redis_url='redis://localhost:6379'):
        self.r = redis.Redis.from_url(redis_url)
        self.ps = self.r.pubsub()
        self.zk = KazooClient(hosts=zk_hosts)
        self.zk.start()
        self.redis_pub_topics = dict()

    def notify_add_delete_topic(self, notify_type, pub_topic):
        self.redis_pub_topics[notify_type] = pub_topic

        def _topic_handler(children):
            op, topic = KafkaAdminEventNotifier._topic_holder.is_changed(children)
            if op and op.lower() == 'create':
                self.r.publish(self.redis_pub_topics[op], json.dumps({'created': topic}))

            if op and op.lower() == 'delete':
                self.r.publish(self.redis_pub_topics[op], json.dumps({'deleted': topic}))

        self.zk.ChildrenWatch("/brokers/topics", _topic_handler)

    # def notify_config_change(self, monitor_topic, pub_topic):
    #     self.zk.DataWatch(f'/config/topics/{monitor_topic}', callback)


# @zk.ChildrenWatch("/brokers/topics")
# def watch_topics(children):
#     print("Topics are now: %s" % children)
#
#
# @zk.DataWatch("/config/topics/ddx-term")
# def watch_topic_config(data, stat, event):
#     print("stats: %s, data: %s, event : %s" % (stat, data, event))

if __name__ == '__main__':
    kn = KafkaAdminEventNotifier()
    kn.notify_add_delete_topic('create', 'topic_create')
    kn.notify_add_delete_topic('delete', 'topic_delete')
    while True:
        sleep(10)
