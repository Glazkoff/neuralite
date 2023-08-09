from pydantic import BaseModel


class SummarizationTaskCreate(BaseModel):
    text: str


class SummarizationTaskResponse(BaseModel):
    id: int
    text: str
    ai_summarization: str
    done: bool
