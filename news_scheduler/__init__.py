"""
Contains Kafka Producer that publishes sites to crawl to a Kafka topic in a schedule manner.
"""
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

from news_scraper.utils import make_spider_dict, json_serializer

from .utils import TimeCheckpoint, struct_time_to_datetime

import time
import itertools
import logging
import feedparser
from uuid import uuid4

log = logging.getLogger(__name__)


def _json_serializer_wrapper(obj, ctx):
    return json_serializer(obj)

class NewsScheduler(object):
    def __init__(self, bootstrap_servers, rss_feeds, topic='crawl-queue',
                 time_checkpoint_fn='timecheckpoint.txt'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.time_checkpoint = TimeCheckpoint(fn=time_checkpoint_fn)

        self.feeds = rss_feeds

        producer_conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'key.serializer': StringSerializer('utf_8'),
            'value.serializer': _json_serializer_wrapper
        }
        self.producer = SerializingProducer(producer_conf)

    def process_feed(self, feed_url, spider, flush=False):
        log.info(f"Processing feed '{feed_url}' via topic '{self.topic}'.")
        rss_feed = feedparser.parse(feed_url)

        for item in rss_feed.entries:
            item['spider'] = spider
            item_publish_time = struct_time_to_datetime(item.published_parsed)

            if item_publish_time > self.time_checkpoint.checkpoint:
                log.info(f"New item: {item['title']}")

                self.producer.produce(topic=self.topic, key=str(uuid4()), value=dict(item))
        
        self.time_checkpoint.checkpoint = struct_time_to_datetime(rss_feed.feed.published_parsed)
        
        if flush:
            self.producer.flush()


    def run_loop(self, interval):
        for feed, spider in itertools.cycle(self.feeds.items()):
            self.process_feed(feed, spider)
            time.sleep(interval)
