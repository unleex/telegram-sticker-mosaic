import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from config.config import BOT_USERNAME, MOSAIC_PHOTOS_PATH
from keyboards.keyboards import mosaic_emoji_or_sticker_keyboard
from lexicon.lexicon import LEXICON_EN
from mosaic.mosaic import slice_photo, create_stickerpack_from_photos
from PIL import Image
from states.states import FSMStates


rt = Router()
lexicon = LEXICON_EN
TELEGRAM_STICKERPACK_ROW_WIDTH = 5 # sticker amount in a row of stickerpack preview
TELEGRAM_STICKER_PREVIEW_APPLE_GAP = 20
CUSTOM_EMOJI_SIZE = 100

@rt.message(Command("mosaic"), StateFilter(default_state))
async def init_mosaic(msg: Message, state: FSMContext):
    await msg.answer(lexicon["init_mosaic"])
    await state.set_state(FSMStates.init_mosaic)


@rt.message(StateFilter(FSMStates.init_mosaic))
async def mosaic_set_title(msg: Message, state: FSMContext):
    if not msg.text or not 1 <= len(msg.text) <= 64:
        await msg.answer(lexicon["mosaic_title_incorrect_size"] % len(msg.text)) 
        return
    await state.set_data({"stickerpack_title": msg.text})
    await msg.answer(lexicon["mosaic_title_set"], reply_markup=mosaic_emoji_or_sticker_keyboard)
    await state.set_state(FSMStates.mosaic_setting_title)


@rt.callback_query(StateFilter(FSMStates.mosaic_setting_title))
async def mosaic_emoji_or_sticker_set(clb: CallbackQuery, state: FSMContext):
    ctx = await state.get_data()
    ctx["emoji_or_sticker"] = clb.data.split()[1] # data format is "mosaic *** selected"
    await state.set_data(ctx)
    await state.set_state(FSMStates.mosaic_emoji_or_sticker_set)
    await clb.answer(lexicon["mosaic_emoji_or_sticker_set"], show_alert=True)


@rt.message(StateFilter(FSMStates.mosaic_emoji_or_sticker_set))
async def get_mosaic_photo(msg: Message, state: FSMContext, bot: Bot):
    photo = msg.photo
    user_id = msg.from_user.id
    ctx_data = await state.get_data()
    if photo is None:
        await msg.answer(lexicon["mosaic_no_photo_provided"])
        return
    if not os.path.exists(f"{MOSAIC_PHOTOS_PATH}/{user_id}"):
        os.mkdir(f"{MOSAIC_PHOTOS_PATH}/{user_id}")
    file_name = f"{MOSAIC_PHOTOS_PATH}/{user_id}/{photo[-1].file_id}.png"
    await msg.answer(lexicon["mosaic_processing"])
    await bot.download(photo[-1].file_id, destination=file_name)
    image = Image.open(file_name)
    if ctx_data["emoji_or_sticker"] == "regular":
        sticker_crop = TELEGRAM_STICKER_PREVIEW_APPLE_GAP
    else:
        sticker_crop = 0
    if ctx_data["emoji_or_sticker"] == "regular":
        slicing_shape = (TELEGRAM_STICKERPACK_ROW_WIDTH,
                                    round(TELEGRAM_STICKERPACK_ROW_WIDTH * (image.size[1] / image.size[0])))
    else: 
        slicing_shape = (round(image.size[0] / CUSTOM_EMOJI_SIZE), 
                         round(round(image.size[0] / CUSTOM_EMOJI_SIZE) * (image.size[1] / image.size[0])))
    slice_photo(photo_path=file_name, 
                slicing_shape=slicing_shape, # avoid stretching
                delete_original=True,
                crop=sticker_crop)
    stickerpack_name = await create_stickerpack_from_photos(
                            bot=bot,
                            photo_folder_path=f"{MOSAIC_PHOTOS_PATH}/{user_id}",
                            title = ctx_data["stickerpack_title"],
                            user_id=user_id,
                            name_prefix="mosaic",
                            bot_username=BOT_USERNAME,
                            format="static",
                            type=ctx_data["emoji_or_sticker"]
                            )
    for photo in os.listdir(f"{MOSAIC_PHOTOS_PATH}/{user_id}"):
        os.remove(f"{MOSAIC_PHOTOS_PATH}/{user_id}/{photo}")
    os.rmdir(f"{MOSAIC_PHOTOS_PATH}/{user_id}")
    if ctx_data["emoji_or_sticker"] == "regular":
        await msg.answer(lexicon["mosaic_success_sticker"] % "t.me/addstickers/%s" % stickerpack_name)
    else:
        await msg.answer(lexicon["mosaic_success_emoji"] % ("t.me/addstickers/%s" % stickerpack_name, *slicing_shape))
    await state.clear()
    
    
