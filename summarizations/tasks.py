import time
from dtb.celery import app
from summarizations.models import SummarizationTask
from celery.utils.log import get_task_logger
from tgbot.handlers.broadcast_message.utils import send_one_message, delete_one_message

logger = get_task_logger(__name__)


@app.task
def call_summarization_api(model_id: int):
    time.sleep(5)

    task = SummarizationTask.objects.get(pk=model_id)
    if _ := send_one_message(
        task.user.user_id, "test :)", reply_to_message_id=task.user_telegram_msg_id
    ):
        task.done = True
        task.save()
    else:
        logger.error("HUSTON WE HAVE A PROBLEM 1 !!!")

    logger.info("task.user.user_id, task.bot_telegram_msg_id")
    logger.info(
        "task.user.user_id, task.bot_telegram_msg_id"
        + str(task.user.user_id)
        + " "
        + str(task.bot_telegram_msg_id),
    )
    if _ := delete_one_message(
        task.user.user_id, message_to_delete_id=task.bot_telegram_msg_id
    ):
        task.done = True
        task.save()
    else:
        logger.error("HUSTON WE HAVE A PROBLEM 2 !!!")
