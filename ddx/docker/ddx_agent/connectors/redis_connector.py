import json

import redis

from core.app_urls import ANOMALIES

CHANNELS = ['schema_violations']
LOCAL_REDIS = 'redis://localhost:6379'


class RedisConnect:
    def __init__(self, ws_client, ws_url=ANOMALIES, redis_url=LOCAL_REDIS):
        self.r = redis.Redis.from_url(redis_url)
        self.ws_client = ws_client
        self.ws_url = ws_url

    def subscribe_channel(self):
        ps = self.r.pubsub()
        ps.subscribe(CHANNELS)
        for raw_message in ps.listen():
            if raw_message["type"] != "message":
                continue

            message = json.loads(raw_message["data"])
            self.process_msg(message)

    def process_msg(self, msg):
        anomalies = {'type': 'anomalies', 'payload': msg}
        self.ws_client.send(self.ws_url, body=json.dumps(anomalies))

