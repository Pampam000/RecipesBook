from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from ..config import ADMINS_ID
from ..create_bot import bot
from ..create_logger import logger
from ..db import crud
from ..keyboards.inline_keyboard import inline_kb_category, inline_kb_update
from ..keyboards.keyboard import cancel_keyboard, admin_keyboard


class Load(StatesGroup):
    name = State()
    category = State()
    ingridients = State()
    description = State()
    photo = State()


class Delete(StatesGroup):
    name = State()


class Update(StatesGroup):
    name = State()
    what_to_change = State()
    new_value = State()


async def load_start(message: Message):
    user_id = message.from_user.id
    if str(user_id) in ADMINS_ID:

        await Load.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
        logger.info(f'Пользователь с id {user_id} является админом и начал '
                    'загрузку рецепта')
    else:
        await message.reply("Вы не можете загружать рецепты")
        logger.info(f'Пользователь с id {user_id} НЕ является админом и хотел '
                    'начать загрузку рецепта')


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


async def set_name(message: Message, state: FSMContext):
    logger.info(f'Пользователь хочет создать рецепт: {message.text}')
    if await crud.get_one_recipe(message.text):
        await message.answer(f"Рецепт c названием: '{message.text}' уже "
                             f"существует, введите другое название",
                             reply_markup=cancel_keyboard)
        logger.info('Такой рецепт уже существует')
    else:
        async with state.proxy() as data:
            data['name'] = message.text.capitalize()
            await Load.next()
            await message.answer("Укажите категорию",
                                 reply_markup=inline_kb_category)
            logger.info(f'Пользователь успешно указал название рецепта: '
                        f'{message.text}')


async def choose_category(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = callback.data
        logger.info(
            f"Пользователь выбрал категорию '{callback.data}' для рецепта: "
            f" {data['name']}")
    await Load.next()
    await callback.message.answer("Введите список ингридиентов",
                                  reply_markup=cancel_keyboard)
    await callback.answer()


async def set_ingridients(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ingridients'] = message.text
        logger.info(
            f"Пользователь указал ингридиенты '{message.text}' для рецепта: "
            f" {data['name']}")
    await Load.next()
    await message.answer("Введите описание")


async def set_description(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        logger.info(
            f"Пользователь указал описание '{message.text}' для рецепта: "
            f" {data['name']}")
    await Load.next()
    await message.answer("Загрузите фото")


async def set_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        photo_id = message.photo[-1].file_id
        data['photo_id'] = photo_id
        logger.info(
            f"Пользователь установил фото '{photo_id}' для рецепта: "
            f" {data['name']}")
        msg = await crud.add_to_db(data)
        await message.answer(msg, reply_markup=admin_keyboard)
    logger.info(f"Конечный автомат {await state.get_state()} закончен")
    await state.finish()


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


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(load_start, text=['Загрузить'], state=None)
    dp.register_message_handler(cancel, text=['Отмена'], state="*")
    dp.register_message_handler(set_name, state=Load.name)
    dp.register_callback_query_handler(choose_category,
                                       state=Load.category)
    dp.register_message_handler(set_ingridients, state=Load.ingridients)
    dp.register_message_handler(set_description, state=Load.description)
    dp.register_message_handler(set_photo, content_types=['photo'],
                                state=Load.photo)

    dp.register_message_handler(delete_start, text=['Удалить рецепт'],
                                state=None)
    dp.register_message_handler(delete, state=Delete.name)

    dp.register_message_handler(update_start, text=['Обновить рецепт'],
                                state=None)
    dp.register_message_handler(update, state=Update.name)
    dp.register_callback_query_handler(choose, state=Update.what_to_change)
    dp.register_message_handler(up, content_types=["text"],
                                state=Update.new_value)
    dp.register_message_handler(up_photo, content_types=["photo"],
                                state=Update.new_value)
    dp.register_callback_query_handler(up_category, state=Update.new_value)
