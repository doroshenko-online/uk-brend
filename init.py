from pathlib import *
import pathlib
from gdrive.gdrive import auth_and_get_service
import sys
from datetime import datetime

def log_message(message, level: int = 1, request_id: str = '0'):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = str(message)
    if level == 1:
        string_level = 'INFO'
    elif level == 2:
        string_level = 'WARNING'
    elif level == 3:
        string_level = 'ERROR'
    template = f"[{dt}][{string_level}][{request_id}] ---- {message} ----"
    print(template, flush=True)


SCOPES = ['https://www.googleapis.com/auth/drive']
SITE_LINK = "http://uklon-branding.com.ua/"

superadmins = ['439874726']

"""
Permissions:
    1 - driver
    2 - regional_acc
    3 - admin
    4 - superadmin
"""

work_directory = pathlib.Path('/web/uk-brend')

core_directory = work_directory / 'core'
gdrive_dir = work_directory / 'gdrive'
states_dir = work_directory / 'states'
database_file = work_directory / 'autobot.db'
credentials_file = gdrive_dir / 'credentials.json'
token_file = gdrive_dir / 'token.json'
files_dir = work_directory / 'files'
archive_files = '/web/uk-brend/archive_files'

try:
    service = auth_and_get_service(token_file, credentials_file, SCOPES)
except Exception as e:
    log_message(e, exc_info=1)
    log_message('can`t connect to google drive api')
    sys.exit(2)
