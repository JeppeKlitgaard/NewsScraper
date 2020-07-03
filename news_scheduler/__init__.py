"""
Contains Kafka Producer that publishes sites to crawl to a Kafka topic in a schedule manner.
"""
from kafka import KafkaProducer
from kafka.errors import KafkaError

from news_scraper.utils import make_spider_dict, json_serializer

import time
import itertools
import logging

log = logging.getLogger(__name__)


class NewsScheduler(object):
    def __init__(self, bootstrap_servers, topic='crawl-queue', value_serializer=json_serializer):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

        self.spiders = [*make_spider_dict()]  # list of spider names


        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers, value_serializer=value_serializer)

    def request_crawl(self, site, timeout=10):
        log.info(f"Requesting crawl on site '{site}' via topic '{self.topic}'")
        return self.producer.send(self.topic, {'spider': site})

    def run_loop(self, interval):
        for spider in itertools.cycle(self.spiders):
            self.request_crawl(spider)
            time.sleep(interval)
