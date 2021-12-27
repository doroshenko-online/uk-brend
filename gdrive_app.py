import os
from sys import argv
import requests

import mimetypes
import googleapiclient.errors

from init import log_message
from gdrive.misc import *
from telegram.core.Db import Db
from telegram.tokens import TOKEN


db = Db()
cursor = db.cursor
conn = db.conn

file_link_temp = "https://drive.google.com/file/d/{0}/view?usp=sharing"
tg_link = f"https://api.telegram.org/bot{TOKEN}"
tg_actions = {'send_video': 'sendVideo', 'send_message': 'sendMessage'}

def send_file(video_path, callsign, city_id, gov_num, request_id):
    mime_type, _ = mimetypes.guess_type(video_path)
    sql = "select * from cities where id=?"
    val = (city_id,)
    try:
        cursor.execute(sql, val)
    except Exception:
        log_message('Something wrong with getting city from database', 3, request_id)
        return None

    result = cursor.fetchone()
    if result:
        dir_id = str(result[3])
    else:
        log_message(f"Can't get city from database with id {city_id}", 3, request_id)
        return None

    city_name = result[1]
    log_message(f"{dir_id=} {city_id=} {city_name=}", 1, request_id)

    try_count = 2
    i = 0
    while i < try_count:
        i += 1
        try:
            files_in_city_dir = show_files_in_directory(dir_id)
        except BrokenPipeError as ex:
            log_message('Broken pipe error while connect to google drive', 2, request_id)
            if i == try_count:
                log_message(ex, 3, request_id)
                return None
        except IOError as ex:
            log_message('IO Error while connect to google drive', 2, request_id)
            if i == try_count:
                log_message(ex, 3, request_id)
                return None
        except Exception as ex:
            log_message('Error while connect to google drive', 2, request_id)
            if i == try_count:
                log_message(ex, 3, request_id)
                return None
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
            log_message(ex, 3 ,request_id)
            log_message(f'HttpError while creating folder in parent {str(dir_id)} with name {str(month_year_dir)}', 3, request_id)
            return None

        except Exception as e:
            log_message(e, 3, request_id)
            log_message(f'Error while creating folder in parent {str(dir_id)} with name {str(month_year_dir)}', 3, request_id)
            return None

    log_message(f"{parents_upload_dir_id=}", 1, request_id)

    files = show_files_in_directory(parents_upload_dir_id)
    video_extension = video_path.split('.')[-1]
    file_index = 1

    video_name = gov_num
    new_video_name = video_name

    log_message(f"Video name: {video_name}.{video_extension}", 1, request_id)
    log_message(f"Count of files in gdrive directory {str(len(files))}", 1, request_id)

    while True:
        for i, file in enumerate(files):
            if file['name'] == str(new_video_name + '.' + video_extension):
                new_video_name = video_name + f'({str(file_index)})'
                file_index += 1
                break
        else:
            break
    
    log_message(f"New video name: {new_video_name}.{video_extension}", 1, request_id)

    file_id = ''
    try:
        file_id = upload_video(video_path, new_video_name + '.' + video_extension, parents_upload_dir_id, mime_type)

    except googleapiclient.errors.HttpError as ex:
        log_message(f'HttpError while file upload with name {new_video_name}', 3, request_id)
        log_message(ex, 3, request_id)
        return None
    except Exception as ex:
        log_message(f'Error while file upload with name {new_video_name}', 3, request_id)
        log_message(ex, 3, request_id)
        return None
    finally:
        os.remove(video_path)
        log_message(f"Removing file {video_path}", 1, request_id)

    link = file_link_temp.format(file_id)
    text_message = f"Позывной {callsign} с гос. номером {gov_num} отправил осмотр -\n{link}"
    log_message(text_message, 1, request_id)

    regional_users = get_regional_users(city_id)

    if regional_users:
        for regional_user in regional_users:
            send_message_tg(text_message, regional_user[1], request_id)

    return True


def get_regional_users(city_id):
    sql = "select * from users where city_id=? and permission_id=2"
    val = (city_id,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    return result


def send_message_tg(message, chat_id, request_id: str = '0'):
    log_message(f"TG: Send message to {chat_id}. {message=}", 1, request_id)
    r = requests.get(f"{tg_link}/{tg_actions['send_message']}?chat_id={chat_id}&text={message}")
    if r.status_code != 200:
        log_message(f"TG: Error while send message. {chat_id=} {request_id=}", 2, request_id)
        log_message(r.text, 2, request_id)


def send_video_tg(video_path, chat_id, request_id: str = '0'):
    log_message(f"TG: Send video to {chat_id}. {video_path=}", 1, request_id)
    files = {'video': open(video_path, 'rb')}
    data = {'chat_id' : chat_id}
    r = requests.post(f"{tg_link}/{tg_actions['send_video']}", files=files, params=data)
    if r.status_code != 200:
        log_message(f"TG: Error while send video. {video_path=} {chat_id=} {request_id=}", 2, request_id)
        log_message(r.text, 2, request_id)


if __name__ == "__main__":
    if len(argv) == 5:
        _, ARG_VIDEONAME, ARG_CALLSIGN, ARG_CITY_ID, ARG_GOV_NUM = argv
        request_id = ARG_VIDEONAME.split('.')[0]
        filepath = '/web/uk-brend/files/' + ARG_VIDEONAME
        if os.path.exists(filepath):
            send_status = send_file(filepath, ARG_CALLSIGN, ARG_CITY_ID, ARG_GOV_NUM, request_id)
            if send_status is None:
                log_message(f"Error while upload video to gdrive", 2, request_id)
                
                os.rename(filepath, f"{archive_files}/{ARG_VIDEONAME}")
                log_message(f"Move file {filepath} to {archive_files}/{ARG_VIDEONAME}")

                text = f"❗️По какой-то причине данное видео не загрузилось на гугл диск\nПозывной: {ARG_CALLSIGN}\nГос. номер: {ARG_GOV_NUM}\n❗️Просмотреть и скачать видео вручную можно по ссылке в течении месяца\n{SITE_LINK}file?filename={filename}"
                regional_users = get_regional_users(ARG_CITY_ID)
                if regional_users:
                    for user in regional_users:
                        send_message_tg(text, user[1], request_id)

                text = text + f".\n.\n.\n{ARG_CITY_ID=}\n{request_id=}"
                for admin in superadmins:
                    send_message_tg(text, admin, request_id)
        else:
            log_message(f"Incorrect filepath {filepath}", 2 ,request_id)