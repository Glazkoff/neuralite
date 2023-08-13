from celery import chain, group
from telegram import ParseMode
from dtb.celery import app
from summarizations.models import SummarizationTask
from summarizations.services import (
    SummarizationService,
    APIError,
)
from celery.utils.log import get_task_logger
from tgbot.handlers.broadcast_message.utils import send_one_message, delete_one_message
from tgbot.handlers.summarize import static_text as static_text

logger = get_task_logger(__name__)


@app.task(bind=True, max_retries=3, retry_backoff=True)
def send_confirmation(self, summarization_task_id: int) -> int:
    logger.info(f"Try to send confirmation for task {summarization_task_id}")
    try:
        task = SummarizationTask.objects.get(pk=summarization_task_id)
        user_id = task.user.user_id

        success, message_id = send_one_message(
            user_id=user_id,
            text=static_text.please_wait.format(task_id=task.pk),
            parse_mode=ParseMode.HTML,
        )

        if not success:
            raise self.retry()

        task.bot_telegram_msg_id = message_id
        task.save()
        logger.info(f"Confirmation message was sent to {user_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {user_id}, reason: {e}")
        raise self.retry(exc=e) from e

    return summarization_task_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def call_summarization_api(self, summarization_task_id: int) -> int:
    logger.info(f"Call summarization API for task #{summarization_task_id}")
    task = SummarizationTask.objects.get(pk=summarization_task_id)

    try:
        service = SummarizationService()
        api_request = service.summarize(task.input_text)
        task.openai_summarized_text = api_request
        task.save()
    except APIError as e:
        logger.error(f"Error summarizing text: {e}")
        raise self.retry(exc=e) from e
    logger.info("API call completed")

    logger.info("API call saved to DB")
    return summarization_task_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def delete_confirmation(self, summarization_task_id: int) -> int:
    logger.info(f"Try to delete service message from task #{summarization_task_id}")
    try:
        logger.info(f"Current retry: {self.request.retries}")
        task = SummarizationTask.objects.get(pk=summarization_task_id)
        if _ := delete_one_message(
            task.user.user_id, message_to_delete_id=task.bot_telegram_msg_id
        ):
            task.done = True
            task.save()
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)

    return summarization_task_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def send_result(self, summarization_task_id: int) -> int:
    logger.info(f"Try to send result for task #{summarization_task_id}")
    task = SummarizationTask.objects.get(pk=summarization_task_id)
    if _ := send_one_message(
        user_id=task.user.user_id,
        text=static_text.message_summary.format(
            summarization_task_id=summarization_task_id,
            summarized_text=task.openai_summarized_text,
        ),
        reply_to_message_id=task.user_telegram_msg_id,
    ):
        task.done = True
        task.save()
    else:
        logger.error("Error while sending message with results")
        self.retry()

    return summarization_task_id


@app.task(bind=True)
def master_summarization_task(self, summarization_task_id: int):
    chain(
        # A - Send confirmation
        send_confirmation.s(summarization_task_id),
        # B - Send API call
        call_summarization_api.s(),
        # C - Results return
        group(
            # C2 - Delete service message
            delete_confirmation.s(),
            # C1 - Send API result
            send_result.s(),
        ),
    ).apply_async()
