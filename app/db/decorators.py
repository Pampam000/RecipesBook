from .connect import get_connection
from ..create_logger import logger


def with_cursor(func):
    async def wrapper(*args):
        conn = await get_connection()
        logger.info(id(conn))
        async with conn.cursor() as cursor:
            return await func(cursor, *args)

    return wrapper
