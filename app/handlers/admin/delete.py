from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message

from app.config import ADMINS_ID
from app.create_logger import logger
from app.db import crud
from app.keyboards.keyboard import cancel_keyboard, admin_keyboard


class Delete(StatesGroup):
    name = State()


async def delete_start(message: Message):
    user_id = message.from_user.id
    if str() in ADMINS_ID:
        await Delete.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
        logger.info(f'Пользователь с id {user_id} является админом и начал '
                    'удаление рецепта')
    else:
        await message.reply("Вы не можете удалять рецепты")
        logger.info(f'Пользователь с id {user_id} НЕ является админом и хотел '
                    'начать удаление рецепта')


async def delete(message: Message, state: FSMContext):
    logger.info(f'Пользователь хочет удалить рецепт: {message.text}')
    if await crud.delete_recipe(message.text):

        await message.answer(
            f"Рецепт '{message.text}' удалён успешно",
            reply_markup=admin_keyboard)
        logger.info(f"Конечный автомат {await state.get_state()} закончен")
        await state.finish()

    else:
        msg = f"Рецепт '{message.text}' не найден. Попробуйте ещё раз."
        await message.answer(msg, reply_markup=cancel_keyboard)
        logger.info(msg)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(delete_start, text=['Удалить рецепт'],
                                state=None)
    dp.register_message_handler(delete, state=Delete.name)
