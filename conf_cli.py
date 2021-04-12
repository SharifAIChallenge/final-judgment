from confluent_kafka import Consumer
from os import getenv
import logging
import enum

logger=logging.getLogger("kafka")

KAFKA_ENDPOINT = getenv('KAFKA_ENDPOINT')
KAFKA_TOPIC_CONSUMER_GROUP = getenv('KAFKA_TOPIC_CONSUMER_GROUP')
KAFKA_CONSUMER_HEART_BEAT_TIMEOUT = int(getenv('KAFKA_CONSUMER_HEART_BEAT_TIMEOUT'))
maximum_count_of_try_to_commit = 6


class Topics(enum.Enum):
    EVENTS = getenv('KAFKA_TOPIC_EVENTS')
    PLAY_GAME = getenv('KAFKA_TOPIC_PLAY_GAME')



c = Consumer({
    'bootstrap.servers': KAFKA_ENDPOINT,
    'group.id': KAFKA_TOPIC_CONSUMER_GROUP,
    'auto.offset.reset': 'latest',
    'enable.auto.commit': True,
    'session.timeout.ms': 10*1000,      #10 seconds
    'max.poll.interval.ms': 30*60*1000,  #30 minutes
    'heartbeat.interval.ms': 1*1000     #1 seconds
})

c.subscribe([Topics.PLAY_GAME.value])


def get_message():
    
    msg = c.poll()

    if msg is None:
        return None
    if msg.error():
        logger.error(f"error acurred while fetching new message: {msg.error()}")
        return None
    return msg.value().decode('utf-8')

def close():
    c.close()