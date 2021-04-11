import enum
from judge import judge
import kafka_cli as kcli
import json
from event import Event, EventStatus
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s:%(message)s')

for message in kcli.get_consumer():
    try:
        command = json.loads(message.value.decode("utf-8"))
        logging.warning(f"got new record:{command}")
        kcli.push_event(Event(token=command['game_id'], status_code=EventStatus.MATCH_STARTED.value,
                              title='match started successfully!').__dict__)
        events = judge(players=command['player_ids'], game_id=command['game_id'], map_id=command['map_id'])
        logging.warning(f"resulting events are:{len(events)}")

        [kcli.push_event(event.__dict__) for event in events]

        kcli.commit(command)
    except Exception as e:
        logging.warning(e)
