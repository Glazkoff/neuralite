from pydantic import BaseModel

class StorageUpload(BaseModel):
    file: str
