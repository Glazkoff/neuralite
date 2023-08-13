from celery import chain, group
from telegram import ParseMode
from dtb.celery import app
from summarizations.models import SummarizationTask, VoiceMessage
from summarizations.services import (
    SpeechToTextService,
    StorageService,
    APIError,
)
from celery.utils.log import get_task_logger
from tgbot.handlers.broadcast_message.utils import send_one_message, delete_one_message
from tgbot.handlers.summarize import static_text as static_text
from .utils import get_voice_massage_key

logger = get_task_logger(__name__)


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
        raise self.retry(exc=e) from e
    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def call_stt_api(self, voice_message_id: int) -> int:
    logger.info(f"Call STT API for voice summarization #{voice_message_id}")
    voice_message = VoiceMessage.objects.get(pk=voice_message_id)

    try:
        service = SpeechToTextService()
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
        raise self.retry(exc=e) from e
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
    logger.info(f"Try to delete service message from voice message #{voice_message_id}")
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


@app.task(bind=True, max_retries=3, retry_backoff=True)
def upload_long_voice(self, voice_message_id: int) -> int:
    logger.info(
        f"Try to send file to S3 storage from voice message #{voice_message_id}"
    )

    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        service = StorageService()
        path = service.upload_from_url(
            voice_message.voice_path, get_voice_massage_key(voice_message)
        )
        voice_message.S3_path = path
        voice_message.save()
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)
    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def call_stt_api_async(self, voice_message_id: int) -> int:
    logger.info(
        f"Try to send request for transcription task from voice message #{voice_message_id}"
    )

    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        service = SpeechToTextService()
        operation_id = service.transcribe_async_start(voice_message.S3_path)
        voice_message.stt_operation_id = operation_id
        voice_message.save()
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)
    return voice_message_id


@app.task(bind=True)
def master_voice_message_task(self, voice_message_id: int):
    voice_message = VoiceMessage.objects.get(pk=voice_message_id)
    if voice_message.duration < 30:
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
    else:
        chain(
            send_confirmation_voice.s(voice_message_id),
            upload_long_voice.s(),
            call_stt_api_async.s(),
            # TODO: check if done and save results
            # TODO: delete file from bucket
            group(
                delete_confirmation_voice.s(),
            ),
        ).apply_async()
