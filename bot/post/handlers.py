import io
import json
import random
import logging
import numpy as np
from aiogram.filters import Command
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from noise import pnoise2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config.settings import ROOT_USER_ID,CHANNEL_CHAT_ID, BOT_USERNAME, CHANNEL_USERNAME
from bot.dispatcher import dispatcher
from models.models import Poll, VoteOption, UserVoteItem
from .states import PostingStates, VotingStates
from .keyboards import  onVoteAcceptKeyboard, createInlineSchemaForPoll
from .locales import VOTES_ACCEPT_GOPOST_BTNTEXT

@dispatcher.message(Command(commands=['post']))
async def post_start_handler(message : Message, bot: Bot, state: FSMContext):
    await state.clear()
    if str(message.chat.id) != ROOT_USER_ID:
        
        await message.answer(f'You have not permission')
        return
    await message.answer('Введите контент нового поста')
    await state.set_state(PostingStates.GETTING_POSTCONTENT) 


@dispatcher.message(PostingStates.GETTING_POSTCONTENT)
async def getting_postcontent(message : Message, bot : Bot, state : FSMContext):
    await state.update_data(messageid=message.message_id)
    await state.update_data(message_caption=message.text)
    await message.answer('Теперь введите обьект голосования: ')
    await state.set_state(PostingStates.GETTING_VOTEITEM)
    

@dispatcher.message(PostingStates.GETTING_VOTEITEM)
async def getVoteItemHandler(message : Message, bot : Bot, state : FSMContext):
    context = await state.get_data()
    if message.text == VOTES_ACCEPT_GOPOST_BTNTEXT:
        await post_poll(context['messageid'], bot, context,)
        await state.clear()
        return 
    
    await message.answer(
        text=f'Получен обьект {message.text}, введите ещё или нажмите на кнопку {VOTES_ACCEPT_GOPOST_BTNTEXT} для поста опроса',
        reply_markup=onVoteAcceptKeyboard,
    )
    vote_items : list = context.get('items', [])
    vote_items.append(message.text)
    await state.update_data(items=vote_items)

    




async def post_poll(messageid: str, bot: Bot, context: dict):
    poll = Poll.objects.create(
        message_id = messageid
    )
    for name in context['items']:
        vote_item = VoteOption.objects.create(
            text=name,
            poll=poll
        )
    new_message = await bot.copy_message(
        chat_id=CHANNEL_CHAT_ID,
        from_chat_id=ROOT_USER_ID,
        reply_markup=createInlineSchemaForPoll(poll=poll),
        message_id=poll.message_id, 
    )
    await bot.edit_message_text(
        chat_id=CHANNEL_CHAT_ID,
        message_id=new_message.message_id,
        text=f"{context['message_caption']}\n\n PID : `{poll.id}`",
        parse_mode="Markdown",
        reply_markup=createInlineSchemaForPoll(poll=poll),
)

    print('new_message_id:', new_message.message_id)
    poll.message_id = new_message.message_id
    poll.save()


    
async def update_poll(poll : Poll, bot: Bot):
    print('poll message id', poll.message_id)
    await bot.edit_message_reply_markup(
        chat_id=CHANNEL_CHAT_ID,
        message_id=poll.message_id,
        reply_markup=createInlineSchemaForPoll(poll) 
    )


# @dispatcher.message(Command(commands=['start']))
# async def vote_contact_getter(message : Message, bot : Bot, state : FSMContext):
#     await state.clear()
#     args_rawstring = message.text.split(' ')[1]
#     if args_rawstring.startswith('poll_'):
#         try:
#             membership = await bot.get_chat_member(CHANNEL_CHAT_ID, message.from_user.id)
#             if membership.status not in ["member", "administrator", "creator"]:
#                 await ask_for_sub(message, bot, state)
#                 return 
#         except: return 
#     args = args_rawstring.split('_')
#     poll_id = args[1]
#     vote_id = args[3]
#     await state.update_data(
#         poll=poll_id,
#         vote=vote_id,
#     )
#     await message.answer()


