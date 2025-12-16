from aiogram import Bot 
from io import BytesIO
from openpyxl import Workbook
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config.settings import ROOT_USER_ID
from bot.dispatcher import dispatcher
from .states import StatsStates
from models.models import Poll, UserVoteItem, VoteOption

@dispatcher.message(Command(commands=['stats']))
async def stats_handlers(message : Message, bot : Bot, state : FSMContext):
    await state.clear()
    if str(message.chat.id) != ROOT_USER_ID:
        await message.answer(f'You have not permission')
        return
    await message.answer('Enter poll id')
    await state.set_state(StatsStates.WAITING_POLLID)
    

@dispatcher.message(StatsStates.WAITING_POLLID)
async def obtain_and_giveback(message : Message, bot : Bot, state : FSMContext):
    poll_id = message.text
    queryset = Poll.objects.filter(id=poll_id)
    if not queryset:
        await message.answer(f'there is not poll with id {poll_id}')
        await state.clear()
        return
    poll : Poll = queryset.first()
    votes = UserVoteItem.objects.filter(poll=poll)
    sheet = dict()
    for vote in votes:
        key = str(vote.option.text) 
        if key not in sheet: sheet[key] = []
        
        sheet[key].append(vote.user_number)
    excel_file = generate_excel(sheet)
    document = BufferedInputFile(
        excel_file.read(),
        filename='otchet.xlsx'
    )
    await message.answer_document(
        document=document,
    )


def generate_excel(data: dict[str, list]) -> BytesIO:
    wb = Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)
    for sheet_name, values in data.items():
        ws = wb.create_sheet(title=sheet_name[:31])  
        for value in values:
            ws.append([value])
    file = BytesIO()
    wb.save(file)
    file.seek(0)
    return file