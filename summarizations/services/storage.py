import requests

from .common import BASE_LLM_API_URL, APIError


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

    def delete_file(self, key: str) -> bool:
        headers = {}

        try:
            response = requests.delete(
                f"{self.upload_file_url_base}{key}", headers=headers
            )

            if response.status_code != 200:
                raise APIError(f"Deleting failed with status {response.status_code}")

            return response.json()["success"]

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
