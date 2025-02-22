from aiogram.fsm.state import StatesGroup, State

class PostingStates(StatesGroup):
    GETTING_POSTCONTENT = State()
    GETTING_VOTEITEM = State()
    VERIFYING = State()
