import enum
from judge import judge
import kafka_cli as kcli
import json
from event import Event, EventStatus
import logging
import log
import traceback
import conf_cli as ccli

log.init()
logger=logging.getLogger("main")

while True:
    try:
        message=ccli.fetch()
        if not message:
            continue

        logger.info(f"message is: {message}")
        command = json.loads(message.value().decode('utf-8'))
        logger.info(f"command is:{command}")
        token=command['game_id']
        
        log.new_token_logger(command['game_id'])
        logger.info(f"got new record:{command}")
        
        kcli.push_event(Event(token=command['game_id'], status_code=EventStatus.MATCH_STARTED.value,
                              title='match started successfully!').__dict__)
        events = judge(players=command['player_ids'], game_id=command['game_id'], map_id=command['map_id'])
        
        logger.info(f"resulting events are:{len(events)}")
        [logger.info(event.title) for event in events]

        [kcli.push_event(event.__dict__) for event in events]
        
        ccli.commit(message)
        logger.info("match was commited successfully!")

    except Exception as e:
        traceback.print_exc()
        logger.exception(f"an error accoured {e}")
    finally:
        log.remove_token_logger(token)