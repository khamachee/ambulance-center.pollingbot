from aiogram import Bot
from bot.dispatcher import dispatcher
from bot.settings import bot
from aiogram.types import ChatMemberUpdated 
from config.settings import ROOT_USER_ID




@dispatcher.my_chat_member()
async def onChatMemberUpdated(update: ChatMemberUpdated):
    await bot.send_message(
        chat_id=ROOT_USER_ID,
        text=f"ADDED TO NODE  TYPE-{update.chat.type.upper()} /// ID: {update.chat.id}"
    )


