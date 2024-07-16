from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
emoji_butt = InlineKeyboardButton(
    text="Emoji",
    callback_data="mosaic custom_emoji selected"
)
sticker_butt = InlineKeyboardButton(
    text="Sticker",
    callback_data="mosaic regular selected"
)
mosaic_emoji_or_sticker_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [emoji_butt],
        [sticker_butt]
    ],
    resize_keyboard=True
)