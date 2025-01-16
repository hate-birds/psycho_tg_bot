from aiogram import Bot
from aiogram.types import BotCommand

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запуск бота"),
        BotCommand(command="/about", description="Информация и Инструкции"),
        BotCommand(command="/feedback", description="Оставить Отзыв"),
    ]
    await bot.set_my_commands(commands)