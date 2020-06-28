import scrapy
import datetime

from news_scraper.utils import filter_empty
from news_scraper.items import Article


class BBCNewsSpider(scrapy.Spider):
    name = 'bbc.com/news'

    start_urls = [
        'https://www.bbc.com/news'
    ]

    def parse(self, response):
        articles = response.css('a.gs-c-promo-heading')

        for article in articles:
            _a = Article()

            _a['headline'] = article.css('.gs-c-promo-heading__title::text').get()
            _a['url'] = response.urljoin(article.attrib['href'])
            _a['crawl_datetime'] = datetime.datetime.now()
            _a['source'] = self.name

            yield _a

        