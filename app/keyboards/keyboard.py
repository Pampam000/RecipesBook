from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..config import ADMIN_BUTTONS, USER_BUTTONS, CANCEL_BUTTONS


def create_keyboard(buttons_rows: list[list]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in buttons_rows:
        keyboard.row(*[KeyboardButton(text=x) for x in row])
    return keyboard


admin_keyboard = create_keyboard(ADMIN_BUTTONS)

client_keyboard = create_keyboard(USER_BUTTONS)

cancel_keyboard = create_keyboard(CANCEL_BUTTONS)
