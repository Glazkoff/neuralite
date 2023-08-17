import os
import openai


class OpenAIService:
    def __init__(self):
        token = os.environ.get("OPEN_AI_TOKEN")
        openai.api_key = token

    def generate_summary(self, text: str) -> str:
        messages = [
            {
                "content": "Could you please provide a summary of the given text, including all key points and supporting details? The summary should be comprehensive and accurately reflect the main message and arguments presented in the original text, while also being concise and easy to understand. To ensure accuracy, please read the text carefully and pay attention to any nuances or complexities in the language. Additionally, the summary should avoid any personal biases or interpretations and remain objective and factual throughout. Use only neutral language. Write only in Russian. Text:",
                "role": "system",
            },
            {"role": "user", "content": text},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return response.choices[0].message.get("content", "")

    def extract_facts(self, text: str) -> str:
        messages = [
            {
                "content": "Your task is to extract facts from the text I give you in up to 10 bulletpoints. Pick a corresponding number emoji (like 1, 2, 3) for each bullet point. To ensure accuracy, please read the text carefully and pay attention to any nuances or complexities in the language. Additionally, the summary should avoid any personal biases or interpretations and remain objective and factual throughout. Sort list by importance of fact. Use only neutral language. Reply in Russian.",
                "role": "system",
            },
            {"role": "user", "content": text},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return response.choices[0].message.get("content", "")
