import requests


class SummarizationService:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def summarize(self, text: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"text": text}

        try:
            response = requests.post(self.api_url, json=data, headers=headers)

            if response.status_code == 200:
                json_response = response.json()
                return json_response.get("ai_summarization", None)

            else:
                raise APIError(f"Request failed with status {response.status_code}")

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e


class APIError(Exception):
    pass
