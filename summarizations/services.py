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


class SpeechToTextService:
    def __init__(
        self,
        api_url_sync: str = f"{BASE_LLM_API_URL}/stt/sync/",
        api_url_async: str = f"{BASE_LLM_API_URL}/stt/async/",
    ):
        self.api_url_sync = api_url_sync
        self.api_url_async = api_url_async

    def transcribe_sync(self, voice_message_url: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"voice_message_url": voice_message_url}

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


class StorageService:
    def __init__(
        self,
        upload_file_url_base: str = f"{BASE_LLM_API_URL}/upload/",
        upload_from_link_url: str = f"{BASE_LLM_API_URL}/upload/from_url/",
    ):
        self.upload_file_url_base = upload_file_url_base
        self.upload_from_link_url = upload_from_link_url

    def upload_file(self, file: bytes, key: str) -> str:
        headers = {"Content-Type": "application/octet-stream"}

        try:
            response = requests.post(
                f"{self.upload_file_url_base}{key}", data=file, headers=headers
            )

            if response.status_code != 200:
                raise APIError(f"Upload failed with status {response.status_code}")

            return response.json()["file_key"]

        except requests.RequestException as e:
            raise APIError(f"Error uploading file: {str(e)}") from e

    def upload_from_url(self, file_url: str, key: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"file_url": file_url, "key": key}

        try:
            response = requests.post(
                self.upload_from_link_url, json=data, headers=headers
            )

            if response.status_code != 200:
                raise APIError(f"Request failed with status {response.status_code}")

            json_response = response.json()
            return json_response.get("path", None)

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e


class APIError(Exception):
    pass
