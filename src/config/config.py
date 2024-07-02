from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, Redis
import asyncio
from environs import Env


env =  Env()
env.read_env()
BOT_TOKEN = env('BOT_TOKEN')
ADMIN_ID = env.int('ADMIN_ID')
MOSAIC_STICKER_EMOTE = "🧩"
MOSAIC_PHOTOS_PATH = "src/mosaic_photos"
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
BOT_USERNAME = "sticker_mosaic_bot"
redis = Redis(host='localhost')
storage = RedisStorage(redis=redis) 
dp = Dispatcher(storage=storage)