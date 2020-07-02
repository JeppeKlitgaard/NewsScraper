"""
Contains Kafka Producer that publishes sites to crawl to a Kafka topic in a schedule manner.
"""
from kafka import KafkaProducer
from kafka.errors import KafkaError

import json

def _default_value_serializer(m):
    return json.dumps(m).encode('utf-8')


class NewsScheduler(object):
    def __init__(self, bootstrap_servers, topic='crawl-queue', value_serializer=_default_value_serializer):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic


        self.producer = KafkaProducer(self.bootstrap_servers, value_serializer=value_serializer)

    def request_crawl(self, site, timeout=10):
        return self.producer.send(self.topic, {'spider': site})




    


    def run_loop(interval):
        pass

def request_crawl(site):
    pass


def run_loop(interval, topic, kafka):
    pass