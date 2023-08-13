from pydantic import BaseModel


class AudioTaskCreate(BaseModel):
    file_url: str


class AudioTaskUploadCreate(AudioTaskCreate):
    key: str


class AudioTaskResponse(BaseModel):
    text: str


class AudioTaskUploadResponse(BaseModel):
    path: str
