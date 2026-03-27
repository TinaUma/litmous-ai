"""LLM provider protocol — common interface for text generation."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        max_tokens: int = 2000,
    ) -> str:
        """Generate text from a prompt."""
        ...
