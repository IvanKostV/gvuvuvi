from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

"""Клавиатура клиента"""
btn_check = KeyboardButton("/check")
btn_status = KeyboardButton("/status")
btn_help = KeyboardButton("/help")
btn_test = KeyboardButton("/test")

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
mainMenu.row(btn_help, btn_check, btn_test, btn_status)