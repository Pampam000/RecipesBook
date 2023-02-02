from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..config import RECIPE_PARAMS_RU, BASE_CATEGORIES


def create_inline_keyboard(button_names: tuple, row_width: int = 3):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = row_width
    for i in button_names:
        keyboard.insert(InlineKeyboardButton(text=i, callback_data=i))
    return keyboard


inline_kb_category = create_inline_keyboard(BASE_CATEGORIES)
inline_kb_update = create_inline_keyboard(RECIPE_PARAMS_RU)
