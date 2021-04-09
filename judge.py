from subprocess import STDOUT, check_output, TimeoutExpired,CalledProcessError
from minio_cli import MinioClient
from event import Event, EventStatus
import logging
import subprocess
import json


LOG_FILE_NAME = "log.json"
STATS_KEYNAME = "stats"
SERVER_OUTPUT = "Log/server/server.log"

server_timeout= 5*60
server_runcommand=["server", "--first-team=./player1", "--second-team=./player2", "--read-map=map"]
     

logging.basicConfig(filename='app.log', filemode='w',
                    format='%(asctime)s - %(levelname)s:%(message)s')


def download_code(code_id, dest) -> bool:
    zip_file = MinioClient.get_compiled_code(code_id)
    if zip_file is None:
        return False

    with open('code.tgz', 'wb') as f:
        f.write(zip_file)

    cmd = subprocess.Popen(["tar", "-xvzf", "code.tgz"],
                           stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    cmd.communicate()
    if cmd.returncode != 0:
        return False

    cmd = subprocess.Popen(
        ["mv", "binary", dest], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    cmd.communicate()
    if cmd.returncode != 0:
        return False

    cmd = subprocess.Popen(
        ["chmod", "+x", dest], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    cmd.communicate()
    if cmd.returncode != 0:
        return False

    return True


def download_map(map_id, dest) -> bool:
    zip_file = MinioClient.get_map(map_id)
    if zip_file is None:
        return False

    with open(dest, 'wb') as f:
        f.write(zip_file)
    return True


def __judge():

    try:
        output = check_output(server_runcommand, stderr=STDOUT, timeout=server_runcommand)
    except TimeoutExpired:
        return -1
    except CalledProcessError:
        return -1


    # cmd = subprocess.Popen(["server", "--first-team=./player1", "--second-team=./player2", "--read-map=map"],
    #                        stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    # output = cmd.stdout.read()
    # error = cmd.stderr.read()
    logging.warning(output)
    # logging.warning(error)
    # cmd.communicate()
    # return cmd.returncode
    return 0


def judge(players, map_id, game_id) -> [Event]:
    resulting_events = []
    player_name = {}
    for index, player in enumerate(players):
        player_name[player] = f"player{index + 1}"
        if not download_code(player, player_name[player]):
            return Event(token=player, status_code=EventStatus.FILE_NOT_FOUND.value,
                         title='failed to fetch the compiled code!')

    if not download_map(map_id, "map"):
        return Event(token=map_id, status_code=EventStatus.FILE_NOT_FOUND.value,
                     title='failed to fetch the map!')

    if __judge() != 0:
        resulting_events.append(Event(token=game_id, status_code=EventStatus.MATCH_FAILED.value,
                                title='failed to hold the match'))
    else:
        stats = str(json.load(open(LOG_FILE_NAME))[STATS_KEYNAME])
        resulting_events.append(Event(token=game_id, status_code=EventStatus.MATCH_SUCCESS.value,
                 title='match finished successfully!', message_body=stats))
    

    # for player in players:
    #     with open(f'{player_name[player]}.log', 'rb') as file:
    #         if not MinioClient.upload_logs(path=game_id, file=file, file_name=player):
    #             return Event(token=player, status_code=EventStatus.UPLOAD_FAILED.value,
    #                          title='failed to upload the player log!')

    with open(LOG_FILE_NAME, 'rb') as file:
        if not MinioClient.upload_logs(path=game_id, file=file, file_name=game_id):
            resulting_events.append(Event(token=game_id, status_code=EventStatus.UPLOAD_FAILED.value,
                         title='failed to upload the game log!'))

    with open(SERVER_OUTPUT, 'rb') as file:
        if not MinioClient.upload_logs(path=game_id, file=file, file_name=f'{game_id}.out'):
            resulting_events.append(Event(token=game_id, status_code=EventStatus.UPLOAD_FAILED.value,
                         title='failed to upload the game server output!'))

    
    return resulting_events
