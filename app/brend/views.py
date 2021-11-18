from aiohttp import web
import aiohttp
import aiohttp_jinja2
from datetime import datetime
import json
from telegram.core.Db import Db
from init import files_dir


class MainPage(web.View):
    
    db = Db()
    cursor = db.cursor
    conn = db.conn
    dic = {'Ь':'', 'ь':'', 'Ъ':'', 'ъ':'', 'А':'A', 'а':'a', 'Б':'B', 'б':'b', 'В':'V', 'в':'v',
       'Г':'G', 'г':'g', 'Д':'D', 'д':'d', 'Е':'E', 'е':'e', 'Ё':'E', 'ё':'e', 'Ж':'Zh', 'ж':'zh',
       'З':'Z', 'з':'z', 'И':'I', 'и':'i', 'Й':'I', 'й':'i', 'К':'K', 'к':'k', 'Л':'L', 'л':'l',
       'М':'M', 'м':'m', 'Н':'N', 'н':'n', 'О':'O', 'о':'o', 'П':'P', 'п':'p', 'Р':'R', 'р':'r', 
       'С':'S', 'с':'s', 'Т':'T', 'т':'t', 'У':'U', 'у':'u', 'Ф':'F', 'ф':'f', 'Х':'Kh', 'х':'kh',
       'Ц':'Tc', 'ц':'tc', 'Ч':'Ch', 'ч':'ch', 'Ш':'Sh', 'ш':'sh', 'Щ':'Shch', 'щ':'shch', 'Ы':'Y',
       'ы':'y', 'Э':'E', 'э':'e', 'Ю':'Iu', 'ю':'iu', 'Я':'Ia', 'я':'ia'}
       
    alphabet = ['Ь', 'ь', 'Ъ', 'ъ', 'А', 'а', 'Б', 'б', 'В', 'в', 'Г', 'г', 'Д', 'д', 'Е', 'е', 'Ё', 'ё',
            'Ж', 'ж', 'З', 'з', 'И', 'и', 'Й', 'й', 'К', 'к', 'Л', 'л', 'М', 'м', 'Н', 'н', 'О', 'о',
            'П', 'п', 'Р', 'р', 'С', 'с', 'Т', 'т', 'У', 'у', 'Ф', 'ф', 'Х', 'х', 'Ц', 'ц', 'Ч', 'ч',
            'Ш', 'ш', 'Щ', 'щ', 'Ы', 'ы', 'Э', 'э', 'Ю', 'ю', 'Я', 'я']

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
        new_gov_num = []
        for symbol in gov_num:
            if symbol in self.alphabet:
                new_gov_num.append(self.dic[symbol])
            else:
                new_gov_num.append(symbol)
        new_gov_num = new_gov_num.join('')
        try:
            filepath = "/web/uk-brend/files/" + callsign + '__' + str(city_id) + '__' + new_gov_num + '__' + filename

            with open(filepath, 'wb') as f:
                f.write(file)
        except:
            error = "Помилка при завантаженні даних. Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову"

        return web.Response(text=json.dumps({'error': ''}))
