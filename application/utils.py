from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import User

from application.settings import settings


async def notify_admins(bot: Bot, message: str, parse_mode: ParseMode = ParseMode.MARKDOWN):
    for admin_telegram_id in settings.ADMINS_TELEGRAM_ID:
        await bot.send_message(admin_telegram_id, message, parse_mode=parse_mode, disable_web_page_preview=True)


def get_user_name_and_link(user: User):
    if user.username:
        return user.full_name, f"t.me/{user.username}"
    else:
        return user.full_name, f"tg://user?id={user.id}"


async def save_media_file(bot: Bot, file_id: str, file_type: str):
    file_path = f"media/{file_id}.{file_type}"
    await bot.download(file_id, destination=file_path)
    return file_path
