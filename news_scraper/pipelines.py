# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


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
