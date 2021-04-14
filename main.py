from judge import judge
# import kafka_cli as kcli
import json
import events
import logging
import log
import traceback
import match_queue as mq

log.init()
logger=logging.getLogger("main")

while True:
    token=""
    try:
        message=mq.fetch()
        if not message:
            continue

        logger.info(f"message is: {message}")
        command = json.loads(message.value().decode('utf-8'))
        logger.info(f"command is:{command}")
        token=command['game_id']
        
        log.new_token_logger(command['game_id'])
        logger.info(f"got new record:{command}")
        
        events.push(events.Event(token=command['game_id'], status_code=events.EventStatus.MATCH_STARTED.value,
                              title='match started successfully!'))
        event_list = judge(players=command['player_ids'], game_id=command['game_id'], map_id=command['map_id'])
        logger.info(f"resulting events are:{len(event_list)}")
      
        events.push_all(event_list)
        mq.commit(message)
      
    except Exception as e:
        traceback.print_exc()
        logger.exception(f"an error accoured {e}")
    finally:
        log.remove_token_logger(token)