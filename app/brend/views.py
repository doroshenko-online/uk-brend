from aiohttp import web
import aiohttp_jinja2
from datetime import datetime

import yarl


class MainPage(web.View):

    @aiohttp_jinja2.template("index.html")
    async def get(self):
        # TODO: Засетить или проверить куки
        # TODO: Проверить города в кеше или выгрузить города из БД и сформировать новый кеш
        cities = [{'name': 'Мариуполь', 'id': 1}, {'name': 'Киев', 'id': 2}]
        year = datetime.now().year
        # TODO: Отдать ответ
        return {'cities': cities, 'year': year}