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
    source = scrapy.Field()
    source_spider = scrapy.Field()

    headline = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()

    url = scrapy.Field()
    
    crawl_datetime = scrapy.Field()
    published_datetime = scrapy.Field()

    language = scrapy.Field()
    author = scrapy.Field()
    article_type = scrapy.Field()  # * See: base.ArticleType
    
