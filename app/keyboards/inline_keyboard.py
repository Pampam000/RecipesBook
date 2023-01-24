from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


hot_dish = InlineKeyboardButton(text='Горячее', callback_data='Горячее')
backery = InlineKeyboardButton(text='Выпечка', callback_data='Выпечка')
sauce = InlineKeyboardButton(text='Соусы', callback_data='Соусы')
salad = InlineKeyboardButton(text='Салаты', callback_data='Салаты')
sol = InlineKeyboardButton(text='Соленья', callback_data='Соленья')
var = InlineKeyboardButton(text='Варенья', callback_data='Варенья')

inline_kb_category = InlineKeyboardMarkup()
inline_kb_category.row(hot_dish, backery).row(sauce, salad).row(sol, var)


name = InlineKeyboardButton(text='Название', callback_data='name')
category = InlineKeyboardButton(text='Категория', callback_data='category')
ingridients = InlineKeyboardButton(text='Ингридиенты',
                                   callback_data='ingridients')
description = InlineKeyboardButton(text='Описание',
                                   callback_data='description')
photo = InlineKeyboardButton(text='Фото', callback_data='photo_id')

inline_kb_update = InlineKeyboardMarkup()
inline_kb_update.row(name, category, photo).row(ingridients, description)
