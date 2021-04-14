from subprocess import STDOUT, check_output, TimeoutExpired,CalledProcessError
from minio_cli import MinioClient
from events import Event, EventStatus
import logging
import subprocess
import json
import os

logger=logging.getLogger("judge")



LOG_FILE_NAME = "log.json"
STATS_KEYNAME = "stats"
SERVER_OUTPUT = "Log/server/server.log"

server_timeout= int(os.getenv("MATCH_TIMEOUT"))
server_runcommand=["match", "--first-team='spawn 1'", "--second-team='spawn 2", "--read-map=map"]

def download_code(code_id, dest) -> bool:
    logger.info(f"start processing code [{code_id}]")

    zip_file = MinioClient.get_compiled_code(code_id)
    if zip_file is None:
        return False


    # unzip source binary
    with open('code.tgz', 'wb') as f:
        f.write(zip_file)
    cmd = subprocess.Popen(["tar", "-xvzf", "code.tgz"],
                           stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    cmd.communicate()
    if cmd.returncode != 0:
        return False
    logger.info(f"successfuly unziped binary [{code_id}]")


    # move binary to given dest
    cmd = subprocess.Popen(
        ["mv", "binary", dest], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    cmd.communicate()
    if cmd.returncode != 0:
        return False
    logger.info(f"successfuly moved binary [{code_id}] to [{dest}]")

    
    # give execute permission to new binary
    cmd = subprocess.Popen(
        ["chmod", "+x", dest], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    cmd.communicate()
    if cmd.returncode != 0:
        return False
    logger.info(f"[{dest}] is now executable")
    
    return True


def download_map(map_id, dest) -> bool:
    zip_file = MinioClient.get_map(map_id)
    if zip_file is None:
        return False

    with open(dest, 'wb') as f:
        f.write(zip_file)
    
    logger.info(f"map is stored to [{dest}] successfuly")
    return True
    


def __judge():

    try:
        logger.info("match started")
        output = check_output(server_runcommand, stderr=STDOUT, timeout=server_timeout)
        logger.info("match held successfully")
    except TimeoutExpired:
        logger.info("match timeout exiceded!")
        return -2
    except CalledProcessError:
        logger.info("match returned none zero exitcode!")
        return -1

    logger.debug(output)
    return 0


def judge(players, map_id, game_id) -> [Event]:
    resulting_events = []
    
    # downloading players code
    for index, player in enumerate(players):
        if not download_code(player, f"/etc/spawn/{index+1}"):
            resulting_events.append(Event(token=player, status_code=EventStatus.FILE_NOT_FOUND.value,
                         title='failed to fetch the compiled code!'))
            return resulting_events

    # download map
    if not download_map(map_id, "/usr/local/match/map"):
        resulting_events.append(Event(token=map_id, status_code=EventStatus.FILE_NOT_FOUND.value,
                     title='failed to fetch the map!'))
        return resulting_events

    # run match
    exit_code=__judge()
    if exit_code == -1:
        resulting_events.append(Event(token=game_id, status_code=EventStatus.MATCH_FAILED.value,
                                title='failed to hold the match'))
    elif exit_code == -2:
        resulting_events.append(Event(token=game_id, status_code=EventStatus.MATCH_TIMEOUT.value,
                                title='match timeout exceeded'))    
    elif exit_code == 0:
        stats = str(json.load(open(LOG_FILE_NAME))[STATS_KEYNAME])
        resulting_events.append(Event(token=game_id, status_code=EventStatus.MATCH_SUCCESS.value,
                 title='match finished successfully!', message_body=stats))
    

    # for player in players:
    #     with open(f'{player_name[player]}.log', 'rb') as file:
    #         if not MinioClient.upload_logs(path=game_id, file=file, file_name=player):
    #             return Event(token=player, status_code=EventStatus.UPLOAD_FAILED.value,
    #                          title='failed to upload the player log!')

    # upload game log
    try:
        with open(LOG_FILE_NAME, 'rb') as file:
            if not MinioClient.upload_logs(path=game_id, file=file, file_name=game_id):
                resulting_events.append(Event(token=game_id, status_code=EventStatus.UPLOAD_FAILED.value,
                            title='failed to upload the game log!'))
    except:
        logger.warning(f"file {LOG_FILE_NAME} didnt exist!")
   
    # upload server log
    with open(SERVER_OUTPUT, 'rb') as file:
        if not MinioClient.upload_logs(path=game_id, file=file, file_name=f'{game_id}.out'):
            resulting_events.append(Event(token=game_id, status_code=EventStatus.UPLOAD_FAILED.value,
                        title='failed to upload the game server output!'))

    return resulting_events
