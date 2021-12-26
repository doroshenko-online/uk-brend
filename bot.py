import googleapiclient.errors
from aiogram.types.message import Message
from init import *
from gdrive.misc import *
import os
from pathlib import *
from telegram.keyboards import *
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from telegram.core.Loader import Loader
from telegram.core.City import City
from telegram.core.Register import Registry
from telegram.core.User import User
from telegram.states.StateCity import StateCity
from telegram.states.StateNumber import StateNumber
from telegram.states.StateAddCity import AddCity
from telegram.states.StateAddRegionalAcc import AddRegionalAcc
from telegram.states.StateUploadReview import UploadReview
from telegram.states.StateChangeCity import ChangeCity
from telegram.states.StateAddAdmin import AddAdmin
import asyncio
from aiogram.utils import executor
from telegram.tokens import TOKEN

"""
Actions:

    Новые пользователи:
        👉 Выбрать город
        ℹ️ Получить ссылку на сайт
        
    Водители:
        🛠 Указать гос. номер
        🔂 Сменить гос. номер
        ↪ Сменить город
        🆕 Загрузить осмотр
        
    Региональные аккаунты:
        👿 Показать заблокированных водителей по городу
        (inline) Заблокировать
        (inline) Разблокирвать
        🆕 Загрузить осмотр
        
    Администраторы:
        🌆 Добавить город
        (inline) Изменить город
        👁 Показать все города
        🧔 Добавить администратора
        🐕 Добавить региональный аккаунт    

"""

MAX_FILE_SIZE = 150000000

memory_storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=memory_storage)
loader = Loader()
downloads_users = []


# ---------------- Общие обработчики
@dp.message_handler(commands=['start', 'help'])
async def start(msg: types.Message):
    text = start_text(msg.chat.id)
    keyboard = start_keyboard(msg.chat.id)
    await msg.answer(text, reply_markup=keyboard)


@dp.message_handler(commands=['id'])
async def get_id(msg: types.Message):
    await msg.answer(msg.chat.id)


@dp.message_handler(commands="cancel", state="*")
async def cancel_cmm(msg: types.Message, state: FSMContext):
    if str(msg.chat.id) in downloads_users:
        return
    user = Registry.get_user(msg.chat.id)
    message = start_text(msg.chat.id)
    keyboard = start_keyboard(msg.chat.id)
    if (user is None and str(msg.chat.id) not in superadmins) or user.isdriver():
        await msg.answer("Дію скасовано", reply_markup=None)
    else:
        await msg.answer("Действие отменено", reply_markup=None)
    await msg.answer(message, reply_markup=keyboard)
    await state.finish()


@dp.message_handler(Text(equals="Скасувати", ignore_case=True), state="*")
async def cancel_ukr(msg: types.Message, state: FSMContext):
    if str(msg.chat.id) in downloads_users:
        return
    message = start_text(msg.chat.id)
    keyboard = start_keyboard(msg.chat.id)
    await msg.answer("Дію скасовано", reply_markup=None)
    await msg.answer(message, reply_markup=keyboard)
    await state.finish()


@dp.message_handler(Text(equals="Отмена", ignore_case=True), state="*")
async def cancel(msg: types.Message, state: FSMContext):
    if str(msg.chat.id) in downloads_users:
        return
    message = start_text(msg.chat.id)
    keyboard = start_keyboard(msg.chat.id)
    await msg.answer("Действие отменено", reply_markup=None)
    await msg.answer(message, reply_markup=keyboard)
    await state.finish()


@dp.message_handler(Text(startswith="🆕", ignore_case=True), content_types=types.ContentTypes.TEXT)
async def upload_review_start(msg: types.Message):
    user = Registry.get_user(msg.chat.id)
    cancel_kb = cancel_keyboard()
    cancel_text = cancel_text_func()
    if user:
        text = ''
        if user.isdriver():
            if user.state_number:
                cancel_kb = cancel_keyboard_ukr()
                cancel_text = cancel_text_func_ukr()
                if user.isblocked():
                    text = 'Вам тимчасово обмежено можливість завантажувати огляди. Зверніться до представництва Uklon.'
                    await msg.answer(text)
                    return
                else:
                    text = 'Завантажте відео або зніміть нове\n(розмір файлу не повинен перевищувати 150МБ\nрозмір відео-нотації не більше 20МБ)'
                    await UploadReview.wait_for_video.set()

        elif user.isregionuser():
            await UploadReview.wait_for_video_name.set()
            text = 'Введите название для видео, которое будет на гугл диске'

        else:
            return

        await msg.answer(text)
        await msg.answer(cancel_text, reply_markup=cancel_kb)

