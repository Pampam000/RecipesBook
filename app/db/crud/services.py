from aiogram.types import ReplyKeyboardMarkup
from aiosqlite import Cursor

from app.create_logger import logger
from ..decorators import with_cursor
from ..schemas import Answer
from ...config import ADMINS_ID
from ...keyboards.keyboard import admin_keyboard, client_keyboard, \
    cancel_keyboard

recipes = 'recipes'
categories = 'categories'


async def check_if_user_is_admin(chat_id: int) -> bool:
    return True if str(chat_id) in ADMINS_ID else False


async def get_user_keyboard(chat_id: int) -> ReplyKeyboardMarkup:
    return admin_keyboard if await check_if_user_is_admin(chat_id) else \
        client_keyboard


@with_cursor
async def check_category_in_db(cursor: Cursor, category: str) -> bool:
    await cursor.execute(
        f"SELECT name FROM {categories} WHERE name == ?", (category,))
    if await cursor.fetchone():
        logger.info(f"Категория {category} найдена в БД")
        return True
    else:
        logger.info(f"Категория {category} НЕ найдена в БД")
        return False


async def fsm_start(chat_id: int, actions: tuple[str]):
    if await check_if_user_is_admin(chat_id):
        logger.info(f'Пользователь {chat_id} является админом и начал '
                    f'{actions[0]} рецепта')
        return Answer(text="Введите название",
                      reply_markup=cancel_keyboard, go_next=True)
    else:
        logger.info(f'Пользователь {chat_id} НЕ является админом и хотел '
                    f'начать {actions[0]} рецепта')
        return Answer(f"Вы не можете {actions[1]} рецепты")
