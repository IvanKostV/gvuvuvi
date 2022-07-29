from aiogram import types, Dispatcher
from create_bot import  bot, db
from keyboards import mainMenu
from dotenv import load_dotenv
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import re


load_dotenv()

class FSMAdmin(StatesGroup):
    """Машина состояний"""
    name = State()
    surname = State()
    group = State()

async def command_start(message: types.Message):
    if (not await db.user_exists(message.from_user.id)):
        await FSMAdmin.name.set()
        await bot.send_message(message.from_user.id,
                               "Привет! Рад приветствовать тебя на нашей стажировке Лиги Цифровой Экономики.Я буду твоим помощником в изучении SQL. Для тебя того, чтобы начать, укажи своё имя.")

    else:
        await bot.send_message(message.from_user.id, "Поздравляю! Регистрация успешно завершена. Перед началом работы, предлагаю тебе ознакомиться с моим функционалом, для этого введи команду /help", reply_markup=mainMenu)

async def registration_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    if re.fullmatch(r'[А-ЯЁ][а-яё-]+', data['name']) is not None:
        await FSMAdmin.next()
        await message.reply('Введите фамилию')
    else:
        await message.reply('Указаны не корректные данные. Введи фамилию на кириллице, первая буква заглавная.')

async def registration_group(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    if re.fullmatch(r'[А-ЯЁ][а-яё-]+', data['surname']) is not None:
        await FSMAdmin.next()
        await message.reply('Осталось ввести номер группы.')
    else:
        await message.reply('Указаны не корректные данные. Введи имя на кириллице, первая буква заглавная.')


async def registration_db(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['group'] = message.text
    if data['group'].isdigit():
        await db.add_user(message.from_user.id, data['name'], data['surname'], data['group'])
        db.set_notstarted_tasks(message.from_user.id)
        await bot.send_message(message.from_user.id,
                                       f"Поздравляю! {data['surname'].strip()} {data['name'].strip()}, группа № {data['group']}, ты успешно зарегистрирован. Перед началом работы, предлагаю тебе ознакомиться с моим функционалом, для этого введи команду /help",
                                       reply_markup=mainMenu)
        await state.finish()
    else:
        await message.reply('Указаны не корректные данные. Введи целое число.')


async def command_help(message: types.Message):
    """Команда помощи пользователю"""
    await message.reply("""
Мои команды:
/help -- описание всех команд

/start -- регистрация пользователей

/status -- количество и номера оставшихся заданий

/check -- для того, чтобы проверить задание, тебе необходимо отправить файл в формате csv с таким именем : task_<номер задания>.csv К примеру: « task_2.1.csv ». Команда cancel позволит выйти из состояния проверки.

/test -- пройти тест

/cancel -- в случае использования команды - /check, если что-то пошло не так и я завис, введи эту команду
""",
                        reply=False
                        )


async def command_status(message: types.Message):
    """Вывод текущего прогресса пользователя по задачам"""
    result = db.check_status(message.from_user.id)
    res = ''
    for element in result:
        number, status=element[0], element[1]
        res += str(number) + " - " + status + "\n"
    await message.reply(res)


def register_handlers_client(dp: Dispatcher):
    """"Регистрируем клиентские хэндлеры"""
    dp.register_message_handler(command_start, commands=['start'], state=None)
    dp.register_message_handler(registration_surname, state=FSMAdmin.name)
    dp.register_message_handler(registration_group, state=FSMAdmin.surname)
    dp.register_message_handler(registration_db, state=FSMAdmin.group)
    dp.register_message_handler(command_status, commands=['status'])
    dp.register_message_handler(command_help, commands=['help'])


