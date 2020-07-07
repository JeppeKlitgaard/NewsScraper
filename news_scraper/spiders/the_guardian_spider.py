"""
Holds Spiders related to `theguardian.com`.

The Guardian has 2 article layouts:
- Live Article (theguardian.com/$CATAGORY$/live/*)
- Regular article (theguardian.com/$CATAGORY$/$DATE$)

"""

import scrapy
import datetime
from dateutil.parser import parse as date_parse
import extruct

from scrapy.exceptions import CloseSpider

from enum import Enum

from news_scraper.utils import filter_empty
from news_scraper.items import Article
from news_scraper.base import ArticleType

from news_scheduler.utils import struct_time_to_datetime



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


class TheGuardianArticleSpider(scrapy.Spider):
    name = 'article-theguardian.co.uk'
    source_name = 'theguardian.co.uk'

    def __init__(self, link: str='', rss_item=None, *args, **kwargs):
        """Spider for crawling TheGuardian articles.

        Args:
            link (str): Useful for setting link through command line interface. Good for testing. 
            rss_item ([dict], optional): When instanciated by application this has a dictionary
                of the feedparsed RSS item. Defaults to None.
                Must be set if `link` is not set.

        Raises:
            ValueError: [description]
        """
        super().__init__(*args, **kwargs)

        if link:
            rss_item = {'link': link}

        if rss_item is None:
            raise ValueError("rss_item must be set.")

        self.rss_item = rss_item

        self.start_urls = [rss_item['link']]
    
    def _find_article_type(self, response):
        article_tag = response.xpath("//article[@role='main']")
        try:
            article_id = article_tag.attrib['id']
        except KeyError:
            import pdb; pdb.set_trace()

        if article_id == 'article':
            return ArticleType.REGULAR
        
        elif article_id == 'live-blog':
            return ArticleType.LIVE
        
        else:
            raise TypeError('Article not of right type. Something is wrong.')

    def _parse_author(self, microdata) -> str:
        """Returns the author(s) as a string."""

        author_list_or_dict = microdata[1]['properties']['author']
        
        if isinstance(author_list_or_dict, list):
            return ", ".join([x['properties']['name'] for x in author_list_or_dict])
        elif isinstance(author_list_or_dict, dict):
            return author_list_or_dict['properties']['name']
        else:
            raise ValueError("Something odd...")
    
    def _parse_summary(self, description) -> str:
        if isinstance(description, list):
            return ", ".join(description)
        elif isinstance(description, str):
            return description
        else:
            raise ValueError("Something odd...")


    def parse(self, response):
        # We're in luck!
        # The Guardian helpfully implements full microdata schema structure
        # No need to scrape, just extract using extruct.

        microdata = extruct.extract(response.text, syntaxes=['microdata'])['microdata']
        
        # Find Article Type
        # Sometimes microdata isn't sent for whatever reason. Just ignore these
        try:
            article_type_schema = microdata[1]['type']
        except IndexError:
            raise CloseSpider('The Guardian did not send valid microdata. Very sad :(. Skipping')

        article_type = None

        if article_type_schema == 'http://schema.org/LiveBlogPosting':
            article_type = ArticleType.LIVE_BLOG
        
        elif article_type_schema == 'http://schema.org/NewsArticle':
            article_type = ArticleType.REGULAR_ARTICLE
        
        elif article_type_schema == 'https://schema.org/ImageGallery':
            raise CloseSpider('Non applicable data type: ImageGallery.')

        else:
            raise NotImplementedError(f'Unsupported article schema: {article_type_schema}')
            
        # Handle articles
        if article_type == ArticleType.REGULAR_ARTICLE:
            _a = Article()

            _a['source'] = self.source_name
            _a['source_spider'] = self.name

            # Sometimes headline is missing. Fall back on rss_item
            try:
                _a['headline'] = microdata[1]['properties']['headline']
            except KeyError:
                _a['headline'] = self.rss_item['title']

            _a['summary'] = microdata[1]['properties']['description']
            _a['content'] = microdata[1]['properties']['articleBody']
            

            _a['url'] = self.rss_item['link']

            _a['crawl_datetime'] = datetime.datetime.now()
            _a['published_datetime'] = date_parse(microdata[1]['properties']['datePublished'])

            _a['language'] = 'en-GB'
            _a['author'] = self._parse_author(microdata)
            _a['article_type'] = article_type

            yield _a
        
        elif article_type == ArticleType.LIVE_BLOG:
            for entry in microdata[1]['properties']['liveBlogUpdate']:
                _a = Article()

                _a['source'] = self.source_name
                _a['source_spider'] = self.name

                _a['headline'] = entry['properties']['headline']
                _a['summary'] = microdata[1]['properties']['description']
                _a['content'] = entry['properties']['articleBody']

                _a['url'] = entry['properties']['url']

                _a['crawl_datetime'] = datetime.datetime.now()
                _a['published_datetime'] = date_parse(entry['properties']['datePublished'])

                _a['language'] = 'en-GB'
                _a['author'] = self._parse_author(microdata)
                _a['article_type'] = article_type

                yield _a
        
        else:
            raise NotImplementedError(f'Article type {article_type} not implemented. :(')
