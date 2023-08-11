import os
import telegram
import requests
from telegram import ParseMode, Update, Voice
from telegram.ext import CallbackContext

from tgbot.handlers.summarize import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from summarizations.models import SummarizationTask
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
    voice: Voice = update.message.voice
    # Получаем из него ID файла аудиосообщения
    file_id = voice.file_id
    # Получаем всю информацию о данном файле
    voice_file = context.bot.get_file(file_id)
    duration = voice.duration
    # А уже из нее достаем путь к файлу на сервере Телеграм в директории
    # с файлами нашего бота
    voice_path = voice_file.file_path
    # TODO: сохранять сущность аудиосообщения в БД и привязывать задачу распознавания
    message = f"Длительность аудио: <b>{duration}c</b>\n---\n"
    if duration <= 30:
        speech_text = get_text_from_speech_sync(voice_path)
        message += f"Текст аудио:\n{speech_text}"

        if speech_text != "":
            user = User.get_user(update, context)
            task = {
                "user": user,
                "input_text": speech_text,
                "user_telegram_msg_id": update.message.message_id,
            }
            SummarizationTask.objects.create(**task)
    else:
        # TODO: асинхронное распознавание аудио
        message += (
            "<i>Распознавание аудиосоообщений больше 30 секунд появится позже</i>"
        )
    context.bot.send_message(
        update.message.chat.id, text=message, parse_mode=ParseMode.HTML
    )


def get_text_from_speech_sync(file_url):
    # TODO: вынести в отдельный сервис
    # URL для отправки аудиофайла на распознавание
    STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    YC_STT_API_KEY = os.environ.get("YC_STT_API_KEY")

    # Выполняем GET-запрос по ссылке на аудиофайл
    response = requests.get(file_url)

    # Если запрос к серверу Telegram не удался...
    if response.status_code != 200:
        return None

    # Получаем из ответа запроса наш аудиофайл
    audio_data = response.content

    # Создам заголовок с API-ключом для Яндекс.Облака, который пошлем в запросе
    headers = {"Authorization": f"Api-Key {YC_STT_API_KEY}"}

    # Отправляем POST-запрос на сервер Яндекс, который занимается расшифровкой аудио,
    # передав его URL, заголовок и сам файл аудиосообщения
    response = requests.post(STT_URL, headers=headers, data=audio_data)

    # Если запрос к Яндекс.Облаку не удался...
    if not response.ok:
        print("response.status_code", response.status_code)
        print("response.content", response.content)
        return None

    # Преобразуем JSON-ответ сервера в объект Python
    result = response.json()
    # Возвращаем текст аудиосообщения
    return result.get("result")
