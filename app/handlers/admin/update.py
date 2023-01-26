from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import Message, CallbackQuery

from app.config import ADMINS_ID
from app.create_bot import bot
from app.create_logger import logger
from app.db import crud
from app.keyboards.inline_keyboard import inline_kb_category, \
    inline_kb_update, english_alias, what_to_change
from app.keyboards.keyboard import cancel_keyboard, admin_keyboard
from ..states_groups import Update


async def update_start(message: Message):
    user_id = message.from_user.id
    if str(user_id) in ADMINS_ID:
        await Update.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
        logger.info(f'Пользователь {user_id} является админом и начал '
                    'обновление рецепта')
    else:
        await message.reply("Вы не можете обновлять рецепты")
        logger.info(f'Пользователь {user_id} НЕ является админом и хотел '
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


async def choose_what_to_change(message: Message, msg: str,
                                state: FSMContext):
    logger.info(f'Пользователь хочет изменить: {msg}')
    if msg in what_to_change:
        async with state.proxy() as data:
            data['what_to_change'] = english_alias[msg]
        if msg == 'Категория':
            await message.answer("На какую категорию заменить?",
                                 reply_markup=inline_kb_category)
            await Update.change_category.set()
        elif msg == 'Фото':
            await message.answer(f"Загрузите новое фото",
                                 reply_markup=cancel_keyboard)
            await Update.change_photo.set()
        else:
            await message.answer(f"Введите новое значение",
                                 reply_markup=cancel_keyboard)
            await Update.change_text.set()
    else:
        await message.answer(f"Нельзя изменить '{msg}'. У рецепта нет такого"
                             f" параметра. Попробуйте ещё раз")


async def choose(callback: CallbackQuery, state: FSMContext):
    clbck_data = callback.data
    await choose_what_to_change(callback.message, clbck_data, state)
    await callback.answer()


async def choos(message: Message, state: FSMContext):
    msg_text = message.text.capitalize()
    await choose_what_to_change(message, msg_text, state)


async def set_new_value(message: Message, state: FSMContext,
                        data: FSMContextProxy):
    logger.info(f'Новое значение: {data["value"]}')
    msg = await crud.update(name=data['name'], key=data['what_to_change'],
                            value=data['value'])
    await message.answer(msg, reply_markup=admin_keyboard)
    logger.info(f"Конечный автомат {await state.get_state()} закончен")
    await state.finish()


async def up(message: Message, state: FSMContext):

    async with state.proxy() as data:
        if data['what_to_change'] == 'name':
            if recipe := await crud.get_one_recipe(message.text.capitalize()):
                await message.answer(f"Рецепт с названием  '{recipe.name}' "
                                     f"уже существует. Введите другое "
                                     f"название.")
                logger.info(f"Рецепт '{recipe.name}'уже существует")
            else:
                data['value'] = message.text.capitalize()
                await set_new_value(message, state, data)
        else:

            data['value'] = message.text.capitalize()
            await set_new_value(message, state, data)


async def up_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.photo[-1].file_id
        await set_new_value(message, state, data)


async def up_category(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = callback.data.capitalize()
        await set_new_value(callback.message, state, data)
        await callback.answer()


async def category_up(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.text.capitalize()
        await set_new_value(message, state, data)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(update_start, text='Обновить рецепт',
                                state=None)
    dp.register_message_handler(update, state=Update.name)
    dp.register_callback_query_handler(choose, state=Update.what_to_change)
    dp.register_message_handler(choos, state=Update.what_to_change)
    dp.register_message_handler(up, content_types="text",
                                state=Update.change_text)
    dp.register_message_handler(up_photo, content_types="photo",
                                state=Update.change_photo)
    dp.register_callback_query_handler(up_category,
                                       state=Update.change_category)
    dp.register_message_handler(category_up, state=Update.change_category)
