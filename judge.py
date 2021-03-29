from minio_cli import MinioClient
from event import Event, EventStatus
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s:%(message)s')


def download_code(code_id, dest) -> bool:
    zip_file = MinioClient.get_compiled_code(code_id)
    if zip_file is None:
        return False

    with open(dest, 'wb') as f:
        f.write(zip_file)

    return True


def download_map(map_id, dest) -> bool:
    zip_file = MinioClient.get_map(map_id)
    if zip_file is None:
        return False

    with open(dest, 'wb') as f:
        f.write(zip_file)

    return True


def __judge() -> bool:
    pass


def judge(players, map_id, game_id) -> Event:
    player_name = {}
    for index, player in enumerate(players):
        player_name[player] = f"player{index + 1}"
        if not download_code(player, player_name[player]):
            return Event(token_id=player, status_code=EventStatus.FILE_NOT_FOUND.value,
                         title='failed to fetch the compiled code!')

    if not download_map(map_id, "map"):
        return Event(token_id=map_id, status_code=EventStatus.FILE_NOT_FOUND.value,
                     title='failed to fetch the map!')

    if not __judge():
        pass  # todo Arshia

    for player in players:
        with open(f'{player_name[player]}.log', 'rb') as file:
            if not MinioClient.upload_logs(path=game_id, file=file, file_name=player):
                return Event(token_id=player, status_code=EventStatus.UPLOAD_FAILED.value,
                             title='failed to upload the player log!')

    with open(f'game.log', 'rb') as file:
        if not MinioClient.upload_logs(path=game_id, file=file, file_name=game_id):
            return Event(token_id=game_id, status_code=EventStatus.UPLOAD_FAILED.value,
                         title='failed to upload the game log!')

    return Event(token_id=game_id, status_code=EventStatus.COMPILE_SUCCESS.value,
                 title='game successfully registered!')
