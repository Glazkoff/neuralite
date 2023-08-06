from pydantic import BaseModel


class SummarizationTask(BaseModel):
    id: int = 0
    text: str
    ai_summarization: str = ""
    done: bool = False
