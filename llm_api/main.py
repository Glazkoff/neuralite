import openai
from fastapi import FastAPI
from .models import SummarizationTask
from .api_requests import summarization_from_openai

app = FastAPI()

openai.api_key = "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"

tasks = [
    {
        "id": 0,
        "message": "test",
    }
]


@app.get("/tasks/")
async def read_tasks():
    return tasks


@app.post("/tasks/")
async def create_task(task: SummarizationTask):
    try:
        result = await summarization_from_openai(task)
        task.ai_summarization = result
    except Exception as e:
        task.ai_summarization = e

    tasks.append(task)
    return {"id": len(tasks), "ai_summarization": task.ai_summarization}
