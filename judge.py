from minio_cli import MinioClient
from event import Event
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


def judge(players, map_id, game_id) -> Event:
    pass
