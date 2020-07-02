"""
Contains utility functions for News Scheduler.
"""
import json

from typing import List

def list_spiders_available() -> List[str]:
    from scrapy import spiderloader
    from scrapy.utils import project

    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()

    return spiders


def _default_value_serializer(m):
    return json.dumps(m).encode('utf-8')
