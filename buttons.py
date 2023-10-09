#создание кнопок для удобного управления ботом
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

main_kb = [
   [KeyboardButton(text ='Показать список всех групп')],
   [KeyboardButton(text = 'Выбрать группу')]
   ]
main1 = ReplyKeyboardMarkup(keyboard = main_kb, resize_keyboard = True)
report1 = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text = 'Отчет', callback_data = 'otchet')]
    ])