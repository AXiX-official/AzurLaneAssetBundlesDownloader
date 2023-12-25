import socket
import requests
import os
from typing import Tuple, Dict

import utils.file as file
import re


def send_tcp_request(server_ip: str, server_port: int, hex_message: str) -> bytes:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))

    message_bytes = bytes.fromhex(hex_message)

    s.sendall(message_bytes)
    data = s.recv(1024)
    s.close()

    return data


"""def download_file(url: str, dir_path: str, file_name: str) -> None:
    r = requests.get(url)
    content = r.content.decode("utf-8")
    file.mkfile(content, dir_path, file_name)"""

def download_file(url: str, dir_path: str, file_name: str) -> None:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        
        with open(os.path.join(dir_path, file_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def get_hashfile_url() -> Tuple[str, Dict[str, str]]:
    """
    从服务器获取最新的apk链接和hash文件链接并返回apk链接和hash文件链接字典
    :return: apk_version: str, hashfile_url: dict
    """
    raw_data = send_tcp_request('203.107.54.123', 80, '000a002a3000000837120130')
    data = raw_data.decode("utf-8", "ignore")
    apk_version = re.findall(r'(https?://\S+)\"', data)
    hashes = re.findall(r'\$(.*?)hash(.*?)\"', data)
    hashfile_url = {}
    for h in hashes:
        hashfile_url[h[0]] = f"${h[0]}hash{h[1]}"
    return apk_version[0], hashfile_url


def download_assetbundle(url: str, dir_path: str, file_name: str) -> None:
    r = requests.get(url)
    content = r.content
    os.makedirs(os.path.join(dir_path, os.path.dirname(file_name)), exist_ok=True)
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "wb") as f:
        f.write(content)
