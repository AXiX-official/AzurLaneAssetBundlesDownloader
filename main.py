import downloader
from downloader import *

conflicts = {}

for key, value in hash_csv_name.items():
    download_hashfile(key)
    merge_hashfile(key, overwrite=True)


