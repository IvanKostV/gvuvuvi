import os
import sys
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from database.db import Database
from aiogram.contrib.fsm_storage.memory import MemoryStorage

"""Создаем бота"""
storage = MemoryStorage()

load_dotenv()

"""Определяем токен по параметру из командной строки"""
if len(sys.argv) > 1:
    l_param_1 = sys.argv[1].upper()
    l_token_name = "BOT_" + l_param_1
    if os.environ.get(l_token_name) is None:
        print("Error in create_bot.py: This token does not exist")
        sys.exit(1)
else:
    l_token_name = "BOT_MASTER"

bot = Bot(token=os.environ.get(l_token_name))
dp = Dispatcher(bot, storage=storage)
db = Database('trainee_database.db')