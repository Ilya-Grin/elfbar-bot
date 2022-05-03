from aiogram import Dispatcher
from .is_admin import IsAdmin


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsAdmin)
