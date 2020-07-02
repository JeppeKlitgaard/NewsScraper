# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils.serialize import ScrapyJSONEncoder

from kafka import KafkaProducer


class NewsScraperPipeline:
    def process_item(self, item, spider):
        return item


class DeduplicationPipeline:
    def __init__(self):
        self.urls_seen = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter['url'] in self.urls_seen:
            raise DropItem(f'Duplicate item found: {item}')

        else:
            self.urls_seen.add(adapter['url'])
            return item

class KafkaPipeline:
    # https://github.com/dfdeshom/scrapy-kafka/blob/master/scrapy_kafka/pipelines.py
    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

        self.encoder = ScrapyJSONEncoder()
    
    def process_item(self, item, spider):
        item = dict(item)
        item['spider'] = spider.name
        msg = self.encoder.encode(item)
        spider.log(msg)
        self.producer.send(self.topic, msg.encode('utf-8'))
        spider.log("Sent to kafka.")
    
    @classmethod
    def from_settings(cls, settings):
        k_hosts = settings.get('KAFKA_HOSTS', ['localhost:9092'])
        topic = settings.get('KAFKA_ITEM_PIPELINE_TOPIC', 'scrapy_kafka_item')

        prod = KafkaProducer(bootstrap_servers=k_hosts)
        return cls(prod, topic)
