from aiogram import types
from aiogram import Dispatcher
from dotenv import load_dotenv

load_dotenv()

async def other_message(message: types.Message):
    """Регистрация пользователя"""
    await message.reply('Я не знаю такой команды. Для получения списка команд введи команду /help')


def register_handlers_other(dp: Dispatcher):
    """Регистрируем диспетчеры"""
    dp.register_message_handler(other_message)



