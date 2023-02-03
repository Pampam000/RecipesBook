from aiogram.types import ReplyKeyboardMarkup
from aiosqlite import Cursor

from app.create_logger import logger
from ..decorators import with_cursor
from ..schemas import Answer
from ...config import ADMINS_ID, BASE_CATEGORIES
from ...keyboards.inline_keyboard import create_inline_keyboard
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
async def create_inline_kb_categories(cursor: Cursor):

    await cursor.execute(
        f"SELECT DISTINCT category FROM {recipes}")
    db_result = [x[0] for x in await cursor.fetchall()]

    result = BASE_CATEGORIES + [x for x in db_result if x not in
                                BASE_CATEGORIES]

    if len(result) % 3 == 0 or len(result) % 3 == 2:
        return create_inline_keyboard(result)
    else:
        return create_inline_keyboard(result, 2)
@with_cursor
async def check_category_in_db(cursor: Cursor, category: str) -> bool:
    if category in BASE_CATEGORIES:
        logger.info(f"Категория {category} найдена в БД")
        return True
    await cursor.execute(
        f"SELECT category FROM {recipes} WHERE category == ? LIMIT 1",
        (category,))
    
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
