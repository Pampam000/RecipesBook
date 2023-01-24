from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start = KeyboardButton('/start')
load = KeyboardButton('Загрузить')
get_all = KeyboardButton('Список рецептов')
category = KeyboardButton('Рецепты по категориям')

update = KeyboardButton('Обновить рецепт')
delete = KeyboardButton('Удалить рецепт')
cancel = KeyboardButton('Отмена')

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
admin_keyboard.row(start, get_all, category).row(load, update, delete)

client_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
client_keyboard.add(start, get_all, category)

cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add(cancel, start)

