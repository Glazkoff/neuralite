import os
import boto3
import requests
from io import BytesIO
from typing import Dict, BinaryIO

S3_URL = "https://storage.yandexcloud.net"


class StorageService:
    def __init__(self) -> None:
        YC_S3_ACCESS_KEY_ID = os.environ.get("YC_S3_ACCESS_KEY_ID")
        YC_S3_SECRET_ACCESS_KEY = os.environ.get("YC_S3_SECRET_ACCESS_KEY")
        session = boto3.session.Session(
            aws_access_key_id=YC_S3_ACCESS_KEY_ID,
            aws_secret_access_key=YC_S3_SECRET_ACCESS_KEY,
            region_name="ru-central1",
        )

        self.bucket = "neuralite-voice"
        self.s3 = session.client(service_name="s3", endpoint_url=S3_URL)

    def upload_file(self, file: BinaryIO, key: str, metadata: Dict = None) -> str:
        """Upload a file-like object to S3"""
        extra_args = metadata or {}
        self.s3.upload_fileobj(file, self.bucket, key, ExtraArgs=extra_args)
        return key

    def upload_from_url(self, file_url: str, key: str) -> [str, None]:
        # Выполняем GET-запрос по ссылке на аудиофайл
        response = requests.get(file_url)

        # Если запрос к серверу Telegram не удался...
        if response.status_code != 200:
            return None

        # Получаем из ответа запроса наш аудиофайл
        file_data = response.content
        file_stream = BytesIO(file_data)

        return self.upload_file(file_stream, key=key)

    def delete_object(self, key: str) -> None:
        """Delete object from S3 bucket"""

        self.s3.delete_object(Bucket=self.bucket, Key=key)
