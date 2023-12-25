import os
import shutil
import json
import fnmatch
from loguru import logger
from typing import List
from datetime import datetime
import pandas as pd
from tqdm import tqdm
from time import sleep

from utils.file import mkdir
from utils.network import get_hashfile_url, download_file, download_assetbundle
from utils.csvfile import merge_csv_with_conflicts
from utils.logs import new_log
from typing import Generator

work_path = os.path.dirname(__file__)
cache_path = os.path.join(work_path, 'cache')
files_path = os.path.join(work_path, 'files')
history_path = os.path.join(work_path, 'history')
assetbundles_path = os.path.join(work_path, 'assetbundles')

version_json_path = os.path.join(work_path, 'files', 'version.json')

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


class Downloader:

    apk_version: str
    hashfile_url: dict
    to_download: List[str]
    version_file_flag: bool = False
    diff_list: List[int] = []

    def __init__(self) -> None:
        new_log()
        # 清空cache文件夹
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
        self.version_check()
        logger.info('Downloader init')

    def version_check(self) -> None:
        """
        检查本地的version.json文件，获取本地的apk_version和hashfile_url
        """
        if not os.path.exists(version_json_path):
            logger.warning('version.json not found')
            return
        self.version_file_flag = True
        with open(version_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.apk_version = data['apk_version']
            logger.info(f'local apk_version:{self.apk_version}')
            self.hashfile_url = data['hashfile_url']
            logger.info(f'local hashfile_url:{self.hashfile_url}')

    def remote_version_check(self, apk_check_flag=False) -> None:
        """
        检查远端的apk_version和hashfile_url
        如果本地的apk_version过期，则抛出异常
        如果本地的hashfile_url过期，则下载最新的hashfile_url
        """
        apk_version, hashfile_url = get_hashfile_url()
        logger.info(f'remote apk_version:{self.apk_version}')
        if self.apk_version != apk_version:
            logger.warning(f'local apk_version is out of date')
            if apk_check_flag:
                raise Exception('apk_version is out of date')
        logger.info(f'remote hashfile_url:{self.hashfile_url}')
        for key, value in hashfile_url.items():
            if self.hashfile_url[key] != value:
                logger.warning(f'local {key} hashfile_url is out of date')
                self.download_hashfile(hash_type=key, url=f'{andorid_hash_url}{value}')

    def download_hashfile(self, hash_type=None, url=None, path=cache_path) -> None:
        """
        下载单个hash文件
        """
        hashfile_name = hash_csv_name[hash_type]
        if not url:
            apk_version, hashfile_url = get_hashfile_url()
            url = f'{andorid_hash_url}{hashfile_url[hash_type]}'
        logger.info(f'remote hashfile:{hashfile_name} url:{url}')
        download_file(url, path, hashfile_name)
        logger.info(f'remote hashfile:{hashfile_name} saved to {path}')
    def download_remote_hashfiles(self, flag="files") -> Generator[str, None, None]:
        """
        下载远端的hash文件
        """
        if flag == "files":
            path = files_path
        elif flag == "cache":
            path = cache_path
        for key, value in hash_csv_name.items():
            self.download_hashfile(hash_type=key, path=path)
            yield f"{key} hashfile downloaded"

    def update_version_json(self) -> None:
        """
        更新本地的version.json文件
        """
        apk_version, hashfile_url = get_hashfile_url()
        data = {
            'apk_version': apk_version,
            'hashfile_url': hashfile_url
        }
        mkdir(files_path)
        with open(version_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f'version.json saved to {version_json_path}')

    def to_history(self, init_flag = False) -> None:
        """
        将files文件夹下的文件移动到history文件夹下
        """
        if init_flag:
            mkdir(history_path)
            path = os.path.join(history_path, '2020-01-01-00-00')
        else:
            date = datetime.now().strftime('%Y-%m-%d-%H-%M')
            path = os.path.join(history_path, date)
        mkdir(path)
        for file in os.listdir(files_path):
            shutil.copy(os.path.join(files_path, file), os.path.join(path, file))
        logger.info(f'files copied to history')

    def check(self) -> Generator[str, None, None]:
        logger.info('checking...')
        yield from self.get_difference()
        if not self.check_diff_files():
            logger.info('no difference found')
            yield 'warn:no difference found'
            return
        yield 'info:difference found'
        logger.info('former hash files deleted')
        #shutil.rmtree(files_path)
        for key, value in hash_csv_name.items():
            shutil.move(os.path.join(cache_path, value), os.path.join(files_path, value))
            logger.info(f'new hash files moved to files')
        yield 'info:new hash files moved to files'
        self.update_version_json()
        yield 'info:version.json updated'
        self.to_history()
        yield 'info:files copied to history'
        logger.info(f"{sum(self.diff_list)} files need to be updated")
        yield f"{sum(self.diff_list)} files need to be updated"

    def check_diff_files(self) -> bool:
        for file in os.listdir(cache_path):
            if fnmatch.fnmatch(file, '*_difference.csv'):
                return True
        return False

    def get_difference(self) -> Generator[str, None, None]:
        """
        获取本地和远端的hash文件的差异
        """
        yield from self.download_remote_hashfiles(flag='cache')
        yield 'info:remote hash files downloaded'
        for key, value in hash_csv_name.items():
            difference = merge_csv_with_conflicts(os.path.join(files_path, value), os.path.join(cache_path, value), flag='right')
            if not difference.empty:
                logger.info(f'{len(difference)} files need to be updated in {key}')
                self.diff_list.append(len(difference))
                difference.to_csv(os.path.join(cache_path, f'{key}_difference.csv'), index=False, header=False)
            else:
                self.diff_list.append(0)
            yield f"{key} comparison completed"

    def download_new_assetbundles(self, type_list: List[int]):
        date = datetime.now().strftime('%Y-%m-%d-%H-%M')
        path = os.path.join(assetbundles_path, date)
        os.makedirs(path, exist_ok=True)
        yield 'info:assetbundles folder created'
        for type_id in type_list:
            key = list(hash_csv_name.keys())[type_id]
            logger.info(f'downloading {key}...')
            if not os.path.exists(os.path.join(cache_path, f'{key}_difference.csv')):
                logger.info(f'{key} need not to be updated')
                continue
            df = pd.read_csv(os.path.join(cache_path, f'{key}_difference.csv'), header=None)
            for index, row in df.iterrows():
                file_name = row[0]
                url = f'{andorid_source_url}{row[2]}'
                logger.info(f'downloading {url}')
                download_assetbundle(url, path, file_name)
                logger.info(f'{file_name} saved to {path}')
                yield f'{file_name} saved'
