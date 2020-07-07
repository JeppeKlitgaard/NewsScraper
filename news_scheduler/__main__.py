from . import NewsScheduler
from . import settings

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

scheduler = NewsScheduler(os.environ["NEWS_NET_KAFKA_HOSTS"], settings.RSS_FEEDS)

scheduler.run_loop(settings.FEED_INTERVAL)
