from .connect import get_connection


def with_cursor(func):
    async def wrapper(*args):
        conn = await get_connection()
        async with conn.cursor() as cursor:
            return await func(cursor, *args)

    return wrapper