# ---------------- Обработчики для новых пользователей

# Выбор города


@dp.message_handler(Text(startswith="👉", ignore_case=True), content_types=types.ContentTypes.TEXT)
async def set_city_start(msg: types.Message, state: FSMContext):
    keyboard = city_inline_keyboard()
    await StateCity.wait_for_city.set()
    text = 'Оберіть ваше місто'
    cancel_text = cancel_text_func_ukr()
    cancel_kb = cancel_keyboard_ukr()
    mes1 = await bot.send_message(msg.chat.id, text, reply_markup=keyboard)
    mes2 = await bot.send_message(msg.chat.id, cancel_text, reply_markup=cancel_kb)
    await state.update_data(msg_city=mes1.message_id)
    await state.update_data(msg_cancel=mes2.message_id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('city_id'), state=StateCity.wait_for_city)
async def processing_city(callback_query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    city_id = int(str(callback_query.data).replace('city_id:', ''))
    await bot.delete_message(callback_query.message.chat.id, state_data['msg_city'])
    await bot.delete_message(callback_query.message.chat.id, state_data['msg_cancel'])
    loader.add_user(callback_query.message.chat.id, callback_query.message.chat.username, city_id)
    await state.finish()
    message = start_text(callback_query.message.chat.id)
    keyboard = start_keyboard(callback_query.message.chat.id)
    await bot.send_message(callback_query.message.chat.id, message, reply_markup=keyboard)

# Получить ссылку на сайт загрузки осмотра

@dp.message_handler(Text(startswith="ℹ️", ignore_case=True), content_types=types.ContentTypes.TEXT)
async def get_site_link(msg: types.Message):
    kb = start_keyboard(msg.chat.id)
    await msg.answer(SITE_LINK, reply_markup=kb)


# ---------------- Обработчики для администраторов

# Добавить город
@dp.message_handler(Text(startswith="🌆", ignore_case=True), content_types=types.ContentTypes.TEXT)
async def add_city_start(msg: types.Message, state: FSMContext):
    user = Registry.get_user(msg.chat.id)
    if str(msg.chat.id) in superadmins or user.isadmin():
        await AddCity.wait_for_city_name.set()
        text = 'Введите название города(не будет отображатся водителю)'
        cancel_kb = cancel_keyboard()
        await msg.answer(text, reply_markup=cancel_kb)


@dp.message_handler(state=AddCity.wait_for_city_name, content_types=types.ContentTypes.TEXT)
async def add_city_name(msg: types.Message, state: FSMContext):
    city_name = str(msg.text).strip()
    await state.update_data(city_name=city_name)
    await AddCity.wait_for_city_ukr_name.set()
    text = 'Введите название города на украинском(будет отображатся водителю)'
    await msg.answer(text)


@dp.message_handler(state=AddCity.wait_for_city_ukr_name, content_types=types.ContentTypes.TEXT)
async def add_city_ukr_name(msg: types.Message, state: FSMContext):
    city_ukr_name = str(msg.text).strip()
    await state.update_data(city_ukr_name=city_ukr_name)
    await AddCity.wait_for_city_id.set()
    text = 'Введите id папки этого города'
    await msg.answer(text)


@dp.message_handler(state=AddCity.wait_for_city_id, content_types=types.ContentTypes.TEXT)
async def add_city_id(msg: types.Message, state: FSMContext):
    city_id = str(msg.text).strip()
    data = await state.get_data()
    try:
        City.validate_dirid(city_id)
    except AssertionError:
        text = "Папки для города {0} с id {1} не существует!! ❌".format(data['city_name'], city_id)
        await msg.answer(text)
        return
    else:
        if City.selectcitybyid(city_id):
            await msg.answer('Город уже существует', reply_markup=start_keyboard(msg.chat.id))
            await state.finish()
        else:
            loader.add_city(data['city_name'], data['city_ukr_name'], city_id)
            text = 'Город {0} с id {1} успешно добавлен!! ✅'.format(data['city_name'], city_id)
            kb = start_keyboard(msg.chat.id)
            await msg.answer(text, reply_markup=kb)
            await state.finish()


# Показать все города
@dp.message_handler(Text(startswith="👁", ignore_case=True), content_types=types.ContentTypes.TEXT)
async def show_cities(msg: types.Message):
    user = Registry.get_user(msg.chat.id)
    if str(msg.chat.id) in superadmins or user.isadmin():
        text = 'Список городов'
        kb = city_inline_keyboard(True)
        await msg.answer(text, reply_markup=kb)


# Изменить город
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('show_city_id'))
async def change_city(callback_query: types.CallbackQuery):
    city_id = int(str(callback_query.data).replace('show_city_id:', ''))
    kb = change_city_inline_keyboard(city_id)
    await callback_query.message.edit_reply_markup(reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('selected_show_city_id'))
