from pydantic import BaseModel


class AudioTaskCreate(BaseModel):
    voice_message_url: str


class AudioTaskResponse(BaseModel):
    text: str
