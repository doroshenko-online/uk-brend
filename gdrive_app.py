from init import service, files_dir
from gdrive.misc import *
import os
from telegram.core.Db import Db
import pathlib
import time
import requests
from telegram.tokens import TOKEN

db = Db()
cursor = db.cursor
conn = db.conn

def scan_dir():

    errors_count = 0

    while True:
        new_videos = os.listdir(files_dir)
        if len(new_videos) > 1:
            new_videos.remove('__init__.py')
            video_name = new_videos.pop()
            callsign, city_id, gov_num, filename = video_name.split('__')
            print(callsign)
            print(city_id)
            print(gov_num)
            print(filename)
            break
        time.sleep(1)


if __name__ == '__main__':
    scan_dir()