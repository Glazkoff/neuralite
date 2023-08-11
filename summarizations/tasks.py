from celery import chain, group
from telegram import ParseMode
from dtb.celery import app
from summarizations.models import SummarizationTask, VoiceMessage
from summarizations.services import (
    SummarizationService,
    TranscribationService,
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
        raise self.retry(exc=e)

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
        raise self.retry(exc=e)
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


@app.task(bind=True, max_retries=3, retry_backoff=True)
def send_confirmation_voice(self, voice_message_id: int) -> int:
    logger.info(f"Try to send confirmation for voice message #{voice_message_id}")
    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        user_id = voice_message.user.user_id

        success, message_id = send_one_message(
            user_id=user_id,
            text=static_text.please_wait_voice.format(
                voice_message_id=voice_message.pk
            ),
            parse_mode=ParseMode.HTML,
        )

        if not success:
            raise self.retry()

        voice_message.bot_telegram_msg_id = message_id
        voice_message.save()
        logger.info(f"Confirmation message was sent to {user_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {user_id}, reason: {e}")
        raise self.retry(exc=e)
    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def call_stt_api(self, voice_message_id: int) -> int:
    logger.info(f"Call STT API for voice summarization #{voice_message_id}")
    voice_message = VoiceMessage.objects.get(pk=voice_message_id)

    try:
        service = TranscribationService()
        api_request = service.transcribe_sync(voice_message.voice_path)

        summarization_task = SummarizationTask.objects.create(
            user_telegram_msg_id=voice_message.user_telegram_msg_id,
            user=voice_message.user,
            input_text=api_request,
        )

        voice_message.summarization_task = summarization_task
        voice_message.transcribed_text = api_request
        voice_message.save()

    except APIError as e:
        logger.error(f"Error transcribing text: {e}")
        raise self.retry(exc=e)
    logger.info("API call completed")

    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def send_result_voice(self, voice_message_id: int) -> int:
    logger.info(f"Try to send result for voice message #{voice_message_id}")
    voice_message = VoiceMessage.objects.get(pk=voice_message_id)
    if _ := send_one_message(
        user_id=voice_message.user.user_id,
        text=static_text.message_transcribe.format(
            voice_message_id=voice_message_id,
            transcribed_text=voice_message.transcribed_text,
        ),
        reply_to_message_id=voice_message.user_telegram_msg_id,
    ):
        voice_message.done = True
        voice_message.save()
    else:
        logger.error("Error while sending message with results")
        self.retry()

    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def delete_confirmation_voice(self, voice_message_id: int) -> int:
    logger.info(
        f"Try to delete service message from voice messsage #{voice_message_id}"
    )
    try:
        logger.info(f"Current retry: {self.request.retries}")
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        if _ := delete_one_message(
            voice_message.user.user_id,
            message_to_delete_id=voice_message.bot_telegram_msg_id,
        ):
            voice_message.done = True
            voice_message.save()
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)
    return voice_message_id


@app.task(bind=True)
def master_voice_message_task(self, voice_message_id: int):
    chain(
        # A - Send confirmation
        send_confirmation_voice.s(voice_message_id),
        # B - Send STT API call
        call_stt_api.s(),
        # C - Results return
        group(
            # C1 - Send API result & create task for summarization
            send_result_voice.s(),
            # C2 - Delete service message
            delete_confirmation_voice.s(),
        ),
    ).apply_async()
