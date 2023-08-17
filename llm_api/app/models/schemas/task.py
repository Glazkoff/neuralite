from pydantic import BaseModel


class SummarizationTaskCreate(BaseModel):
    text: str


class SummarizationTaskResponse(BaseModel):
    text: str
    ai_summarization: str
    extracted_facts: str = ""
