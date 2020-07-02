import scrapy
import datetime

from news_scraper.utils import filter_empty
from news_scraper.items import Article


class TheGuardianSpider(scrapy.Spider):
    name = 'theguardian.co.uk'

    start_urls = [
        'https://www.theguardian.com/'
    ]

    def parse(self, response):
        sel_articles = response.css('a[data-link-name="article"]')

        for article in sel_articles:
            _a = Article()
            article_url = article.attrib['href']
            article_headline_bits = filter_empty(article.css('::text').getall())

            if len(article_headline_bits) == 1:
                article_headline = article_headline_bits[0]
            
            elif len(article_headline_bits) == 2:
                article_headline = f'{article_headline_bits[0]}: {article_headline_bits[1]}'

            else:
                raise ValueError('Got unexpected number of headline bits. Please investigate.')

            _a['headline'] = article_headline
            _a['url'] = article_url
            _a['crawl_datetime'] = datetime.datetime.now()
            _a['source'] = self.name

            yield _a
