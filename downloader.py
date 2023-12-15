import os
import shutil
from loguru import logger

from utils.file import mkdir
from utils.network import get_hashfile_url, download_file
from utils.csvfile import merge_csv_with_conflicts

work_path = os.path.dirname(__file__)
cache_path = os.path.join(work_path, 'cache')
apk_csv_path = os.path.join(work_path, 'files', 'apk')
data_csv_path = os.path.join(work_path, 'files', 'data')
merged_csv_path = os.path.join(work_path, 'files', 'merged')
conflicts_csv_path = os.path.join(work_path, 'files', 'conflicts')
andorid_hash_url = "https://line3-patch-blhx.bilibiligame.net/android/hash/"
andorid_source_url = "https://line3-patch-blhx.bilibiligame.net/android/resource/"
hash_csv_name = {
    'az': 'hashes.csv',
    'cv': 'hashes-cv.csv',
    'l2d': 'hashes-live2d.csv',
    'pic': 'hashes-pic.csv',
    'bgm': 'hashes-bgm.csv',
    'painting': 'hashes-painting.csv',
    'manga': 'hashes-manga.csv',
    'cipher': 'hashes-cipher.csv'
}


def download_hashfile(hash_type, path=cache_path):
    hashfile_url = get_hashfile_url()
    hashfile_name = f'{hash_csv_name[hash_type]}'
    url = f'{andorid_hash_url}{hashfile_url[hash_type]}'
    download_file(url, path, hashfile_name)


def merge_hashfile(hash_type, path=merged_csv_path, overwrite=False):
    hashfile_name = f'{hash_csv_name[hash_type]}'
    apk_path = os.path.join(apk_csv_path, hashfile_name)
    data_path = os.path.join(data_csv_path, hashfile_name)
    merged_path = os.path.join(path, hashfile_name)

    if os.path.exists(merged_path) and not overwrite:
        logger.info(f'{hashfile_name} already exists')
        return

    mkdir(path)

    if not os.path.exists(apk_path):
        shutil.copyfile(data_path, merged_path)
        return
    if not os.path.exists(data_path):
        shutil.copyfile(apk_path, merged_path)
        return

    conflict = merge_csv_with_conflicts(apk_path, data_path, merged_path)
    if not conflict.empty:
        conflict_path = os.path.join(conflicts_csv_path, hashfile_name)
        mkdir(conflicts_csv_path)
        logger.warning(f'conflict found in {hashfile_name}')
        conflict.to_csv(conflict_path, index=False)


def merge_local():
    """
    合并本地的csv文件，即files/apk和files/data中的文件
    默认不覆盖已有文件
    """
    for key, value in hash_csv_name.items():
        merge_hashfile(key)