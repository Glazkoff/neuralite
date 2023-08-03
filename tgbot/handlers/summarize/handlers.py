from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.summarize import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update


def begin_summarization(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)["user_id"]
    text = static_text.text_needed

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
    )
