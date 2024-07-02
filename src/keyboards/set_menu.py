from aiogram.types import BotCommand
from aiogram import Bot


async def set_main_menu(bot: Bot) -> None:
    main_menu_commands = [
        BotCommand(command="mosaic", description="Create mosaic pack🧩"),
        BotCommand(command="cancel", description="Cancel current operation❌"),
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Info about the bot")
    ]
    await bot.set_my_commands(main_menu_commands)