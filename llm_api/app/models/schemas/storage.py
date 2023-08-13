from pydantic import BaseModel
from .audio import AudioTaskCreate


class StorageUpload(BaseModel):
    file: str


class FileUploadCreate(AudioTaskCreate):
    key: str


class FileUploadResponse(BaseModel):
    path: str
