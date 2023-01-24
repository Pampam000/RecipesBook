from aiogram.utils import executor
from create_bot import dp
from app.handlers import client, admin
#from db.crud import start_db
admin.register_handlers(dp)
client.register_handlers(dp)


async def on_startup(_):
    print('Bot started')
    #start_db()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


