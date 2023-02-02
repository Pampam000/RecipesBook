from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.create_logger import logger
from app.db import crud
from ..decorators import get_chat_id, capitalize_message
from ..states_groups import Delete


@get_chat_id
async def delete_start(chat_id: int, message: Message):
    result = await crud.delete_start(chat_id)
    if result.go_next:

        await Delete.name.set()
        await message.answer(**await result.as_tg_answer())
    else:
        await message.reply(result.text)


@get_chat_id
@capitalize_message(1)
async def delete(msg_text: str, chat_id: int, message: Message,
                 state: FSMContext):
    logger.info(f'Пользователь {chat_id} хочет удалить рецепт: {msg_text}')
    result = await crud.delete_recipe_if_exists(msg_text)

    if result.go_next:
        await message.answer(**await result.as_tg_answer())
        logger.info(f"Конечный автомат {await state.get_state()} закончен")
        await state.finish()

    else:
        await message.answer(**await result.as_tg_answer())


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(delete_start, text='Удалить рецепт',
                                state=None)
    dp.register_message_handler(delete, state=Delete.name)
