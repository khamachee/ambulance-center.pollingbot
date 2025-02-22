import os 
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

django.setup()

import asyncio
import traceback
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

from bot.settings import bot
from bot.dispatcher import dispatcher
from bot.handlers import * 

async def start_bot():
    try:
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dispatcher.start_polling(bot)
    except Exception:
        print(traceback.format_exc())
        await bot.session.close()
asyncio.run(start_bot())
