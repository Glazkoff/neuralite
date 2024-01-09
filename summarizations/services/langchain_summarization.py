import requests

from .common import LANGCHAIN_LLM_API_URL, APIError


class LangchainSummarizationService:
    def __init__(
        self,
        api_url: str = f"{LANGCHAIN_LLM_API_URL}/summ/invoke",
    ):
        self.api_url = api_url

    def summarize(self, text: str) -> (str, str):
        headers = {"Content-Type": "application/json"}
        data = {"input": {"context": text}, "config": {}, "kwargs": {}}

        try:
            response = requests.post(self.api_url, json=data, headers=headers)

            if response.status_code != 200:
                raise APIError(f"Request failed with status {response.status_code}")

            json_response = response.json()
            # return json_response.get("ai_summarization", None), json_response.get(
            #     "extracted_facts", None
            # )
            return json_response.get("output", None), "TEST: будет позже"

        except requests.RequestException as e:
            raise APIError(f"Error calling API: {str(e)}") from e
