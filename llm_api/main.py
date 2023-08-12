from fastapi import FastAPI

from llm_api.app.api.endpoints import tasks
from llm_api.app.api.endpoints import audio
from llm_api.app.api.endpoints import storage

app = FastAPI()

# app.include_router(tasks.router, prefix="/api")
app.include_router(tasks.router)
app.include_router(audio.router)
app.include_router(storage.router)
