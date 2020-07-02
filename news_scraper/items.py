# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Article(scrapy.Item):
    headline = scrapy.Field()
    url = scrapy.Field()
    crawl_datetime = scrapy.Field()
    source = scrapy.Field()

