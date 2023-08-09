from fastapi import FastAPI

from llm_api.app.api.endpoints import tasks

app = FastAPI()

# app.include_router(tasks.router, prefix="/api")
app.include_router(tasks.router)
