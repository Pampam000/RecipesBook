from aiosqlite import Cursor

from app.create_logger import logger
from .services import fsm_start
from ..connect import commit
from ..decorators import with_cursor
from ..schemas import Answer

recipes = 'recipes'
categories = 'categories'


async def update_start(chat_id: int) -> Answer:
    return await fsm_start(chat_id, ('обновление', 'обновлять'))


@with_cursor
async def update(cursor: Cursor, name: str, key: str, value: str) -> str:
    try:

        await cursor.execute(
            f"UPDATE {recipes} SET {key} == ? WHERE name == ?",
            (value, name))
        await commit()
        result_msg = "Рецепт успешно обновлён"
        logger.info(f'{result_msg}: у рeцепта "{name}" изменено поле "{key}".'
                    f' Новое значение: {value}')
        return result_msg
    except Exception as e:
        result_msg = f"Рецепт не обновлён"
        logger.error(result_msg + f"\n Ошибка: {e}")
        return result_msg
