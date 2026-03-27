"""Grok (xAI) LLM provider — OpenAI-compatible API."""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class GrokProvider:
    def __init__(self, api_key: str, model: str = "grok-3-mini-fast") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.x.ai/v1"

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
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
