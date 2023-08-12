import os
import boto3
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
