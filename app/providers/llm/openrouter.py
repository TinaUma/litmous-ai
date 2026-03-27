"""OpenRouter provider — unified OpenAI-compatible gateway for GPT, Claude, Llama, DeepSeek."""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class OpenRouterProvider:
    """Single async client for all OpenRouter models.

    Compatible with LLMProvider protocol. Pass any model_id from openrouter.ai/models.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model

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

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/yumacontentposter",
                    "X-Title": "YumaContentPoster",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
