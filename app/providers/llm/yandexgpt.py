"""YandexGPT LLM provider."""

import re

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def _strip_code_fence(text: str) -> str:
    """Strip markdown code fences that YandexGPT sometimes wraps responses in.

    Handles: ```html\\n...\\n``` or ```\\n...\\n```
    """
    text = text.strip()
    match = re.match(r"^```[^\n]*\n(.*?)```\s*$", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


class YandexGPTProvider:
    def __init__(self, api_key: str, folder_id: str, model: str = "yandexgpt-lite") -> None:
        self.api_key = api_key
        self.folder_id = folder_id
        self.model_uri = f"gpt://{folder_id}/{model}"
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        max_tokens: int = 2000,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "text": system_prompt})
        messages.append({"role": "user", "text": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/completion",
                headers={
                    "Authorization": f"Api-Key {self.api_key}",
                    "x-folder-id": self.folder_id,
                },
                json={
                    "modelUri": self.model_uri,
                    "completionOptions": {
                        "maxTokens": max_tokens,
                        "stream": False,
                    },
                    "messages": messages,
                },
            )
            response.raise_for_status()
            data = response.json()
            raw = data["result"]["alternatives"][0]["message"]["text"]
            return _strip_code_fence(raw)
