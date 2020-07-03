from . import NewsScheduler

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

scheduler = NewsScheduler(os.environ["NEWS_NET_KAFKA_HOSTS"])

scheduler.run_loop(3)
