import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from aiogram import Router, Bot
from aiogram.enums.content_type import ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from config.config import BOT_USERNAME, MOSAIC_PHOTOS_PATH
from lexicon.lexicon import LEXICON_EN
from mosaic.mosaic import slice_photo, create_stickerpack_from_photos
from PIL import Image
from states.states import FSMStates


rt = Router()
lexicon = LEXICON_EN
TELEGRAM_STICKERPACK_ROW_WIDTH = 5 # sticker amount in a row of stickerpack preview

@rt.message(Command("mosaic"), StateFilter(default_state))
async def init_mosaic(msg: Message, state: FSMContext):
    await msg.answer(lexicon["init_mosaic"])
    await state.set_state(FSMStates.init_mosaic)


@rt.message(StateFilter(FSMStates.init_mosaic))
async def mosaic_set_title(msg: Message, state: FSMContext):
    if not msg.text or not 1 <= len(msg.text) <= 64:
        await msg.answer(lexicon["mosaic_title_incorrect_size"]) % len(msg.text)
        return
    await state.set_data({"stickerpack_title": msg.text})
    await msg.answer(lexicon["mosaic_title_set"])
    await state.set_state(FSMStates.mosaic_setting_title)


@rt.message(StateFilter(FSMStates.mosaic_setting_title))
async def get_mosaic_photo(msg: Message, state: FSMContext, bot: Bot):
    photo = msg.photo
    if photo is None:
        await msg.answer(lexicon["mosaic_no_photo_provided"])
        return
    file_name = f"{MOSAIC_PHOTOS_PATH}/{photo[-1].file_id}.png"
    await msg.answer(lexicon["mosaic_processing"])
    await bot.download(photo[-1].file_id, destination=file_name)
    image = Image.open(file_name)
    slice_photo(photo_path=file_name, 
                slicing_shape=(TELEGRAM_STICKERPACK_ROW_WIDTH,
                                round(TELEGRAM_STICKERPACK_ROW_WIDTH * (image.size[1] / image.size[0]))), # avoid stretching
                delete_original=True)
    stickerpack_name = await create_stickerpack_from_photos(
                            bot=bot,
                            photo_folder_path=MOSAIC_PHOTOS_PATH,
                            title = (await state.get_data())["stickerpack_title"],
                            user_id=msg.from_user.id,
                            name_prefix="mosaic",
                            bot_username=BOT_USERNAME,
                            format="static"
                            )
    for photo in os.listdir(MOSAIC_PHOTOS_PATH):
        os.remove(f"{MOSAIC_PHOTOS_PATH}/{photo}")
    await msg.answer(lexicon["mosaic_success"] % "t.me/addstickers/%s" % stickerpack_name)
    await state.clear()
    
    
