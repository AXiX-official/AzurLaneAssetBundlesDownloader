import socket
import requests
import utils.file as file
import re


def send_tcp_request(server_ip, server_port, hex_message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))

    message_bytes = bytes.fromhex(hex_message)

    s.sendall(message_bytes)
    data = s.recv(1024)
    s.close()

    return data


def download_file(url, dir_path, file_name):
    r = requests.get(url)
    content = r.content.decode("utf-8")
    file.mkfile(content, dir_path, file_name)


def get_hashfile_url():
    raw_data = send_tcp_request('203.107.54.123', 80, '000a002a3000000837120130')
    data = raw_data.decode("utf-8", "ignore")
    hashes = re.findall(r'\$(.*?)hash(.*?)\"', data)
    hashfile_url = {}
    for h in hashes:
        hashfile_url[h[0]] = f"${h[0]}hash{h[1]}"
    return hashfile_url
