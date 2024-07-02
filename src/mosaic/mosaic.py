from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.types.input_sticker import InputSticker
from config.config import BOT_USERNAME, MOSAIC_STICKER_EMOTE
import numpy as np
import os
from PIL import Image
from typing import Literal
import uuid

TELEGRAM_STICKER_PREVIEW_GAP = 20

def slice_photo(photo_path: str,
                slicing_shape: tuple[int, int],  
                target_folder: str = None,
                crop: int = TELEGRAM_STICKER_PREVIEW_GAP,
                delete_original: bool = False):
    """
    Slice photo into grid of subphotos and save them into *target_folder*. 
    Subphotos will have names slice_i_j, where i and j are their indices in grid. 

    Parameters 
    -------
    photo path: str
        Path to photo to be sliced
    slicing_shape: tuple[int, int]
        Shape of the grid to be sliced in. 
    target_folder: str (default is None)
        Folder for subphotos to be saved to. If not specified, save to folder of original photo.
    crop: int (default is 0)
        Shrink all subphotos by *crop* pixels.
    delete_original: bool (default is False)
        Delete original photo
    """
    if not target_folder:
        target_folder = photo_path[:photo_path.rfind('/')]
    photo = Image.open(photo_path)
    size: tuple[int, int] = photo.size
    subphoto_size: tuple[int, int] = size[0] // slicing_shape[0], size[1] // slicing_shape[1]
    for i in range(slicing_shape[0]):
        for j in range(slicing_shape[1]):
            subphoto = Image.fromarray(np.asarray(photo)
                                       [j * subphoto_size[0] + crop : (j + 1) * subphoto_size[0] - crop,
                                        i * subphoto_size[1] + crop : (i + 1) * subphoto_size[1] - crop]
                                       )
            subphoto.save(f"{target_folder}/slice_{i}_{j}.png")
    if delete_original:
        os.remove(photo_path)


async def create_stickerpack_from_photos(bot: Bot,
                                         photo_folder_path: str,
                            title: str,
                            user_id: int,
                            name_prefix: str,
                            bot_username: str = BOT_USERNAME,
                            format: Literal["static"] = "static", 
                            ) -> str:
    """
    Create a stickerpack from photos in some folder. 
    The name of the stickerpack has the format {name_prefix}_{uuid}_by_{bot_username}.
    More about stickerpack names: https://docs.aiogram.dev/en/dev-3.x/api/methods/create_new_sticker_set.html (parameter "name").
    Returns stickerpack name.
    
    Parameters
    ----------
    photo_folder_path: str
        Folder with photos for stickerpack
    title: str
        Title for the stickerpack
    user_id: int
        ID of the stickerpack creator
    name_prefix: str
        The stickerpack name prefix.
    bot_username: str (default is "Sticker mosaic"):
        The stickerpack bot username in stickerpack name. 
    format: str (default is "static)
        Format of stickers.
        Currently, only "static" is supported.
    """
    def _sliced_photo_sort_key(x: str):
        i = int(x[x.find('_') + 1: x.rfind('_')])
        j = int(x[x.rfind('_') + 1: x.find('.')])
        return j * 100 + i
    
    MIN_STICKER_SIZE = 512
    stickers = []
    for file in os.listdir(photo_folder_path):
        photo = Image.open(f"{photo_folder_path}/{file}")
        # adjusting
        if max(photo.size) < MIN_STICKER_SIZE:
            ratio = MIN_STICKER_SIZE / max(photo.size)
            photo = photo.resize((round(photo.size[0] * ratio), round(photo.size[1] * ratio)))
            os.remove(f"{photo_folder_path}/{file}")
            photo.save(f"{photo_folder_path}/{file}")
        stickers.append(InputSticker(sticker=FSInputFile(f"{photo_folder_path}/{file}"),
                                      format=format, 
                                      emoji_list=[MOSAIC_STICKER_EMOTE]))
        
    stickers = [InputSticker(sticker=FSInputFile(f"{photo_folder_path}/{photo}"), format=format, emoji_list=[MOSAIC_STICKER_EMOTE])
                for photo in sorted(os.listdir(photo_folder_path), key=_sliced_photo_sort_key)]
    stickerpack_name = f"{name_prefix}{uuid.uuid4()}_by_{bot_username}".replace('-', '_')
    await bot.create_new_sticker_set(user_id=user_id,
                        name=stickerpack_name,
                        title=title,
                        stickers=stickers)
    return stickerpack_name
