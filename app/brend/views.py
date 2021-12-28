from datetime import datetime
import json
import os
import uuid

from aiohttp import web
import aiohttp_jinja2

from init import log_message, superadmins, SITE_LINK, archive_files
from gdrive_app import send_file, get_regional_users, send_message_tg, send_video_tg
from telegram.core.Db import Db


class MainPage(web.View):
    
    db = Db()
    cursor = db.cursor
    conn = db.conn
    translit_table = {
        'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E',
        'Н': 'H', 'І': 'I', 'К': 'K', 'М': 'M',
        'О': 'O', 'Р': 'P', 'Т': 'T', 'Х': 'X',
    }

    @aiohttp_jinja2.template("index.html")
    async def get(self):
        """
        0 - id
        1 - name
        2 - ukr_name
        3 - dir_id
        :return: list
        """
        sql = "select * from cities"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        cities = [{'name': city[2], 'id': city[0]} for city in result]
        year = datetime.now().year
        return {'cities': cities, 'year': year}

    async def post(self):
        error = ""
        request_id = str(uuid.uuid4())
        try:
            async for obj in (await self.request.multipart()):
                try:
                    if obj.name == 'gov_num':
                        gov_num = await obj.json()
                        gov_num = gov_num.replace('__', '_').replace('"', '').replace(' ', '').upper()

                        gov_num_arr = []

                        for symbol in gov_num:
                            if self.translit_table.get(symbol):
                                symbol = self.translit_table[symbol]
                            gov_num_arr.append(symbol)
                        gov_num = ''.join(gov_num_arr)

                        # validate gov_num
                        for symbol in gov_num:
                            if not symbol in self.translit_table.values() and not symbol.isdigit():
                                error = f"Введено не корректний державний номер авто. Символ '{symbol}' не допустимий у державних номерах"
                                log_message(error, 1, request_id)
                                return web.Response(text=json.dumps({'error': error}))
                                
                    elif obj.name == 'callsign':
                        callsign = str(json.dumps(await obj.json()))
                    elif obj.name == 'city_id':
                        city_id = int(json.dumps(await obj.json()))
                    elif obj.name == 'file':
                        filename = str(obj.filename).replace('__', '_')
                        file = await obj.read()
                except Exception as e:
                        log_message(e, 3, request_id)
                        error = "Помилка при отриманнi даних. Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову"
                        return web.Response(text=json.dumps({'error': error}))
        except Exception as e:
            log_message(e, 3, request_id)
            error = "Помилка при завантаженні даних. Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову"

        if error:
            return web.Response(text=json.dumps({'error': error}))

        try:
            log_message(f"New send request: callsign: {callsign}, gov_num: {gov_num}, city_id: {city_id}", 1, request_id)
            filename = request_id + '.' + filename.split('.')[-1]
            filepath = "/web/uk-brend/files/" + filename

            with open(filepath, 'wb') as f:
                f.write(file)
            
            log_message(f"file was temporary saved at {filepath}", 1, request_id)
            
            send_status = send_file(filepath, callsign, city_id, gov_num, request_id)
            if send_status is None:
                log_message(f"Error while upload video to gdrive", 2, request_id)
                
                os.rename(filepath, f"{archive_files}/{filename}")
                log_message(f"Move file {filepath} to {archive_files}/{filename}")

                text = f"❗️По какой-то причине данное видео не загрузилось на гугл диск\nПозывной: {callsign}\nГос. номер: {gov_num}\n❗️Просмотреть и скачать видео вручную можно по ссылке в течении месяца\n{SITE_LINK}file?filename={filename}"
                regional_users = get_regional_users(city_id)
                if regional_users:
                    for user in regional_users:
                        send_message_tg(text, user[1], request_id)

                text = text + f".\n.\n.\n{city_id=}\n{request_id=}"
                for admin in superadmins:
                    send_message_tg(text, admin, request_id)
                
        except Exception as e:
            log_message(e, 3, request_id)
            error = "Помилка при завантаженні даних. Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову"
            return web.Response(text=json.dumps({'error': error}))

        return web.Response(text=json.dumps({'error': ''}))
    
class ViewFile(web.View):

    async def get(self):
        request_id = str(uuid.uuid4())
        filename = self.request.rel_url.query['filename']
        filepath = f"{archive_files}/{filename}"
        log_message(f"Request to view file '{filepath}'", 1, request_id)
        if os.path.exists(filepath):
            return web.FileResponse(filepath)
        else:
            return web.HTTPNotFound()