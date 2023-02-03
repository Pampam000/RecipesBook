from aiogram.utils import executor

from app.handlers import client, wrong
from app.handlers.admin import cancel, create, update, delete
from .create_bot import dp
from .create_logger import logger
from .db.connect import connect, disconnect

client.register_start_handlers(dp)
cancel.register_handlers(dp)

create.register_handlers(dp)
update.register_handlers(dp)
delete.register_handlers(dp)
client.register_handlers(dp)

wrong.register_handlers(dp)


async def on_startup(_):
    logger.info('Bot started')
    await connect()


async def on_shutdown(_):
    logger.info('Bot stopped')
    await disconnect()


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True,
                           on_startup=on_startup, on_shutdown=on_shutdown)
