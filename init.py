from pathlib import *
from gdrive.gdrive import auth_and_get_service
import sys
from telegram.core.Logger import Logger

SCOPES = ['https://www.googleapis.com/auth/drive']

superadmins = ['439874726']

"""
Permissions:
    1 - driver
    2 - regional_acc
    3 - admin
    4 - superadmin
"""

home_dir = Path.home()
work_directory = home_dir / 'projects' / 'uk-brend'

core_directory = work_directory / 'core'
gdrive_dir = work_directory / 'gdrive'
states_dir = work_directory / 'states'
database_file = work_directory / 'autobot.db'
credentials_file = gdrive_dir / 'credentials.json'
token_file = gdrive_dir / 'token.json'
files_dir = work_directory / 'files'
log_file_bot = work_directory / 'logs' / 'bot.log'

log = Logger.get_instance(log_file_bot).info

try:
    service = auth_and_get_service(token_file, credentials_file, SCOPES)
except Exception as e:
    log(e, exc_info=1)
    log('can`t connect to google drive api')
    sys.exit(2)
