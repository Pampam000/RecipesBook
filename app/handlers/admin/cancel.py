from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.create_logger import logger
from ..decorators import get_chat_id
from ...db import crud


@get_chat_id
async def cancel(chat_id: int, message: Message, state: FSMContext = None):
    if not state:
        await message.answer("Нечего отменять")
        logger.info(f'Пользователь {chat_id} нажал кнопку "Отмена" НЕ '
                    'находясь ни в одном конечном автомате')
        return
    current_state = await state.get_state()
    if not current_state:
        await message.answer("Нечего отменять")
        logger.info(f'Пользователь {chat_id} нажал кнопку "Отмена" НЕ '
                    'находясь ни в одном конечном автомате')
        return

    logger.info(f'Пользователь {chat_id} нажал кнопку "Отмена" находясь в '
                f'конечном автомате: {current_state}')
    msg = 'Действие отменено'
    await state.finish()
    await message.answer(msg,
                         reply_markup=await crud.get_user_keyboard(chat_id))
    logger.info(msg)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel, text=['Отмена', 'отмена'], state="*")
