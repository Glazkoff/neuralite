from pydantic import BaseModel


class AudioSyncTask(BaseModel):
    voice_message_url: str
    text: str = ""
