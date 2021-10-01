from aiohttp import web
import aiohttp
import aiohttp_jinja2
from datetime import datetime
import json


class MainPage(web.View):

    @aiohttp_jinja2.template("index.html")
    async def get(self):
        # TODO: Проверить города в кеше или выгрузить города из БД и сформировать новый кеш
        cities = [{'name': 'Мариуполь', 'id': 1}, {'name': 'Киев', 'id': 2}]
        year = datetime.now().year
        # TODO: Отдать ответ
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
