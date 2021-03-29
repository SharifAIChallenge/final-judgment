import enum
from judge import judge
import kafka_cli as kcli
import json
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s:%(message)s')


for message in kcli.get_consumer():
    try:
        command = json.loads(message.value.decode("utf-8"))
        logging.info(f"got new record:{command}")
        event = judge(players=command['player_ids'], game_id=command['game_id'], map_id=command['map_id'])
        logging.info(f"resulting event is:{event}")
        kcli.push_event(event.__dict__)
    except Exception as e:
        logging.warning(e)
