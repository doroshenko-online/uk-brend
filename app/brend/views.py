from aiohttp import web
import aiohttp_jinja2


class MainPage(web.View):

    @aiohttp_jinja2.template("index.html")
    async def get(self):
        # TODO: Засетить или проверить куки
        # TODO: Проверить города в кеше или выгрузить города из БД и сформировать новый кеш
        # TODO: Отдать ответ
        return {'title': 'hello'}