async def change_city(callback_query: types.CallbackQuery):
    kb = city_inline_keyboard(True)
    await callback_query.message.edit_reply_markup(reply_markup=kb)


# Изменить название города
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('change_city_name'))
async def change_city_name_start(callback_query: types.CallbackQuery, state: FSMContext):
    kb = city_inline_keyboard(True)
    await callback_query.message.edit_reply_markup(reply_markup=kb)
    city_id = int(str(callback_query.data).replace('change_city_name:', ''))
    await ChangeCity.wait_for_city_name.set()
    await state.update_data(city_id=city_id)
    text = 'Введите новое название города(не отображается у водителей)'
    cancel_kb = cancel_keyboard()
    await callback_query.message.answer(text, reply_markup=cancel_kb)


@dp.message_handler(state=ChangeCity.wait_for_city_name, content_types=types.ContentTypes.TEXT)
async def change_city_name_processing(msg: types.Message, state: FSMContext):
    city_name = str(msg.text).strip()
    city_id = await state.get_data()
    city_id = int(city_id['city_id'])
    kb = start_keyboard(msg.chat.id)
    text = 'Название города изменено на ' + city_name
    city = Registry.get_city(city_id)
    if city.change_name(city_name):
        await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer('Something wrong with change city')

    await state.finish()


# Изменить украинское название города
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('change_city_ukr_name'))
async def change_city_ukr_name_start(callback_query: types.CallbackQuery, state: FSMContext):
    kb = city_inline_keyboard(True)
    await callback_query.message.edit_reply_markup(reply_markup=kb)
    city_id = int(str(callback_query.data).replace('change_city_ukr_name:', ''))
    await ChangeCity.wait_for_city_ukr_name.set()
    await state.update_data(city_id=city_id)
    text = 'Введите новое название города на украинском(отображается у водителей)\n Текущее украинское название: ' + Registry.get_city(city_id).ukr_name
    cancel_kb = cancel_keyboard()
    await callback_query.message.answer(text, reply_markup=cancel_kb)


@dp.message_handler(state=ChangeCity.wait_for_city_ukr_name, content_types=types.ContentTypes.TEXT)
async def change_city_ukr_name_processing(msg: types.Message, state: FSMContext):
    city_ukr_name = str(msg.text).strip()
    city_id = await state.get_data()
    city_id = int(city_id['city_id'])
    kb = start_keyboard(msg.chat.id)
    text = 'Украинское название города изменено на ' + city_ukr_name
    city = Registry.get_city(city_id)
    if city.change_ukrname(city_ukr_name):
        await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer('Something wrong with change city')

    await state.finish()


# Изменить id папки города
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('change_city_dir_id'))
async def change_city_dir_id_start(callback_query: types.CallbackQuery, state: FSMContext):
    kb = city_inline_keyboard(True)
    await callback_query.message.edit_reply_markup(reply_markup=kb)
    city_id = int(str(callback_query.data).replace('change_city_dir_id:', ''))
    await ChangeCity.wait_for_city_dir_id.set()
    await state.update_data(city_id=city_id)
    text = 'Введите новый id папки города'
    cancel_kb = cancel_keyboard()
    await callback_query.message.answer(text, reply_markup=cancel_kb)


