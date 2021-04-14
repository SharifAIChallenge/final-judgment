from confluent_kafka import Producer
import logging
from os import getenv

logger=logging.getLogger("events")

KAFKA_ENDPOINT = getenv('KAFKA_ENDPOINT')
KAFKA_TOPIC_EVENTS = getenv('KAFKA_TOPIC_EVENTS')


p = Producer({'bootstrap.servers': KAFKA_ENDPOINT})


def __on_deliver(err,msg):
    """ Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush(). """
    if err is not None:
        logger.warn(f"failed to push event : [{msg}]")
        logger.warn(f"failed with error : [{err}]")        
    else:
        print(f"event pushed successfully")


def __push_data(data):
    logger.info(f"pushing event:[{data}]")
    # Trigger any available delivery report callbacks from previous produce() calls
    p.poll(0)

    # Asynchronously produce a message, the delivery report callback
    # will be triggered from poll() above, or flush() below, when the message has
    # been successfully delivered or failed permanently.
    p.produce(KAFKA_TOPIC_EVENTS, data.encode('utf-8'), callback=__on_deliver)

def push(event):
    __push_data(event.__dict__)
    p.flush()

def push_all(events):
    [__push_data(event) for event in events]
    p.flush()


