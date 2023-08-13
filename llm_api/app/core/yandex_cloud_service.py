import os
import json
import requests
from .storage_service import S3_URL

# URL для отправки аудиофайла на распознавание
STT_SYNC_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
STT_ASYNC_START_URL = (
    "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize"
)


class YandexCloudService:
    def __init__(self):
        self.YC_STT_API_KEY = os.environ.get("YC_STT_API_KEY")

    def get_text_from_speech_sync(self, file_url: str) -> [str, None]:
        # Выполняем GET-запрос по ссылке на аудиофайл
        response = requests.get(file_url)

        # Если запрос к серверу Telegram не удался...
        if response.status_code != 200:
            return None

        # Получаем из ответа запроса наш аудиофайл
        audio_data = response.content

        # Создам заголовок с API-ключом для Яндекс.Облака, который пошлем в запросе
        headers = {"Authorization": f"Api-Key {self.YC_STT_API_KEY}"}

        # Отправляем POST-запрос на сервер Яндекс, который занимается расшифровкой аудио,
        # передав его URL, заголовок и сам файл аудиосообщения
        response = requests.post(STT_SYNC_URL, headers=headers, data=audio_data)

        # Если запрос к Яндекс.Облаку не удался...
        if not response.ok:
            return None

        # Преобразуем JSON-ответ сервера в объект Python
        result = response.json()

        # Возвращаем текст аудиосообщения
        return result.get("result")

    def start_async_stt(self, s3_path: str) -> [str, None]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.YC_STT_API_KEY}",
        }
        data = {
            "config": {},
            "audio": {"uri": f"{S3_URL}/{s3_path}"},
        }

        # Выполняем POST-запрос на создание задачи
        response = requests.post(
            STT_ASYNC_START_URL, data=json.dumps(data), headers=headers
        )

        # Если запрос к Яндекс.Облаку не удался...
        if not response.ok:
            return None

        # Преобразуем JSON-ответ сервера в объект Python
        result = response.json()

        # Возвращаем ID операции в облаке
        return result.get("id")

    def check_async_stt(self, operation_id: str) -> [bool, None]:
        # TODO
        pass

    # def
