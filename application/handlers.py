import logging
import os

from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNotFound
from aiogram.filters import CommandStart
from aiogram.types import Message, BusinessConnection, FSInputFile, User

from application.settings import settings
from application.utils import notify_admins, get_user_name_and_link, save_media_file

router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message):
    await message.answer("Hi, I'll be sending all extracted media to this chat room 🫡")


@router.message()
async def all_messages_handler(message: Message):
    await message.answer("Unknown command, please use /start to begin 😕")


@router.business_connection()
async def business_connection_event_handler(business_connection_data: BusinessConnection, bot: Bot):
    if business_connection_data.is_enabled:
        header = "🟢 Business connection enabled"
    else:
        header = "🔴 Business connection disabled"

    user_filed = get_user_name_and_link(business_connection_data.user)
    message = f"<b>{header}</b>\n" \
                f"🆔 ID: <i>{business_connection_data.id}</i>\n" \
                f"👤 User: <a href=\"{user_filed[1]}\">{user_filed[0]}</a>"

    logging.info(business_connection_data)
    await notify_admins(bot=bot, message=message)


async def send_media_to_admins(bot: Bot, user: User, admins: list[int], file_path: str, caption: str = None):
    if file_path.endswith("jpg"):
        caption = f"Photo received from {user.full_name} (`{user.id}`)\n\n{caption or ''}"
        for admin_telegram_id in admins:
            await bot.send_photo(admin_telegram_id, photo=FSInputFile(file_path), caption=caption, parse_mode=ParseMode.MARKDOWN)

    elif file_path.endswith("mp4"):
        caption = f"Video received from {user.full_name} (`{user.id}`)\n\n{caption or ''}"
        for admin_telegram_id in admins:
            await bot.send_video(admin_telegram_id, video=FSInputFile(file_path), caption=caption, parse_mode=ParseMode.MARKDOWN)

    elif file_path.endswith("ogg"):
        caption = f"Voice message received from {user.full_name} (`{user.id}`)\n\n{caption or ''}"
        for admin_telegram_id in admins:
            await bot.send_voice(admin_telegram_id, voice=FSInputFile(file_path), caption=caption, parse_mode=ParseMode.MARKDOWN)


async def send_media_to_user(bot: Bot, user: User, file_path: str, caption: str = None):
    if file_path.endswith("jpg"):
        await bot.send_photo(user.id, photo=FSInputFile(file_path), caption=caption)

    elif file_path.endswith("mp4"):
        await bot.send_video(user.id, video=FSInputFile(file_path), caption=caption)

    elif file_path.endswith("ogg"):
        await bot.send_voice(user.id, voice=FSInputFile(file_path), caption=caption)


@router.business_message(F.reply_to_message.photo | F.reply_to_message.video | F.reply_to_message.video_note | F.reply_to_message.voice)
async def media_reply_handler(message: Message, bot: Bot):
    try:
        reply_to_message = message.reply_to_message
        if reply_to_message.photo:
            file_path = await save_media_file(bot, reply_to_message.photo[-1].file_id, "jpg")

        elif reply_to_message.video:
            file_path = await save_media_file(bot, reply_to_message.video.file_id, "mp4")

        elif reply_to_message.video_note:
            file_path = await save_media_file(bot, reply_to_message.video_note.file_id, "mp4")

        else:
            file_path = await save_media_file(bot, reply_to_message.voice.file_id, "ogg")

        user = message.from_user
        caption = reply_to_message.caption or ""
        if user.id == settings.ADMINS_TELEGRAM_ID[0]:
            admins = []
        elif user.id == settings.ADMINS_TELEGRAM_ID[1]:
            admins = [settings.ADMINS_TELEGRAM_ID[0]]
        else:
            admins = settings.ADMINS_TELEGRAM_ID

        await send_media_to_user(bot, user, file_path, caption)
        await send_media_to_admins(bot, user, admins, file_path, caption)

        if os.path.exists(file_path):
            os.remove(file_path)

    except TelegramNotFound:
        logging.warning("User does not start the bot yet")
