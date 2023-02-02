from aiogram.dispatcher import FSMContext

from ..config import RECIPE_PARAMS_RU
from ..create_logger import logger


def get_chat_id(func):
    async def wrapper(*args, state: FSMContext = None):

        chat_id = args[0]['from']['id']
        if state and await state.get_state():
            return await func(chat_id, *args, state)
        else:
            return await func(chat_id, *args)

    return wrapper


def capitalize_message(index: int = 0):
    def decorator(func):

        async def wrapper(*args, state: FSMContext = None):
            msg = args[index]['text'].capitalize()
            if state and await state.get_state() and await state.get_state() \
                    != 'Category:name':
                return await func(msg, *args, state)
            else:
                return await func(msg, *args)

        return wrapper

    return decorator


def check_what_to_change(func):
    async def wrapper(*args):
        logger.info(args)
        if args[0] in RECIPE_PARAMS_RU:
            return await func(*args)
        else:
            logger.info(args)
            msg = f"Нельзя изменить '{args[0]}'. У рецепта нет такого " \
                  "параметра. Попробуйте ещё раз"
            logger.info(msg)
            await args[1].answer(msg)

    return wrapper
