import os
import requests

# URL для отправки аудиофайла на распознавание
STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"


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
