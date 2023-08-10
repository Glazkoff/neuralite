import telegram
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.summarize import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from summarizations.models import SummarizationTask
from users.models import User


def begin_summarization(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)["user_id"]

    if update.message.text == static_text.summ_command:
        # user typed only command without text for the message.
        update.message.reply_text(
            text=static_text.summ_wrong_format,
            parse_mode=telegram.ParseMode.HTML,
        )
        return

    user = User.get_user(update, context)
    task = {
        "user": user,
        "input_text": update.message.text.replace(f"{static_text.summ_command} ", ""),
        "user_telegram_msg_id": update.message.message_id,
    }
    SummarizationTask.objects.create(**task)
