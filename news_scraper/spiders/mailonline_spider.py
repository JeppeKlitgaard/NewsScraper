import scrapy
import datetime

from news_scraper.utils import filter_empty
from news_scraper.items import Article


class MailOnlineSpider(scrapy.Spider):
    name = 'dailymail.co.uk'

    # dailymail does not behave nicely, so neither will we.
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
    }

    # Text-based site easier to parse
    start_urls = [
        'https://www.dailymail.co.uk/textbased/channel-1/index.html'
    ]

    def parse(self, response):
        articles = response.xpath('//div[a[h3]]')

        for article in articles:
            _a = Article()

            _a['headline'] = article.xpath('a/h3/text()').get()
            _a['url'] = article.xpath('a/@href').get()
            _a['crawl_datetime'] = datetime.datetime.now()
            _a['source'] = self.name

            yield _a

        