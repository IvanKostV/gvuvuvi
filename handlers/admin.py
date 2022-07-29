from aiogram import Dispatcher
from create_bot import dp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
from requests import get
from create_bot import l_token_name
import json
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types
from create_bot import db, bot, l_token_name
from aiogram.types import ContentTypes, Message
import pandas as pd
import openpyxl


load_dotenv()

ID = None

class FSMAdmin(StatesGroup):
    """Машина состояний"""
    file_test = State()


#получаем id пользователя
async def adm_check_admin_id(message: types.Message):
    global ID
    ID = message.from_user.id
    admin_buttons = ['Помощь', 'Статистика', 'Управление тестами']
    kb = InlineKeyboardMarkup()
    for button in admin_buttons:
        kb.add(InlineKeyboardButton(text=f'{button}', callback_data=f'{button}'))
    await bot.send_message(message.from_user.id, "<b>Команды для администратора:</b>", reply_markup=kb, parse_mode=types.ParseMode.HTML)
    await message.delete()

#help admin
@dp.callback_query_handler(Text('Помощь'))
async def adm_help(callback : types.CallbackQuery):
    await callback.message.answer('Раздел - Управление тестами\n'
                                  'Загрузка теста - отпраить боту тест в соответствии с шаблоном\n'
                                  'Скачать шаблон - Наименование теста в вписать в наименование этого файла ексель. 1 строку не удалять\n' 
                                    'test_id - номер вопроса в тесте, int\n'
                                    "test_question - тело вопроса, обернуть в ''\n"
                                    "test_answers - варинат ответов, каждый новый вариант с новой строки (alt+enter), обренуть в ''\n"
                                    "true_answer - верный номер ответа, int\n"
                                    "test_button - количество варинатов ответа, int\n"
                                  'Активация - при нажатии бот выдаст список неактивированных тестов.\n'
                                  'При нажатии на тест активируется. Срок выполнения теста устанавливается на 3 суток.\n'
                                  'Деактивация - при нажатии бот выдаст список активированных тестов.\n'
                                  'При нажатии на тест деактивируется. Срок выполнения сбрасывается.')
    await callback.answer()

# Меню статистики
@ dp.callback_query_handler(Text('Статистика'))
async def adm_statistics(callback: types.CallbackQuery):
    await callback.answer('Здесь пока ничего нет')
    await callback.answer()

# Меню управления тестами
@ dp.callback_query_handler(Text('Управление тестами'))
async def manage_test(callback: types.CallbackQuery):
    inline_buttons = ['Загрузка теста', 'Скачать шаблон', 'Активация', 'Деактивация']
    kb = InlineKeyboardMarkup()
    for button in inline_buttons:
        kb.add(InlineKeyboardButton(text=f'{button}', callback_data=f'{button}'))
    await callback.message.answer("<b>Управление тестами:</b>", reply_markup=kb,
                               parse_mode=types.ParseMode.HTML)
    await callback.answer()

# Загрузка теста
@ dp.callback_query_handler(Text('Скачать шаблон'))
async def adm_statistics(callback: types.CallbackQuery):
    await callback.message.reply_document(open('test_template/pattern/pattern_test.xlsx', 'rb'))
    await callback.answer()

# Загрузка теста
@ dp.callback_query_handler(Text('Загрузка теста'), state=None)
async def adm_statistics(callback: types.CallbackQuery):
    await FSMAdmin.file_test.set()
    await callback.message.reply('Загрузите тест в формате .xlsx')

# Загрузка теста
async def download_test(message: Message, state: FSMContext):
    await message.answer('Началось')
    try:
        file_id =  message.document.file_id
        response = get("https://api.telegram.org/bot{token}/getFile?file_id={file_id}".format(token=os.environ.get(l_token_name),
                                                                                              file_id=file_id))
        resp_dict = json.loads(response.text)
        file_name = message.document.file_name
        file_path = resp_dict['result']['file_path']
        destination = r"./test_template/{file_name}".format(file_name=file_name)
        await bot.download_file(file_path, destination=destination)
        temp_test_list = pd.read_excel(destination[2:])
        test_list = temp_test_list.to_dict(orient='records')
        # Определяем тест код
        max_code = await db.max_test_code()
        if max_code:
            temp_num_code = str(int(max_code[-3:]) + 1)
            if len(temp_num_code) == 1:
                temp_num_code = '0' + temp_num_code
            if len(temp_num_code) == 2:
                temp_num_code = '0' + temp_num_code
            max_code = max_code[:-3] + temp_num_code
        else:
            max_code = 'Test_000'
        # Выбираем вопросы на тест
        test_to_sql = ''
        for row in test_list:
            test_to_sql += '('
            temp = ''
            for item in row.values():
                temp += str(item) + ', '
            test_to_sql += temp + "'" + max_code + "'" + '), '
        await db.upload_test(file_name[:-5], test_to_sql[:-2], max_code)
        os.unlink(f"test_template/{file_name}")
        await state.finish()
        await message.answer(f'Тест "{file_name[:-5]}" успешно загружен')
    except:
        await message.answer("Что-то пошло не так. Попробуй еще раз")
        await state.finish()

#Вывод списка тестов для активации
@dp.callback_query_handler(Text('Активация'))
async def adm_activate(callback : types.CallbackQuery):
    inline_buttons = list(await db.adm_activate_test())
    kb = InlineKeyboardMarkup()
    for button in inline_buttons:
        test_name, test_code = button
        kb.add(InlineKeyboardButton(text=f'{test_name}', callback_data=f'activate {str(test_code)}'))
    await callback.message.answer("<b>Выберите тест для активации:</b>", reply_markup=kb, parse_mode=types.ParseMode.HTML)
    await callback.answer()

@dp.callback_query_handler(Text(startswith='activate'))
async def adm_set_Y(callback : types.CallbackQuery):
    try:
        await db.adm_test_to_Y(callback.data.split()[1])
        await callback.answer("Тест активирован!", show_alert=True)
    except:
        await callback.answer("Oтсутствует доступ к базе данных. Попробуйте позже.", show_alert=True)
    await callback.answer()

#Вывод списка тестов для деактивации
@dp.callback_query_handler(Text('Деактивация'))
async def adm_deactivate(callback : types.CallbackQuery):
    inline_buttons = list(await db.adm_deactivate_test())
    kb = InlineKeyboardMarkup()
    for button in inline_buttons:
        test_name, test_code = button
        kb.add(InlineKeyboardButton(text=f'{test_name}', callback_data=f'deactivate {test_code}'))
    await callback.message.answer("<b>Выберите тест для деактивации:</b>", reply_markup=kb, parse_mode=types.ParseMode.HTML)
    await callback.answer()

@dp.callback_query_handler(Text(startswith='deactivate'))
async def adm_set_N(callback : types.CallbackQuery):
    try:
        await db.adm_test_to_N(callback.data.split()[1])
        await callback.answer("Тест деактивирован!", show_alert=True)
    except:
        await callback.answer("Oтсутствует доступ к базе данных. Попробуйте позже.", show_alert=True)
    await callback.answer()

def register_handlers_admin(dp: Dispatcher):
    """"Регистрируем клиентские хэндлеры"""
    dp.register_message_handler(adm_check_admin_id, commands=['admin'], is_chat_admin = True)
    dp.register_message_handler(download_test, content_types=ContentTypes.DOCUMENT, state=FSMAdmin.file_test)