import enum
from kafka import KafkaConsumer, KafkaProducer
from os import getenv
import json
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s:%(message)s')
KAFKA_ENDPOINT = getenv('KAFKA_ENDPOINT')


class Topics(enum.Enum):
    EVENTS = getenv('KAFKA_TOPIC_EVENTS')
    PLAY_GAME = getenv('KAFKA_TOPIC_PLAY_GAME')


consumer = KafkaConsumer(
    Topics.PLAY_GAME.value,
    bootstrap_servers=KAFKA_ENDPOINT,
    group_id='judge-test',
    auto_offset_reset='latest',
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_ENDPOINT,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)


def get_consumer():
    return consumer


def push_event(event) -> bool:
    try:
        producer.send(topic=Topics.EVENTS.value, value=event)
        producer.flush()
        return True
    except Exception as e:
        logging.warning(e)
        return False
