from aiogram.utils import executor

from app.handlers import client
from app.handlers.admin import cancel, create, update, delete
from create_bot import dp
from create_logger import logger

cancel.register_handlers()
create.register_handlers()
update.register_handlers()
delete.register_handlers()
client.register_handlers()


async def on_startup(_):
    logger.info('Bot started')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
