import openai
from models import SummarizationTask


async def summarization_from_openai(task: SummarizationTask):
    messages = [
        {
            "content": "Create a summary capturing the main points and key details of text.",
            "role": "system",
        },
        {
            "role": "user",
            "content": task.text,
        },
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message.get("content", "")
