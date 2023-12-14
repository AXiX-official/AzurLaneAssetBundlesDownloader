import os

from utils.file import mkdir
from utils.network import get_hashfile_url, download_file
from utils.csvfile import merge_csv_with_conflicts

work_path = os.path.dirname(__file__)
cache_path = os.path.join(work_path, 'cache')
apk_csv_path = os.path.join(work_path, 'files', 'apk')
data_csv_path = os.path.join(work_path, 'files', 'data')
merged_csv_path = os.path.join(work_path, 'files', 'merged')
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


def merge_hashfile(hash_type, path=merged_csv_path):
    hashfile_name = f'{hash_csv_name[hash_type]}'
    apk_path = os.path.join(apk_csv_path, hashfile_name)
    data_path = os.path.join(data_csv_path, hashfile_name)
    mkdir(path)
    conflict = merge_csv_with_conflicts(apk_path, data_path, os.path.join(path, hashfile_name))
    if not conflict.empty:
        print(conflict)
