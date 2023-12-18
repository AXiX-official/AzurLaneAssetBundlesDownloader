import os
from loguru import logger


def mkdir(path):
    if os.path.exists(path):
        return
    os.mkdir(path)
    logger.info(f'mkdir: {path}')


def mkfile(content, dir_path, file_name):
    os.makedirs(os.path.join(dir_path, os.path.dirname(file_name)), exist_ok=True)
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "w", newline='\n') as f:
        f.write(content)
