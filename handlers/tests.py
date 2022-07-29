from aiogram import types, Dispatcher
from create_bot import  bot, db, dp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text

#Собираем в список все доступные тесты: тест активирован, со дня активации прошло менее 3 дней, пользователь не потратил 2 попытки на прохождение
async def command_test(message: types.Message):
    await db.set_notstarted_test(message.from_user.id) #заполняем таблицы фактов данными пользователя, если они не начаты
    inline_buttons = list(await db.choiсe_list_test(message.from_user.id))
    kb = InlineKeyboardMarkup()
    for button in inline_buttons:
        test_name, test_code = button
        kb.add(InlineKeyboardButton(text=f'{test_name}', callback_data=f'test {test_code}'))
    await bot.send_message(message.from_user.id, "<b>Выберите тест:</b>", reply_markup=kb, parse_mode=types.ParseMode.HTML)

#Кнопка начать тест
@dp.callback_query_handler(Text(startswith='test'))
async def start_test(callback : types.CallbackQuery):
    test_code = callback.data.split()[1]
    if await db.check_status_test(callback.from_user.id, test_code): #Проверка статуса теста
        test_name = await db.test_name(test_code)
        num_try = await db.num_try(callback.from_user.id, test_code)
        await callback.message.answer(f'Начать прохождение теста по теме:\n<b><i>{test_name}</i></b>.\nНа прохождение теста дается 2 попытки, на каждую попытку 2 часа.', parse_mode=types.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(). \
                                      add(InlineKeyboardButton(text='Начать тест!', callback_data=f'question {test_code} {num_try}')))
        await db.set_start_date_try(callback.from_user.id, test_code, num_try)
    else:
        await callback.answer('Тест завершен или истекло время на прохождение теста.', show_alert=True)
    await callback.answer()

# Вывод вопроса и результата
@dp.callback_query_handler(Text(startswith='question'))
async def question_test(callback : types.CallbackQuery):
    test_code, num_try = callback.data.split()[1:]
    if num_try:
        list_question = await db.random_question(callback.from_user.id, test_code, num_try)
        if list_question:
            test_id, question, answers, true_answer, num_button, test_code = list(list_question)[0]
            kb = InlineKeyboardMarkup()
            for num in range(1, num_button + 1):
                kb.add(InlineKeyboardButton(text=f'Вариант {num}',
                                        callback_data=f'answer {test_code} {test_id} {num} {num_try}'))
            await callback.message.answer(f'<b>{question}</b> \n\n {answers}', parse_mode=types.ParseMode.HTML, reply_markup=kb)
        else:
            await callback.message.answer('Подтвердите выбранные варианты.', reply_markup=InlineKeyboardMarkup(). \
                                                                    add(InlineKeyboardButton(text='Commit', callback_data=f'commit {test_code} {num_try}')))
    else:
        await callback.answer('Тест завершен.', show_alert=True)
    await callback.answer()

# проверка ответа и изменение статуса
@dp.callback_query_handler(Text(startswith='answer'))
async def answer_to_sql(callback : types.CallbackQuery):
    test_code, test_id, num, num_try = callback.data.split()[1:]
    if await db.check_status_test(callback.from_user.id, test_code) and await db.check_time_try(callback.from_user.id, test_code, num_try): #Проверка статуса теста
        if num_try == '1':
            if await db.check_status_try_1(callback.from_user.id, test_code): #Проверка статуса 1 попытки
                await db.record_answer(callback.from_user.id, test_code, test_id, num_try, num)
                amount_list = list(await db.amount_answer(callback.from_user.id, test_code, num_try))
                amount_total = amount_list[0][0]
                amount_passed = amount_list[1][0]
                await callback.message.answer(f'Вариант {num} принят. Прогресс: {amount_passed} из {amount_total}.' ,reply_markup=InlineKeyboardMarkup().\
                                  add(InlineKeyboardButton(text='Следующий вопрос', callback_data=f'question {test_code} {num_try}')))
            else:
                await callback.answer('Тест завершен. Попробуйте пройти тест еще раз.', show_alert=True)
        else:
            await db.record_answer(callback.from_user.id, test_code, test_id, num_try, num)
            amount_list = list(await db.amount_answer(callback.from_user.id, test_code, num_try))
            amount_total = amount_list[0][0]
            amount_passed = amount_list[1][0]
            await callback.message.answer(f'Вариант {num} принят. Прогресс: {amount_passed} из {amount_total}.',
                                              reply_markup=InlineKeyboardMarkup(). \
                                              add(InlineKeyboardButton(text='Следующий вопрос',
                                                                       callback_data=f'question {test_code} {num_try}')))
    else:
        await db.commit_test(callback.from_user.id, test_code, num_try)
        await callback.answer('Тест завершен или истекло время на прохождение теста.', show_alert=True)
    await callback.answer()

# Кнопка commit
@dp.callback_query_handler(Text(startswith='commit'))
async def commit_test(callback : types.CallbackQuery):
    test_code, num_try = callback.data.split()[1:]
    await db.commit_test(callback.from_user.id, test_code, num_try)
    result, amount = list(await db.print_result(callback.from_user.id, test_code, num_try))[0]
    await callback.message.answer(f'Попытка №{num_try}.Верных ответов: {result} из {amount}.')
    if result == amount or num_try == '2':
        best_result, surname, name, name_test = list(await db.print_total_result(callback.from_user.id, test_code))[0]
        await callback.message.answer(f'{name_test}\n{surname} {name}.\nИтоговый результат: {best_result} из {amount}.')
    await callback.answer()

def register_handlers_tests(dp: Dispatcher):
    """Регистрируем хэндлеры"""
    dp.register_message_handler(command_test, commands=['test'])
    # dp.register_message_handler(start_test)
    # dp.callback_query_handler(question_test, Text(startswith='question'))
    # dp.callback_query_handler(answer_to_sql, Text(startswith='answer'))
    # dp.callback_query_handler(continue_test, Text='continue')