from datetime import timedelta

from django.utils.timezone import now
import telegram
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.info import send_typing_action, extract_user_data_from_update
from users.models import User


def admin(update: Update, context: CallbackContext) -> None:
    """Show help info about all secret admins commands"""
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    update.message.reply_text(static_text.secret_admin_commands)


def stats(update: Update, context: CallbackContext) -> None:
    """Show help info about all secret admins commands"""
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return

    text = static_text.users_amount_stat.format(
        user_count=User.objects.count(),  # count may be ineffective if there are a lot of users.
        active_24=User.objects.filter(
            updated_at__gte=now() - timedelta(hours=24)
        ).count(),
    )

    update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def send_test_reply(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)["user_id"]

    if update.message.text == static_text.reply_command:
        # user typed only command without text for the message.
        update.message.reply_text(
            text=static_text.reply_wrong_format,
            parse_mode=telegram.ParseMode.HTML,
        )
        return
    try:
        message_id = update.message.text.replace("/reply ", "")
        context.bot.send_message(
            chat_id=user_id,
            reply_to_message_id=message_id,
            text=static_text.reply_test.format(message_id=message_id),
        )
    except Exception:
        update.message.reply_text(static_text.reply_incorrect_command)


@send_typing_action
def export_users(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return

    # in values argument you can specify which fields should be returned in output csv
    users = User.objects.all().values()
    csv_users = _get_csv_from_qs_values(users)
    context.bot.send_document(chat_id=u.user_id, document=csv_users)
