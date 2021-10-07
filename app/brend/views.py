from aiohttp import web
import aiohttp
import aiohttp_jinja2
from datetime import datetime
import json
from telegram.core.Db import DB


class MainPage(web.View):
    
    db = DB()
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
        result = self.cursor.cursor.fetchall()
        cities = [{'name': city[2], 'id': city[0]} for city in result]
        year = datetime.now().year
        return {'cities': cities, 'year': year}

    async def post(self):
        error = ""
        async for obj in (await self.request.multipart()):
            try:
                if obj.name == 'gov_num':
                    gov_num = str(json.dumps(await obj.json()))
                elif obj.name == 'callsign':
                    callsign = str(json.dumps(await obj.json()))
                elif obj.name == 'city_id':
                    city_id = int(json.dumps(await obj.json()))
                elif obj.name == 'file':
                    filename = obj.filename
                    file = await obj.read()
            except:
                    error = "Помилка при отриманнi даних. Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову"
                    return web.Response(text=json.dumps({'error': error}))

        with open('tmp/' + filename, 'wb') as f:
            f.write(file)

        return web.Response(text=json.dumps({'error': ''}))
