import events
import logging
import log
import traceback
from match import match_queue as mq

log.init()
logger=logging.getLogger("main")

while True:
    token=""
    try:
        match=mq.fetch()
        if not match:
            continue
        
        token=match.game_id
        # log.new_token_logger(token)
        events.push(events.Event(token=token, status_code=events.EventStatus.MATCH_STARTED.value,title='match started successfully!'))
        
        event_list = match.hold()
        logger.info(f"resulting events are:{len(event_list)}")
      
        events.push_all(event_list)
        mq.commit(match)
      
    except Exception as e:
        traceback.print_exc()
        logger.exception(f"an error accoured {e}")
    # finally:
        # log.remove_token_logger(token)