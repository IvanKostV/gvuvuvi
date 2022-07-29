import logging
from aiogram import executor
from create_bot import dp
from handlers import client, fsm_check_client, other, tests, admin

"""Запускаем бота"""
logging.basicConfig(level=logging.INFO)


client.register_handlers_client(dp=dp)
admin.register_handlers_admin(dp=dp)
fsm_check_client.register_handlers_admin(dp=dp)
tests.register_handlers_tests(dp=dp)
other.register_handlers_other(dp=dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
