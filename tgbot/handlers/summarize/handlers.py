import os
import telegram
import requests
from telegram import ParseMode, Update, Voice
from telegram.ext import CallbackContext

from tgbot.handlers.summarize import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from summarizations.models import (
    SummarizationTask,
    VoiceMessage,
    LangchainSummarizationTask,
)
from users.models import User


def begin_summarization(update: Update, context: CallbackContext) -> None:
    if update.message.text == static_text.summ_command:
        # user typed only command without text for the message.
        update.message.reply_text(
            text=static_text.summ_wrong_format,
            parse_mode=ParseMode.HTML,
        )
        return

    user = User.get_user(update, context)
    task = {
        "user": user,
        "input_text": update.message.text.replace(f"{static_text.summ_command} ", ""),
        "user_telegram_msg_id": update.message.message_id,
    }
    SummarizationTask.objects.create(**task)


def begin_tts(update: Update, context: CallbackContext) -> None:
    # Get Voice object from message
    voice: Voice = update.message.voice
    # Get ID of audio file
    file_id = voice.file_id
    # Get all info about file
    voice_file = context.bot.get_file(file_id)
    # Get user
    user = User.get_user(update, context)
    # Create VoiceMessage instance
    voice_message = {
        "user": user,
        "file_id": file_id,
        "duration": voice.duration,
        "voice_path": voice_file.file_path,
        "user_telegram_msg_id": update.message.message_id,
    }
    VoiceMessage.objects.create(**voice_message)


def begin_langchain_summarization(update: Update, context: CallbackContext) -> None:
    if update.message.text == static_text.langchain_summ_command:
        # user typed only command without text for the message.
        update.message.reply_text(
            text=static_text.langchain_summ_wrong_format,
            parse_mode=ParseMode.HTML,
        )
        return

    user = User.get_user(update, context)
    task = {
        "user": user,
        "input_text": update.message.text.replace(f"{static_text.summ_command} ", ""),
        "user_telegram_msg_id": update.message.message_id,
    }
    LangchainSummarizationTask.objects.create(**task)
