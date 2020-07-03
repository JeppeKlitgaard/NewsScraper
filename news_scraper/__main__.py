import os

from .scraper import KafkaScraper

scraper = KafkaScraper(os.environ.get("NEWS_NET_KAFKA_HOSTS"))
scraper.run_loop()
