import os
import openai


class OpenAIService:
    def __init__(self):
        token = os.environ.get("OPEN_AI_TOKEN")
        openai.api_key = token

    def generate_summary(self, text: str) -> str:
        messages = [
            {
                "content": "Create a summary capturing the main points and key details of text.",
                "role": "system",
            },
            {"role": "user", "content": text},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return response.choices[0].message.get("content", "")
