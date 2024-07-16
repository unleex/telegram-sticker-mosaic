from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, FSInputFile
from lexicon.lexicon import LEXICON_EN


rt = Router()
lexicon = LEXICON_EN

@rt.message(CommandStart(), StateFilter(default_state))
async def start(msg: Message):
    await msg.answer(lexicon["start"])


@rt.message(Command("help"), StateFilter(default_state))
async def help(msg: Message):
    await msg.answer(lexicon["help"])
    await msg.answer_photo(FSInputFile("src/sample_photos/sample_input_sticker.png"), caption=lexicon["help_sample_input"])
    await msg.answer_photo(FSInputFile("src/sample_photos/sample_output_sticker.png"), caption=lexicon["help_sample_output"])
    await msg.answer_photo(FSInputFile("src/sample_photos/sample_input_emoji.png"), caption=lexicon["help_sample_input"])
    await msg.answer_photo(FSInputFile("src/sample_photos/sample_output_emoji.png"), caption=lexicon["help_sample_output"])

    

@rt.message(Command("cancel"))
async def cancel(msg: Message, state: FSMContext):
    await msg.answer(lexicon["cancel"])
    await state.clear()