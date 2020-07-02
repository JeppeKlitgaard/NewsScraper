"""
Contains Kafka Producer that publishes sites to crawl to a Kafka topic in a schedule manner.
"""
from kafka import KafkaProducer
from kafka.errors import KafkaError

from .utils import list_spiders_available, _default_value_serializer

import time
import itertools


class NewsScheduler(object):
    def __init__(self, bootstrap_servers, topic='crawl-queue', value_serializer=_default_value_serializer):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

        self.spiders = list_spiders_available()


        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers, value_serializer=value_serializer)

    def request_crawl(self, site, timeout=10):
        return self.producer.send(self.topic, {'spider': site})

    def run_loop(self, interval):
        for spider in itertools.cycle(self.spiders):
            self.request_crawl(spider)
            time.sleep(interval)
