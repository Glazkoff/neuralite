import requests

BASE_LLM_API_URL = "http://dtb.llm-api:8001"


class SummarizationService:
    def __init__(
        self,
        api_url: str = f"{BASE_LLM_API_URL}/tasks/",
    ):
        self.api_url = api_url

    def summarize(self, text: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"text": text}

        try:
            response = requests.post(self.api_url, json=data, headers=headers)

            if response.status_code != 200:
                raise APIError(f"Request failed with status {response.status_code}")

            json_response = response.json()
            return json_response.get("ai_summarization", None)

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e


class TranscribationService:
    def __init__(
        self,
        api_url: str = f"{BASE_LLM_API_URL}/stt/sync/",
    ):
        self.api_url = api_url

    def transcribe_sync(self, voice_message_url: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"voice_message_url": voice_message_url}

        try:
            response = requests.post(self.api_url, json=data, headers=headers)

            if response.status_code != 200:
                raise APIError(f"Request failed with status {response.status_code}")

            json_response = response.json()
            return json_response.get("text", None)

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e


class APIError(Exception):
    pass
