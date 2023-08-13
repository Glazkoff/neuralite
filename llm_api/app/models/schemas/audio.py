from pydantic import BaseModel
from typing import Optional


class AudioTaskCreate(BaseModel):
    file_url: str


class AudioTaskResponse(BaseModel):
    text: str


class AudioTaskAsyncCreate(BaseModel):
    S3_path: str


class AudioTaskAsyncResponse(BaseModel):
    operation_id: str


class AudioTaskAsyncResults(BaseModel):
    done: bool
    text: Optional[str] = None
