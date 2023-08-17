from pydantic import BaseModel


class SummarizationTask(BaseModel):
    text: str
    ai_summarization: str = ""
    extracted_facts: str = ""
