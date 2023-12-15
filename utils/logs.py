from loguru import logger
from utils.file import mkdir
import os


work_path = os.path.dirname(__file__)
work_path = os.path.dirname(work_path)
log_dir = os.path.join(work_path, 'logs')


def new_log(info='new log', logdir=log_dir):
    mkdir(logdir)
    logger.add(os.path.join(logdir, "{time}.log"))
    logger.info(info)
    logger.info(f'logdir: {logdir}')

