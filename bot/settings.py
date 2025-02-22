import os 
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
print(BOT_API_TOKEN)
bot = Bot(
    token=BOT_API_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

