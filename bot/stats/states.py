from aiogram.fsm.state import StatesGroup, State

class StatsStates(StatesGroup):
    WAITING_POLLID = State()

    