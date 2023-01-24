from aiogram.utils import executor

from app.handlers import client, admin
from create_bot import dp
from create_logger import logger

admin.register_handlers(dp)
client.register_handlers(dp)


async def on_startup(_):
    logger.info('Bot started')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
