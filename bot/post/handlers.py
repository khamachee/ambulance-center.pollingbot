import json
from aiogram.filters import Command
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.settings import ROOT_USER_ID,CHANNEL_CHAT_ID, BOT_USERNAME
from bot.dispatcher import dispatcher
from models.models import Poll, VoteOption, UserVoteItem
from .states import PostingStates
from .keyboards import  onVoteAcceptKeyboard, createInlineSchemaForPoll
from .locales import VOTES_ACCEPT_GOPOST_BTNTEXT
from .callbacks import SimpleCallbackData

@dispatcher.message(Command(commands=['post']))
async def post_start_handler(message : Message, bot: Bot, state: FSMContext):
    await state.clear()
    if str(message.chat.id) != ROOT_USER_ID:
        
        await message.answer(f'You are not root user ROOTUSERID : {ROOT_USER_ID} {type(ROOT_USER_ID)} CURRENT: {message.chat.id} {type(message.chat.id)}')
        return
    await message.answer('Введите контент нового поста')
    await state.set_state(PostingStates.GETTING_POSTCONTENT) 


@dispatcher.message(PostingStates.GETTING_POSTCONTENT)
async def getting_postcontent(message : Message, bot : Bot, state : FSMContext):
    await state.update_data(messageid=message.message_id)
    await message.answer('Теперь введите обьект голосования: ')
    await state.set_state(PostingStates.GETTING_VOTEITEM)
    

@dispatcher.message(PostingStates.GETTING_VOTEITEM)
async def getVoteItemHandler(message : Message, bot : Bot, state : FSMContext):
    context = await state.get_data()
    if message.text == VOTES_ACCEPT_GOPOST_BTNTEXT:
        await post_poll(message, bot, context)
        await state.clear()
        return 
    
    await message.answer(
        text=f'Получен обьект {message.text}, введите ещё или нажмите на кнопку {VOTES_ACCEPT_GOPOST_BTNTEXT} для поста опроса',
        reply_markup=onVoteAcceptKeyboard,
    )
    vote_items : list = context.get('items', [])
    vote_items.append(message.text)
    await state.update_data(items=vote_items)
    await message.answer(json.dumps(context, indent=4))

    




async def post_poll(message: Message, bot: Bot, context: dict):
    poll = Poll.objects.create(
        message_id = message.message_id
    )
    for name in context['items']:
        vote_item = VoteOption.objects.create(
            text=name,
            poll=poll
        )
    print('bot_message_id:', message.message_id)
    new_message = await bot.copy_message(
        chat_id=CHANNEL_CHAT_ID,
        from_chat_id=message.chat.id,
        reply_markup=createInlineSchemaForPoll(poll=poll),
        message_id=poll.message_id
    )

    print('new_message_id:', new_message.message_id)
    poll.message_id = new_message.message_id
    poll.save()

    print(f'{new_message.message_id=}')

    
async def update_poll(poll : Poll, bot: Bot):
    print('update poll started')
    print('poll message id', poll.message_id)
    await bot.edit_message_reply_markup(
        chat_id=CHANNEL_CHAT_ID,
        message_id=poll.message_id,
        reply_markup=createInlineSchemaForPoll(poll) 
    )




@dispatcher.message(Command(commands=['start']))
async def vote_handler(message : Message, bot: Bot, state: FSMContext):
    if len(message.text.split(' ')) < 2: return 
    args_rawstring = message.text.split(' ')[1]
    if args_rawstring.startswith('poll_'):
        args = args_rawstring.split('_')
        poll_id = args[1]
        vote_id = args[3]
        print(f'{poll_id=}')
        print(f'{vote_id=}')
        
        try: poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist: return
        try: option = VoteOption.objects.get(poll=poll, id=vote_id)
        except Poll.DoesNotExist: return

        uservote, created = UserVoteItem.objects.get_or_create(
            user_id=message.from_user.id,
            poll=poll
        )
        uservote.option = option
        uservote.save()
        await update_poll(poll, bot=bot)
        answer_text = 'Ваш голос был принят' if created else 'Ваш голос был изменен' 
        await message.answer(text=answer_text)

         

