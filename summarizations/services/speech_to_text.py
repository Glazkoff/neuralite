import requests

from .common import BASE_LLM_API_URL, APIError


class SpeechToTextService:
    def __init__(
        self,
        api_url_sync: str = f"{BASE_LLM_API_URL}/stt/sync/",
        api_url_async: str = f"{BASE_LLM_API_URL}/stt/async/",
    ):
        self.api_url_sync = api_url_sync
        self.api_url_async = api_url_async

    def transcribe_sync(self, file_url: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"file_url": file_url}

        try:
            response = requests.post(self.api_url_sync, json=data, headers=headers)

            if response.status_code != 200:
                raise APIError(f"Request failed with status {response.status_code}")

            json_response = response.json()
            return json_response.get("text", None)

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e

    def transcribe_async_start(self, s3_path: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"S3_path": s3_path}

        try:
            response = requests.post(self.api_url_async, json=data, headers=headers)

            if response.status_code != 200:
                raise APIError(f"Request failed with status {response.status_code}")

            json_response = response.json()
            return json_response.get("operation_id", None)

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e

    def transcribe_async_results(self, operation_id: str) -> (bool, [str, None]):
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.get(
                f"{self.api_url_async}{operation_id}", headers=headers
            )

            if response.status_code != 200:
                raise APIError(f"Request failed with status {response.status_code}")

            json_response = response.json()
            return json_response.get("done", False), json_response.get("text", None)

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e
