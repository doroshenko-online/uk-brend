from init import service, files_dir
from gdrive.misc import *
import os
from telegram.core.Db import Db
from telegram.core.City import City
import pathlib
import time
import requests
from telegram.tokens import TOKEN
import mimetypes
import googleapiclient.errors


db = Db()
cursor = db.cursor
conn = db.conn

def scan_dir():

    errors_count = 0

    while True:
        new_videos = os.listdir(files_dir)
        if len(new_videos) > 1:
            errors = []
            new_videos.remove('__init__.py')
            video_name = new_videos.pop()
            video_path = files_dir / video_name
            print(video_path)
            try:
                callsign, city_id, gov_num, filename = video_name.split('__')
            except:
                os.remove(video_path)
                time.sleep(1)
                continue

            mime_type, _ = mimetypes.guess_type(video_path)
            sql = "select * from cities where id=?"
            val = (city_id,)
            try:
                cursor.execute(sql, val)
            except Exception:
                print('Something wrong with getting city from database')
                time.sleep(1)
                os.remove(video_path)
                continue

            result = cursor.fetchone()
            if result:
                dir_id = str(result[3])
            else:
                os.remove(video_path)
                time.sleep(1)
                continue

            
            try_count = 2
            i = 0
            while i < try_count:
                i += 1
                try:
                    files_in_city_dir = show_files_in_directory(dir_id)
                except BrokenPipeError as ex:
                    errors.append(ex)
                    errors.append('Broken pipe error while connect to google drive')
                    if i == try_count:
                        time.sleep(1)
                        continue
                except IOError as ex:
                    errors.append(ex)
                    errors.append('IO Error while connect to google drive')
                    if i == try_count:
                        time.sleep(1)
                        continue
                else:
                    break
            month_year_dir = get_month_year()
            for file in files_in_city_dir:
                if file['name'] == month_year_dir:
                    parents_upload_dir_id = file['id']
                    break
            else:
                try:
                    parents_upload_dir_id = create_folder(month_year_dir, dir_id)
                except googleapiclient.errors.HttpError as ex:
                    errors.append(ex)
                    errors.append(f'Error while creating folder in parent {str(dir_id)} with name {str(month_year_dir)}')
                    print(f'Error while creating folder in parent {str(dir_id)} with name {str(month_year_dir)}')
                    os.remove(video_path)
                    time.sleep(1)
                    continue

            files = show_files_in_directory(parents_upload_dir_id)
            video_extension = video_name.split('.')[-1]
            file_index = 1

            video_name = gov_num
            new_video_name = video_name

            while True:
                for file in files:
                    if file['name'] == new_video_name + '.' + video_extension:
                        new_video_name = video_name + f'({str(i)})'
                        file_index += 1
                        break
                else:
                    break
            try:
                file_id = upload_video(video_path, new_video_name + '.' + video_extension, parents_upload_dir_id, mime_type)

            except googleapiclient.errors.HttpError as ex:
                errors.append(ex)
                errors.append(f'Error while file upload with name {new_video_name}')
                time.sleep(1)
            finally:
                os.remove(video_path)
                continue
        time.sleep(1)


if __name__ == '__main__':
    scan_dir()