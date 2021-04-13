import enum
from kafka import KafkaConsumer, KafkaProducer
from os import getenv
import json
import logging
import time
import random

logger=logging.getLogger("kafka")

KAFKA_ENDPOINT = getenv('KAFKA_ENDPOINT')
KAFKA_TOPIC_CONSUMER_GROUP = getenv('KAFKA_TOPIC_CONSUMER_GROUP')
KAFKA_CONSUMER_HEART_BEAT_TIMEOUT = int(getenv('KAFKA_CONSUMER_HEART_BEAT_TIMEOUT'))
maximum_count_of_try_to_commit = 6


class Topics(enum.Enum):
    EVENTS = getenv('KAFKA_TOPIC_EVENTS')
    PLAY_GAME = getenv('KAFKA_TOPIC_PLAY_GAME')


consumer = KafkaConsumer(
    Topics.PLAY_GAME.value,
    bootstrap_servers=KAFKA_ENDPOINT,
    group_id=f"{KAFKA_TOPIC_CONSUMER_GROUP}",
    auto_offset_reset='latest',
    enable_auto_commit=True,
    session_timeout_ms=300000,
    max_poll_interval_ms=1200000,
)
logger.info(f"consumer {consumer} is built and connected")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_ENDPOINT,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)
logger.info(f"producer {consumer} is built and connected")


def get_consumer():
    return consumer


def commit(message):
    for t in range(1, maximum_count_of_try_to_commit + 1):
        try:
            consumer.commit()
            return
        except Exception as e:
            logger.warning(f'fail to commit message: {message}, We will try again, error: {e}')
            time.sleep(t ** 2)
    try:
        consumer.commit()
    except Exception as e:
        logger.exception(f'fail to commit message error: {e}, ignore commit message: {message}')


def push_event(event) -> bool:
    try:
        producer.send(topic=Topics.EVENTS.value, value=event)
        producer.flush()
        logger.info(f"event pushed successfully: {event}")
        return True
    except Exception as e:
        logger.exception(e)
        return False
