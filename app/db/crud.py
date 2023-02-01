import aiosqlite as sq
from typing import NamedTuple

from app.create_logger import logger

recipes = 'recipes'
categories = 'categories'


async def connect_to_db():
    global connection
    connection = await sq.connect('recipes_book.db')
    logger.info("Connected to db")


async def disconnect():
    global connection
    await connection.close()
    logger.info("Disconnect db")


class Recipe(NamedTuple):
    name: str
    category: str
    ingridients: str
    description: str
    photo_id: str


async def add_to_db(data: dict) -> str:
    cursor = await connection.cursor()
    try:

        await cursor.execute("PRAGMA foreign_keys = ON;")
        await cursor.execute(
            "INSERT INTO recipes VALUES(?,?,?,?,?)", tuple(data.values()))
        await connection.commit()
        result_msg = 'Рецепт успешно добавлен'
        logger.info(f'{result_msg}: {Recipe(*data.values())}')
        return result_msg
    except sq.IntegrityError as ex:
        logger.info(ex)
        logger.info(data.values())
        await cursor.execute("INSERT INTO categories VALUES(?)",
                             (list(data.values())[1],))
        await connection.commit()
        return await add_to_db(data)
    except Exception as e:
        result_msg = f'При добавлении рецепта произошла ошибка: {e}'
        logger.error(result_msg)
        return result_msg
    finally:
        await cursor.close()


async def get_all() -> list:
    async with connection.cursor() as cursor:
        await cursor.execute(f"SELECT * FROM {recipes}")
        result = [Recipe(*x) for x in await cursor.fetchall()]
        logger.info(f'Получены все рецепты: {result}')
        return result


async def get_one_recipe(name: str) -> Recipe | None:
    name = name.capitalize()
    async with connection.cursor() as cursor:
        await cursor.execute(
            f"SELECT * from {recipes} WHERE name == ?", (name,))
        if db_result := await cursor.fetchone():

            result = Recipe(*db_result)
            logger.info(f"Рецепт {result} найден в БД")
            return result

        else:
            logger.info(f"Рецепт '{name}' не найден в БД")
            return


async def get_all_in_category(category: str) -> list[Recipe]:
    async with connection.cursor() as cursor:
        await cursor.execute(
            f"SELECT * FROM {recipes} WHERE category == ?", (category,))
        result = [Recipe(*x) for x in await cursor.fetchall()]
        logger.info(f"Рецепты в категории '{category}': {result}")
        return result


async def delete_recipe(name: str) -> bool | None:
    async with connection.cursor() as cursor:
        if recipe := await get_one_recipe(name):
            await cursor.execute(
                "DELETE FROM recipes WHERE name == ?", (recipe.name,))
            await connection.commit()

            logger.info(f'Рецепт удалён успешно: {Recipe(*recipe)}')
            return True


async def update(name: str, key: str, value: str):
    cursor = await connection.cursor()
    try:

        await cursor.execute(
            f"UPDATE {recipes} SET {key} == ? WHERE name == ?",
            (value, name))
        await connection.commit()
        result_msg = "Рецепт успешно обновлён"
        logger.info(f'{result_msg}: у рeцепта "{name}" изменено поле "{key}".'
                    f' Новое значение: {value}')
        return result_msg
    except Exception as e:
        result_msg = f"Рецепт не обновлён\n Ошибка: {e}"
        logger.error(result_msg)
        return result_msg
    finally:
        await cursor.close()


#async def get_all_categories():
#    async with connection.cursor() as cursor:
#        await cursor.execute(
#            f"SELECT DISTINCT category FROM {recipes}")
#        logger.info(await cursor.fetchall())
#        await cursor.execute(f"SELECT * FROM {categories}")
#        logger.info(await cursor.fetchall())
