import aiosqlite as sq

from app.create_logger import logger


async def connect():
    global connection
    connection = await sq.connect('recipes_book.db')
    logger.info("Connected to db")
    logger.info(connection)
    logger.info(id(connection))


async def disconnect():
    global connection
    await connection.close()
    logger.info("Disconnect db")


async def get_connection():
    global connection
    return connection


async def commit():
    global connection
    await connection.commit()
