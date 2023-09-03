from celery import chain, group
from telegram import ParseMode
from dtb.celery import app
from summarizations.models import SummarizationTask, VoiceMessage
from summarizations.services.speech_to_text import SpeechToTextService
from summarizations.services.storage import StorageService
from summarizations.services.common import APIError
from celery.utils.log import get_task_logger
from tgbot.handlers.broadcast_message.utils import send_one_message, delete_one_message
from tgbot.handlers.summarize import static_text as static_text
from .utils import get_voice_massage_key

logger = get_task_logger(__name__)


def register_transcription_for_vm(voice_message: VoiceMessage, text: str):
    summarization_task = SummarizationTask.objects.create(
        user_telegram_msg_id=voice_message.user_telegram_msg_id,
        user=voice_message.user,
        input_text=text,
    )

    voice_message.summarization_task = summarization_task
    voice_message.transcribed_text = text
    voice_message.transcribed = True
    voice_message.save()


@app.task(bind=True, max_retries=3, retry_backoff=True)
def send_confirmation_voice(self, voice_message_id: int) -> int:
    logger.info(
        f"[{self.request.retries}] Try to send confirmation for voice message #{voice_message_id}"
    )
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
    logger.info(
        f"[{self.request.retries}] Call STT API for voice summarization #{voice_message_id}"
    )
    voice_message = VoiceMessage.objects.get(pk=voice_message_id)

    try:
        service = SpeechToTextService()
        transcription = service.transcribe_sync(voice_message.voice_path)

        register_transcription_for_vm(voice_message, transcription)
        logger.info("API call completed")
    except APIError as e:
        logger.error(f"Error transcribing text: {e}")
        raise self.retry(exc=e) from e

    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def send_result_voice(self, voice_message_id: int) -> int:
    logger.info(
        f"[{self.request.retries}] Try to send result for voice message #{voice_message_id}"
    )
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
        logger.info("Results were sent successfully")
    else:
        logger.error("Error while sending message with results")
        self.retry()

    return voice_message_id


@app.task(bind=True, max_retries=1, retry_backoff=True)
def delete_confirmation_voice(self, voice_message_id: int) -> int:
    logger.info(
        f"[{self.request.retries}] Try to delete service message from voice message #{voice_message_id}"
    )
    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        if _ := delete_one_message(
            voice_message.user.user_id,
            message_to_delete_id=voice_message.bot_telegram_msg_id,
        ):
            voice_message.done = True
            voice_message.save()
            logger.info("Message was deleted successfully")
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)
    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def upload_long_voice(self, voice_message_id: int) -> int:
    logger.info(
        f"[{self.request.retries}] Try to send file to S3 storage from voice message #{voice_message_id}"
    )

    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        service = StorageService()
        path = service.upload_from_url(
            voice_message.voice_path, get_voice_massage_key(voice_message)
        )
        voice_message.S3_path = path
        voice_message.save()
        logger.info("Voice message was uploaded successfully")
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)
    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def call_stt_api_async(self, voice_message_id: int) -> int:
    logger.info(
        f"[{self.request.retries}] Try to send request for transcription task from voice message #{voice_message_id}"
    )

    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        service = SpeechToTextService()
        operation_id = service.transcribe_async_start(voice_message.S3_path)
        voice_message.stt_operation_id = operation_id
        voice_message.save()
        logger.info("Task on async STT was started successfully")
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)
    return voice_message_id


@app.task(bind=True, retry_backoff=True)
def try_get_results_async(self, voice_message_id: int) -> int:
    logger.info(
        f"[{self.request.retries}] Try to send request for getting transcription results from voice message #{voice_message_id}"
    )

    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        if not voice_message.transcribed:
            service = SpeechToTextService()
            done, text_result = service.transcribe_async_results(
                voice_message.stt_operation_id
            )

            if not done:
                logger.error("Not ready")
                raise self.retry(countdown=10)

            register_transcription_for_vm(voice_message, text_result)
            logger.info("Task on async STT was ended successfully")
        else:
            # Stop the chain
            self.request.chain = None
            self.request.callbacks = None
            return voice_message_id
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)

    return voice_message_id


@app.task(bind=True, max_retries=3, retry_backoff=True)
def delete_storage_file(self, voice_message_id: int) -> int:
    logger.info(
        f"[{self.request.retries}] Try to delete storage file from voice message #{voice_message_id}"
    )
    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        service = StorageService()

        _, _, key = voice_message.S3_path.partition("/")
        service.delete_file(key)
        logger.info(f"File with key - '{key}' - deleted successfully")
    except Exception as e:
        logger.error(f"Error: {e}")
        self.retry(exc=e)
    return voice_message_id


@app.task(bind=True)
def master_voice_message_task(self, voice_message_id: int):
    try:
        voice_message = VoiceMessage.objects.get(pk=voice_message_id)
        if voice_message.transcribed:
            return None
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
            ).delay()
        else:
            chain(
                send_confirmation_voice.s(voice_message_id),
                # TODO: diarization
                upload_long_voice.s(),
                call_stt_api_async.s(),
                # TODO: transform STT to dialog format
                try_get_results_async.s(),
                group(
                    send_result_voice.s(),
                    delete_confirmation_voice.s(),
                    delete_storage_file.s(),
                ),
            ).delay()
    except Exception as e:
        logger.error(f"Error: {e}")
    return None
