from aiogram.filters.callback_data import CallbackData

class SimpleCallbackData(CallbackData, prefix='simplecb'):
    data : str 