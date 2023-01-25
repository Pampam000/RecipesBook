from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.create_logger import logger
from app.keyboards.keyboard import admin_keyboard


async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        await message.answer("Нечего отменять")
        logger.info('Пользователь нажал кнопку "Отмена" НЕ находясь ни в одном'
                    ' конечном автомате')
        return

    logger.info('Пользователь нажал кнопку "Отмена" находясь в конечном'
                f' автомате: {current_state}')
    msg = 'Действие отменено'
    await state.finish()
    await message.answer(msg, reply_markup=admin_keyboard)
    logger.info(msg)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel, text=['Отмена'], state="*")
