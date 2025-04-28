import logging
import os

from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BusinessConnection, FSInputFile

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
    await notify_admins(bot=bot, message=message, parse_mode=ParseMode.HTML)


@router.business_message(F.reply_to_message.photo | F.reply_to_message.video | F.reply_to_message.video_note | F.reply_to_message.voice)
async def media_reply_handler(message: Message, bot: Bot):
    reply_to_message = message.reply_to_message
    if reply_to_message.photo:
        file_path = await save_media_file(bot, reply_to_message.photo[-1].file_id, "jpg")
        await bot.send_photo(message.from_user.id, photo=FSInputFile(file_path), caption=message.caption)

    elif reply_to_message.video:
        file_path = await save_media_file(bot, reply_to_message.video.file_id, "mp4")
        await bot.send_video(message.from_user.id, video=FSInputFile(file_path), caption=message.caption)

    elif reply_to_message.video_note:
        file_path = await save_media_file(bot, reply_to_message.video_note.file_id, "mp4")
        await bot.send_video_note(message.from_user.id, video_note=FSInputFile(file_path))

    else:
        file_path = await save_media_file(bot, reply_to_message.voice.file_id, "ogg")
        await bot.send_voice(message.from_user.id, voice=FSInputFile(file_path), caption=message.caption)

    os.remove(file_path)
