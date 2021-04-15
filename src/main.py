from judge import judge
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

        command = json.loads(message.value().decode('utf-8'))
        logger.info(f"command is:{command}")
        
        token=command['game_id']
        players=command['player_ids']
        map_id=command['map_id']
        
        log.new_token_logger(token)
        logger.info(f"got new record:{command}")
        
        events.push(events.Event(token=token, status_code=events.EventStatus.MATCH_STARTED.value,title='match started successfully!'))
        # event_list = judge(players=players, game_id=token, map_id=map_id)
        # logger.info(f"resulting events are:{len(event_list)}")
        import time
        time.sleep(10)
        exit(-2)
        events.push_all(event_list)
        mq.commit(message)
      
    except Exception as e:
        traceback.print_exc()
        logger.exception(f"an error accoured {e}")
    finally:
        log.remove_token_logger(token)