from aiohttp import web
import aiohttp
import aiohttp_jinja2
from datetime import datetime
import json
from telegram.core.Db import Db
from init import work_directory


class MainPage(web.View):
    
    db = Db()
    cursor = db.cursor
    conn = db.conn

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
        async for obj in (await self.request.multipart()):
            try:
                if obj.name == 'gov_num':
                    gov_num = str(json.dumps(await obj.json())).replace('__', '_').replace('"', '')
                elif obj.name == 'callsign':
                    callsign = str(json.dumps(await obj.json()))
                elif obj.name == 'city_id':
                    city_id = int(json.dumps(await obj.json()))
                elif obj.name == 'file':
                    filename = str(obj.filename).replace('__', '_')
                    file = await obj.read()
            except Exception as e:
                    print(e)
                    error = "Помилка при отриманнi даних. Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову"
                    return web.Response(text=json.dumps({'error': error}))
        try:
            with open(work_directory / 'files' / + callsign + '__' + str(city_id) + '__' + gov_num + '__' + filename, 'wb') as f:
                f.write(file)
        except:
            error = "Помилка при завантаженні даних. Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову"

        return web.Response(text=json.dumps({'error': ''}))
