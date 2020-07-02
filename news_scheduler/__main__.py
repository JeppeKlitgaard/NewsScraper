from . import NewsScheduler

import os

scheduler = NewsScheduler(os.environ["NEWS_NET_KAFKA_HOSTS"])

scheduler.run_loop(1)
