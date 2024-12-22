from kafka import KafkaAdminClient

# Default (dummy)
LOCAL_BOOTSTRAP_SERVERS = 'localhost:9092'


class KafkaConnect:
    def __init__(self, **kwargs):
        if kwargs.get('bootstrap_servers') is None:
            kwargs['bootstrap_servers'] = LOCAL_BOOTSTRAP_SERVERS

        self.admin_client = KafkaAdminClient(**kwargs)

    def list_topics(self):
        # Any business logic goes here
        return self.admin_client.list_topics()

    def describe_topics(self, topics=None):
        # Any business logic goes here
        return self.admin_client.describe_topics(topics)

    def list_consumer_groups(self):
        return self.admin_client.list_consumer_groups()

    def describe_consumer_groups(self, group_id):
        return self.admin_client.describe_consumer_groups(group_id)
