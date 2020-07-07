from enum import Enum


class ArticleType(str, Enum):
    LIVE_BLOG = 'LiveBlog'
    REGULAR_ARTICLE = 'Article'