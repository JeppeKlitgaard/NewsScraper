import os

# from .scraper import KafkaScraper

# scraper = KafkaScraper(os.environ.get("NEWS_NET_KAFKA_HOSTS"))
# scraper.run_loop()

import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils import project

from .utils import make_spider_dict

import json
import sys
import logging

from twisted.internet import reactor, defer, task

from afkak.client import KafkaClient
from afkak.consumer import OFFSET_LATEST, OFFSET_EARLIEST, OFFSET_COMMITTED, Consumer
from afkak.common import OperationInProgress

log = logging.getLogger('consumer_example')


@defer.inlineCallbacks
def ready_client(reactor, netloc, topic):
    """
    Connect to a Kafka broker and wait for the named topic to exist.
    This assumes that ``auto.create.topics.enable`` is set in the broker
    configuration.
    :raises: `KafkaUnavailableError` if unable to connect.
    """
    client = KafkaClient(netloc, reactor=reactor)

    e = True
    while e:
        yield client.load_metadata_for_topics(topic)
        e = client.metadata_error_for_topic(topic)
        if e:
            log.info("Error getting metadata for topic %r: %s (will retry)",
                     topic, e)

    defer.returnValue(client)


@defer.inlineCallbacks
def consume(reactor, hosts='kafka-server1:9092'):
    topic = 'crawl-queue'
    client = yield ready_client(reactor, hosts, topic)
    partitions = client.topic_partitions[topic]
    print(f'PARTITIONS: {partitions}')

    settings = project.get_project_settings()

    runner = CrawlerRunner(settings=settings)
    spiders = make_spider_dict(settings=settings)

    def process(consumer, message_list):
        """
        This function is called for every batch of messages received from
        Kafka. It may return a Deferred, but this implementation just logs the
        messages received.
        """
        deferreds = []
        for m in message_list:
            log.debug("Got message %r", m)
            mo = json.loads(m.message.value)
            log.info(mo)
            log.info(consumers)

            try:
                spider_obj = spiders[mo['spider']]
            except KeyError as e:
                log.error(f"Unable to find spider '{mo['spider']}'. Ignoring error {e}")
                continue

            d = runner.crawl(spider_obj, rss_item=mo)
            deferreds.append(d)


        def consumer_commit(r):
            success = all(list(zip(*r))[0])

            if success:
                log.info("Committing to consumer!")
                d = consumer.commit()
                d.addCallback(lambda _: log.info("Succesfully commited."))
            
            else:
                log.error("A consumer failed. Not committing...")

    
        dl = defer.DeferredList(deferreds)
        dl.addBoth(consumer_commit)

        consumer.shutdown()

    consumers = [Consumer(client, topic, partition, process, consumer_group='scraper-group',
                          auto_offset_reset=OFFSET_EARLIEST, buffer_size=1024)
                 for partition in partitions]
    


    def cb_closed(result):
        """
        Called when a consumer cleanly stops.
        """
        log.info("Consumer stopped")

    def eb_failed(failure):
        """
        Called when a consumer fails due to an uncaught exception in the
        processing callback or a network error on shutdown. In this case we
        simply log the error.
        """
        log.error("Consumer failed: %s", failure)
    
    def start_consumer(consumer):
        log.info("Consumer started.")
        d = consumer.start(OFFSET_COMMITTED)
        d.addCallbacks(cb_closed, eb_failed)
        
        return d


    def stop_consumers():
        log.info("\n")
        log.info("Time is up, stopping consumers...")
        d = defer.gatherResults([c.shutdown() for c in consumers])
        d.addCallback(lambda result: client.close())
        return d


    yield defer.gatherResults(
        [start_consumer(c) for c in consumers]
        #[task.deferLater(reactor, 10.0, stop_consumers)]
        
    )

scrapy_logger = logging.getLogger("scrapy")
scrapy_logger.setLevel(logging.ERROR)

kafka_logger = logging.getLogger("kafka")
kafka_logger.setLevel(logging.ERROR)

logging.basicConfig(
    format='%(name)s %(levelname)s %(message)s',
    level=logging.INFO,
)

consume(reactor)
reactor.run()
#task.react(consume, sys.argv[1:])
log.info("All Done!")


