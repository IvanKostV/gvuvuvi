import json
import os
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types
from create_bot import db, bot, l_token_name
from aiogram.types import ContentTypes, Message
from requests import get
from aiogram import Dispatcher
from dotenv import load_dotenv

load_dotenv()


class FSMAdmin(StatesGroup):
    """Машина состояний"""
    file_name = State()
    number_of_task = State()
    result = State()


async def command_check(message: types.Message):
    """Пользователь вводит команду check (начинается проверка)"""
    await FSMAdmin.file_name.set()
    await message.reply('Загрузите ваше решение в формате - task_<task_id>.csv')


async def download_file(message: Message, state: FSMContext):
    """Загружаем файл пользователя"""
    try:
        file_id = message.document.file_id
        response = get("https://api.telegram.org/bot{token}/getFile?file_id={file_id}".format(token=os.environ.get(l_token_name),
                                                                                              file_id=file_id))
        resp_dict = json.loads(response.text)
        file_name = message.document.file_name
        async with state.proxy() as data:
            data['file_name'] = file_name
        file_path = resp_dict['result']['file_path']
        destination = r"./static/trainee_solutions/{user_id}_{file_name}".format(file_name=file_name,
                                                                                 user_id=message.from_user.id)
        await bot.download_file(file_path, destination=destination)
        await FSMAdmin.next()
        await message.reply('Введите номер задания')
    except:
        await message.reply("Вы отправили документ в неправильном формате!")
        await state.finish()


async def check_task_with_id(message: types.Message, state: FSMContext):
    """Пользователь вводит id таска и проверям"""
    try:
        async with state.proxy() as data:
            result = True
            with open(r"./static/answers/answer_{id}.csv".format(id=message.text), encoding="cp1251", mode='r') as answer, \
                    open(r"./static/trainee_solutions/{user_id}_{file_name}".format(file_name=data['file_name'],
                                                                                    user_id=message.from_user.id),
                         encoding="cp1251", mode='r') as solution:
                for ans, sol in zip(answer.readlines(), solution.readlines()):
                    if ans != sol:
                        result = False
                        break
            data['number_of_task'] = message.text
            if result:
                db.change_status_of_task_completed(user_id=message.from_user.id, task_id=message.text)
                os.unlink("static/trainee_solutions/{user_id}_{file_name}".format(file_name=data['file_name'],
                                                                                    user_id=message.from_user.id),)
                await FSMAdmin.next()
                await message.reply("Все верно! Введите комментарий.")
            else:
                db.change_status_of_task_in_progress(user_id=message.from_user.id, task_id=message.text)
                os.unlink("static/trainee_solutions/{user_id}_{file_name}".format(file_name=data['file_name'],
                                                                            user_id=message.from_user.id), )
                await state.finish()
                await message.reply("К сожалению решение неверное, попробуй ещё раз!)")
    except:
        await message.reply("Вы ввели неправильнй формат id задания")
        await state.finish()

async def update_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        db.update_comment_on_task(user_id=message.from_user.id,
                                  task_id=data['number_of_task'],
                                  user_comment=str(message.text))
    await message.reply("Ваш комментарий записан!")
    await state.finish()

async def cancel_handler(message: types.Message, state: FSMContext):
    """Выход из машины состояний"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Готово, давай продолжим!')


def register_handlers_admin(dp: Dispatcher):
    """Регистрируем хэндлеры"""
    dp.register_message_handler(command_check, commands=['check'], state=None)
    dp.register_message_handler(download_file, content_types=ContentTypes.DOCUMENT, state=FSMAdmin.file_name)
    dp.register_message_handler(check_task_with_id, state=FSMAdmin.number_of_task)
    dp.register_message_handler(update_comment,content_types=ContentTypes.TEXT ,state=FSMAdmin.result)
    dp.register_message_handler(cancel_handler, commands='cancel', state="*")
    dp.register_message_handler(cancel_handler, Text(equals='cancel', ignore_case=True), state="*")