@dp.message_handler(state=ChangeCity.wait_for_city_dir_id, content_types=types.ContentTypes.TEXT)
async def change_city_dir_id_processing(msg: types.Message, state: FSMContext):
    city_dir_id = str(msg.text).strip()
    city_id = await state.get_data()
    city_id = int(city_id['city_id'])
    try:
        City.validate_dirid(city_dir_id)
    except AssertionError:
        kb = start_keyboard(msg.chat.id)
        await msg.answer('Такого id не существует на гугл диске', reply_markup=kb)
        await state.finish()
    else:
        kb = start_keyboard(msg.chat.id)
        text = 'id папки города изменено на ' + city_dir_id
        city = Registry.get_city(city_id)
        city.change_dir_id(city_dir_id)
        await state.finish()
        await msg.answer(text, reply_markup=kb)

# Изменить id папки города
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('change_city_delete'))
async def change_city_delete(callback_query: types.CallbackQuery, state: FSMContext):
    city_id = int(str(callback_query.data).replace('change_city_delete:', ''))
    city = Registry.unload_city(city_id)
    if city:
        if city.delete_city():
            Registry.unload_city(city_id)
            text = f"Город с id {city_id} успешно удален"
        else:
            text = f"Произошла ошибка при удалении города с id {city_id}"
    else:
        text = f"Города с id {city_id} не оказалось в списке. Удаление невозможно"
    kb = city_inline_keyboard(True)
    await callback_query.message.edit_reply_markup(reply_markup=kb)
    await callback_query.message.answer(text, reply_markup=start_keyboard(callback_query.message.chat.id))

# Добавить администратора
@dp.message_handler(Text(startswith="🧔", ignore_case=True), content_types=types.ContentTypes.TEXT)
async def add_admin_start(msg: types.Message):
    user = Registry.get_user(msg.chat.id)
    if str(msg.chat.id) in superadmins or user.isadmin():
        cancel_kb = cancel_keyboard()
        text = 'Введите chat id пользователя'
        await AddAdmin.wait_for_chat_id.set()
        await msg.answer(text, reply_markup=cancel_kb)


@dp.message_handler(state=AddAdmin.wait_for_chat_id, content_types=types.ContentTypes.TEXT)
async def add_admin_proccesing_chat_id(msg: types.Message, state: FSMContext):
    chat_id = int(str(msg.text).strip())
    user = Registry.get_user(chat_id)
    username = str(msg.chat.username)
    if user:
        user.change_permission(3)
    else:
        loader.add_user(chat_id=chat_id, username=username, permission_level=3)

    await state.finish()
    text = 'Администратор добавлен'
    kb = start_keyboard(msg.chat.id)
    await msg.answer(text, reply_markup=kb)


# Добавить региональный аккаунт
@dp.message_handler(Text(startswith="🐕", ignore_case=True), content_types=types.ContentTypes.TEXT)
async def add_region_acc_start(msg: types.Message):
    user = Registry.get_user(msg.chat.id)
    if str(msg.chat.id) in superadmins or user.isadmin():
        await AddRegionalAcc.wait_for_chat_id.set()
        text = 'Введите чат-ид регионального аккаунта'
        await msg.answer(text)
        cancel_kb = cancel_keyboard()
        cancel_text = cancel_text_func()
        await msg.answer(cancel_text, reply_markup=cancel_kb)


@dp.message_handler(state=AddRegionalAcc.wait_for_chat_id, content_types=types.ContentTypes.TEXT)
async def add_regiona_acc_processing(msg: types.Message, state: FSMContext):
    reg_acc_chat_id = str(msg.text).strip()
    user = Registry.get_user(reg_acc_chat_id)
    if user or str(msg.chat.id) in superadmins:
        user.change_permission(2)
        await state.finish()
        kb = start_keyboard(msg.chat.id)
        text = 'Пользователь добавлен как региональный аккаунт'
        await msg.answer(text, reply_markup=kb)
    else:
        await msg.answer('Данного пользователя нет в базе. Пользователю необходимо зайти в бота и выбрать город')
        return

# ---------------- Обработчики для superadmin


if __name__ == '__main__':
    executor.start_polling(dp)
