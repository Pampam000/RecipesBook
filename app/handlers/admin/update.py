from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from app.config import ADMINS_ID
from app.create_bot import bot, dp
from app.create_logger import logger
from app.db import crud
from app.keyboards.inline_keyboard import inline_kb_category, inline_kb_update
from app.keyboards.keyboard import cancel_keyboard, admin_keyboard


class Update(StatesGroup):
    name = State()
    what_to_change = State()
    new_value = State()


async def update_start(message: Message):
    user_id = message.from_user.id
    if str(user_id) in ADMINS_ID:
        await Update.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
        logger.info(f'Пользователь с id {user_id} является админом и начал '
                    'обновление рецепта')
    else:
        await message.reply("Вы не можете обновлять рецепты")
        logger.info(f'Пользователь с id {user_id} НЕ является админом и хотел '
                    'начать обновление рецепта')


async def update(message: Message, state: FSMContext):
    logger.info(f'Пользователь хочет обновить рецепт: {message.text}')

    if recipe := await crud.get_one_recipe(message.text.capitalize()):
        async with state.proxy() as data:
            data['name'] = recipe.name
        await bot.send_photo(message.from_user.id, recipe.photo_id,
                             f'{recipe.name} '
                             f'({recipe.category})\n\n'
                             f'{recipe.ingridients}\n\n'
                             f'{recipe.description}')

        await message.answer("Что будем менять?",
                             reply_markup=inline_kb_update)
        await Update.next()
    else:
        await message.answer(
            'Нет рецепта с таким названием')


async def choose(callback: CallbackQuery, state: FSMContext):
    logger.info(f'Пользователь хочет изменить: {callback.data}')
    async with state.proxy() as data:
        data['what_to_change'] = callback.data

    if 'category' in callback.data:
        await callback.message.answer("На какую категорию заменить?",
                                      reply_markup=inline_kb_category)
    elif 'photo' in callback.data:
        await callback.message.answer(f"Загрузите новое фото",
                                      reply_markup=cancel_keyboard)
    else:
        await callback.message.answer(f"Введите новое значение",
                                      reply_markup=cancel_keyboard)
    await Update.next()
    await callback.answer()


async def up(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.text.capitalize()
        logger.info(f'Новое значение: {data["value"]}')
        msg = await crud.update(name=data['name'], key=data['what_to_change'],
                                value=data['value'])
        await message.answer(msg, reply_markup=admin_keyboard)
    logger.info(f"Конечный автомат {await state.get_state()} закончен")
    await state.finish()


async def up_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.photo[-1].file_id

        msg = await crud.update(name=data['name'], key=data['what_to_change'],
                                value=data['value'])
        await message.answer(msg, reply_markup=admin_keyboard)
        logger.info(f"Конечный автомат {await state.get_state()} закончен")
        await state.finish()


async def up_category(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = callback.data.capitalize()
        msg = await crud.update(name=data['name'], key=data['what_to_change'],
                                value=data['value'])
        await callback.message.answer(msg, reply_markup=admin_keyboard)
        logger.info(f"Конечный автомат {await state.get_state()} закончен")
        await state.finish()
        await callback.answer()


def register_handlers():
    dp.register_message_handler(update_start, text=['Обновить рецепт'],
                                state=None)
    dp.register_message_handler(update, state=Update.name)
    dp.register_callback_query_handler(choose, state=Update.what_to_change)
    dp.register_message_handler(up, content_types=["text"],
                                state=Update.new_value)
    dp.register_message_handler(up_photo, content_types=["photo"],
                                state=Update.new_value)
    dp.register_callback_query_handler(up_category, state=Update.new_value)
