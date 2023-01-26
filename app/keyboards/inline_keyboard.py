from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

categories = ('Горячее', 'Выпечка', 'Соусы', 'Салаты', 'Соленья', 'Варенья')
what_to_change = ('Название', 'Категория', 'Фото', 'Ингридиенты', 'Описание')
what_to_change_en = ('name', 'category', 'photo_id', 'ingridients',
                     'description')
english_alias = {x: y for x, y in zip(what_to_change, what_to_change_en)}

inline_kb_category = InlineKeyboardMarkup()
inline_kb_category.row_width = 3

inline_kb_update = InlineKeyboardMarkup()
inline_kb_update.row_width = 3


def create_inline_categories():
    for i in categories:
        inline_kb_category.insert(
            InlineKeyboardButton(text=i, callback_data=i)
        )


def create_inline_update():
    for i in what_to_change:
        inline_kb_update.insert(
            InlineKeyboardButton(text=i, callback_data=i)
        )


create_inline_categories()
create_inline_update()
