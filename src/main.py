import asyncio
from config.config import bot, dp
from keyboards.set_menu import set_main_menu
from handlers import mosaic_handlers, other_handlers

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates = True)
    await set_main_menu(bot)
    dp.include_router(other_handlers.rt)
    dp.include_router(mosaic_handlers.rt)
    print("starting")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())