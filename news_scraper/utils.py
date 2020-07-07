"""
Contains utility functions.
"""
from scrapy import spiderloader
from scrapy.utils import project

import json

def normalise_space(s):
    return " ".join(s.split())


def filter_empty(lst):
    return [x.strip() for x in lst if x.strip()]

class JSONEncoder(json.JSONEncoder):
    # https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    def default(self, obj):
        # to_json method
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        

        return json.JSONEncoder.default(self, obj)


def json_serializer(m):
    return json.dumps(m, cls=JSONEncoder).encode('utf-8')


def json_deserializer(x):
    return json.loads(x.decode('utf-8'))


def make_spider_dict(settings=None):
    # https://stackoverflow.com/questions/46871133/get-all-spiders-class-name-in-scrapy/46871206
    if settings is None:
        settings = project.get_project_settings()
    
    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    # classes = [spider_loader.load(name) for name in spiders]
    spider_dict = {name: spider_loader.load(name) for name in spiders}

    return spider_dict