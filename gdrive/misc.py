from init import *
from googleapiclient.errors import HttpError
from googleapiclient.discovery import MediaFileUpload
from datetime import date, datetime


def upload_video(file, name, folder_id, mimetype='video/mp4'):
    file_metadata = {
        'name': name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file, mimetype=mimetype, resumable=True)
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  supportsAllDrives=True,
                                  fields='id', ).execute()

    return file.get('id')


def create_folder(name, parents_dir_id=None):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parents_dir_id:
        file_metadata['parents'] = [parents_dir_id]

    file = service.files().create(
        body=file_metadata,
        supportsAllDrives=True,
        fields='id').execute()
    return file.get('id')


def find_file_by_name(name):
    try:
        response = service.files().list(q=f"name='{name}'",
                                spaces='drive',
                                includeItemsFromAllDrives=True,
                                supportsAllDrives=True).execute()
    except HttpError as e:
<<<<<<< HEAD
        log_message(e, 2)
        log_message(f'Error while find file {name}', 2)
=======
        log_message(e)
        log_message(f'Error while find file {name}')
>>>>>>> 81f353c1fd948525ca43f682828ed12c0162d2ed
        return None

    return response['files']


def find_file_by_id(fid):
    try:
        response = service.files().get(fileId=fid, supportsAllDrives=True).execute()
    except HttpError as e:
<<<<<<< HEAD
        log_message(e, 2)
        log_message(f'Error while find file by id {str(fid)}', 2)
=======
        log_message(e)
        log_message(f'Error while find file by id {str(fid)}')
>>>>>>> 81f353c1fd948525ca43f682828ed12c0162d2ed
        return None

    return response


def show_files_in_directory(dir_id):
    try:
        response = service.files().list(q=f"'{str(dir_id)}' in parents",
                                spaces='drive',
                                includeItemsFromAllDrives=True,
                                supportsAllDrives=True,
                                fields='files(id, name)').execute()
    except HttpError as e:
<<<<<<< HEAD
        log_message(e, 2)
        log_message(f'Error show list files in dir {str(dir_id)}', 2)
=======
        log_message(e)
        log_message(f'Error show list files in dir {str(dir_id)}')
>>>>>>> 81f353c1fd948525ca43f682828ed12c0162d2ed
        return None

    return [file for file in response['files']]


def get_month_year():
    month = str(datetime.now().month)
    year = str(datetime.now().year)
    if int(month) < 10:
        month = '0' + month
    return month + '.' + year
