from aiogram import Bot, Dispatcher, types
from database.db import Database
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config

bot = Bot(token=config.TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database(config.CONNECTION_STRING)