@dispatcher.message(Command(commands=['start']))
async def vote_handler(message : Message, bot: Bot, state: FSMContext):
    if len(message.text.split(' ') ) < 2: return
    args_rawstring = message.text.split(' ')[1]
    if args_rawstring.startswith('poll_'):
        try:
            membership = await bot.get_chat_member(CHANNEL_CHAT_ID, message.from_user.id)
            if membership.status not in ["member", "administrator", "creator"]:
                await ask_for_sub(message, bot, state)
                return 
        except: return
        args = args_rawstring.split('_')
        poll_id = args[1]
        vote_id = args[3]
        
        await state.update_data(poll_id=poll_id)
        await state.update_data(vote_id=vote_id)    
        img, answer = generate_captcha_image()
        await state.update_data(answer=str(answer))

        await message.answer_photo(
            photo=img,
            caption='Javobini kiring' 
        )
        await state.set_state(VotingStates.VERIFY_CAPTCHA)
        
        

@dispatcher.message(VotingStates.VERIFY_CAPTCHA)
async def captcha_handler(message : Message, bot : Bot, state : FSMContext):
    context = await state.get_data()
    if not(message.text == str(context['answer'])):
        img, answer = generate_captcha_image()
        await state.update_data(answer=str(answer))
        await message.answer_photo(
            photo=img,
            caption='xato-kiritildi, qaytadan uruning',
        )
        return 
    poll_id = context['poll_id']   
    vote_id = context['vote_id']
    
    
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
    try:
        await update_poll(poll, bot=bot)
    except : pass
    answer_text = 'Ovozingiz qabul qilindi' if created else 'Ovozingiz o`zgartirildi' 
    await message.answer(text=answer_text)
    await state.clear()
    
    
    
         

async def ask_for_sub(message: Message, bot: Bot, state : FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Obuna bo'lish",
        url=f"t.me/{CHANNEL_USERNAME}"
    )
    builder.adjust(1)
    await message.answer(
        text='Ovoz bera olish uchun kanalga obuna bolishingiz lozim!', 
        reply_markup=builder.as_markup(),
    )



def generate_math_task():
    a = random.randint(20, 29)
    b = random.randint(10, 19)
    op = random.choice(["+", "-"])

    if op == "+":
        answer = a + b
    elif op == "-":
        answer = a - b
    else:
        answer = a * b

    return f"{a}{op}{b}", answer


def perlin_distort(image, scale=25.0, amplitude=10):
    width, height = image.size
    pixels = np.array(image)
    new_pixels = np.zeros_like(pixels)

    for y in range(height):
        for x in range(width):
            dx = int(pnoise2(x / scale, y / scale) * amplitude)
            dy = int(pnoise2(x / scale + 100, y / scale + 100) * amplitude)

            nx = min(max(x + dx, 0), width - 1)
            ny = min(max(y + dy, 0), height - 1)

            new_pixels[y, x] = pixels[ny, nx]

    return Image.fromarray(new_pixels)


def generate_captcha_image():
    text, answer = generate_math_task()

    img = Image.new("RGB", (240, 100), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
    draw.text((40, 25), text, font=font, fill=(0, 0, 0))

    # линии
    for _ in range(4):
        draw.line(
            (
                random.randint(0, 240),
                random.randint(0, 100),
                random.randint(0, 240),
                random.randint(0, 100),
            ),
            fill=(0, 0, 0),
            width=2,
        )

    img = perlin_distort(img)
    img = img.filter(ImageFilter.GaussianBlur(1))

    buf = io.BytesIO()
    buf.name = "captcha.png"
    img.save(buf, format="PNG")
    buf.seek(0)
    file = BufferedInputFile(buf.read(), filename='captcha.png')
    return file, answer
