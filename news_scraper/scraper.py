import os

from kafka import KafkaConsumer, KafkaProducer

from twisted.internet import reactor

from scrapy import spiderloader
from scrapy.utils import project
from scrapy.crawler import CrawlerRunner

from .utils import make_spider_dict, json_deserializer, json_serializer


class KafkaScraper(object):
    def __init__(self, bootstrap_servers, consume_topic='crawl-queue', produce_topic=None, value_serializer=json_serializer, value_deserializer=json_deserializer):
        self.scrapy_settings = project.get_project_settings()

        if produce_topic is None:
            produce_topic = self.scrapy_settings.get('KAFKA_ITEM_PIPELINE_TOPIC')
        self.produce_topic = produce_topic

        self.bootstrap_servers = bootstrap_servers
        self.consume_topic = consume_topic

        self.spiders = make_spider_dict()

        self.crawler_runner = CrawlerRunner(self.scrapy_settings)

        self.consumer = KafkaConsumer(self.consume_topic,
                                      bootstrap_servers=self.bootstrap_servers,
                                      auto_offset_reset='earliest',
                                      enable_auto_commit=True,
                                      group_id='scraper-group',
                                      value_deserializer=value_deserializer,
                                      )

        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                      value_serializer=value_serializer
                                      )

    def run_loop(self):
        for message in self.consumer:
            try:
                spider = self.spiders[message.value['spider']]
            except KeyError as e:
                print(f"ERROR: Got KeyError: {e}")
                continue
            
            print(f"Started crawling {spider}")
            import time
            time.sleep(3)
            deferred = self.crawler_runner.crawl(spider)
            print(deferred)
            deferred.addCallback(lambda x: print(x))
            deferred.addErrback(lambda x: print(x))
            reactor.run()
