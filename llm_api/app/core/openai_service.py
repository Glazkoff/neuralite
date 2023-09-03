import os
import openai


class OpenAIService:
    def __init__(self):
        token = os.environ.get("OPEN_AI_TOKEN")
        openai.api_key = token

    def generate_summary(self, text: str) -> str:
        messages = [
            {
                "content": f"Could you please provide a summary of the given text, including all key points and supporting details? The summary should be comprehensive and accurately reflect the main message and arguments presented in the original text, while also being concise and easy to understand. To ensure accuracy, please read the text carefully and pay attention to any nuances or complexities in the language. Ensure that the meaning of the original text is not changed. Additionally, the summary should avoid any personal biases or interpretations and remain objective and factual throughout. If the text does not contain any information, then simply write \"Нет информации.\". Use only neutral language. Write only in Russian. Please execute the command for the following text: '{text}'",
                "role": "system",
            },
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
        )
        return response.choices[0].message.get("content", "")

    def extract_facts(self, text: str) -> str:
        messages = [
            {
                "content": f"Your task is to extract facts from the text I give you in up to 10 bulletpoints. Pick a corresponding number emoji (like 1, 2, 3) for each bullet point. To ensure accuracy, please read the text carefully and pay attention to any nuances or complexities in the language. Additionally, the summary should avoid any personal biases or interpretations and remain objective and factual throughout. Sort list by importance of fact. Use only neutral language. If the text does not contain any information, then simply write \"Нет информации.\". Reply in Russian. Please execute the command for the following text: '{text}'",
                "role": "system",
            },
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
        )
        return response.choices[0].message.get("content", "")
