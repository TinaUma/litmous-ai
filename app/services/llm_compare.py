"""LLM comparison service — runs multiple models in parallel and scores their output."""

import asyncio
import os
import time
from dataclasses import dataclass, field

from app.providers.llm.grok import GrokProvider
from app.providers.llm.openrouter import OpenRouterProvider
from app.providers.llm.yandexgpt import YandexGPTProvider
from app.services.post_evaluator import EvalResult, evaluate


@dataclass(frozen=True)
class ModelConfig:
    id: str             # unique slug used in results
    display_name: str   # human-readable
    provider: str       # "openrouter" | "grok" | "yandex"
    model_id: str       # exact model ID sent to API
    is_free: bool = False


MODELS: list[ModelConfig] = [
    # Via OpenRouter (paid)
    ModelConfig(id="gpt-4o",            display_name="GPT-4o",            provider="openrouter", model_id="openai/gpt-4o"),
    ModelConfig(id="gpt-4o-mini",       display_name="GPT-4o mini",       provider="openrouter", model_id="openai/gpt-4o-mini"),
    ModelConfig(id="claude-3-5-sonnet", display_name="Claude 3.5 Sonnet", provider="openrouter", model_id="anthropic/claude-3.5-sonnet"),
    # Via OpenRouter (free)
    ModelConfig(id="llama-3-3-70b",     display_name="Llama 3.3 70B",     provider="openrouter", model_id="meta-llama/llama-3.3-70b-instruct:free",   is_free=True),
    ModelConfig(id="deepseek-v3",       display_name="DeepSeek V3",       provider="openrouter", model_id="deepseek/deepseek-chat:free",              is_free=True),
    # Direct APIs
    ModelConfig(id="grok-2",            display_name="Grok-2",            provider="grok",       model_id="grok-2-1212"),
    ModelConfig(id="yandexgpt",         display_name="YandexGPT 3",       provider="yandex",     model_id="yandexgpt"),
]


@dataclass
class ModelResult:
    model_id: str
    display_name: str
    provider: str
    is_free: bool
    text: str = ""
    elapsed_sec: float = 0.0
    error: str = ""
    eval: EvalResult | None = None

    @property
    def ok(self) -> bool:
        return not self.error and bool(self.text)


def _build_provider(cfg: ModelConfig):
    if cfg.provider == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        return OpenRouterProvider(api_key=api_key, model=cfg.model_id)

    if cfg.provider == "grok":
        api_key = os.environ.get("GROK_API_KEY", "")
        if not api_key:
            raise ValueError("GROK_API_KEY is not set")
        return GrokProvider(api_key=api_key, model=cfg.model_id)

    if cfg.provider == "yandex":
        api_key = os.environ.get("YANDEXGPT_API_KEY", "")
        folder_id = os.environ.get("YANDEX_FOLDER_ID", "")
        if not api_key or not folder_id:
            raise ValueError("YANDEXGPT_API_KEY or YANDEX_FOLDER_ID is not set")
        return YandexGPTProvider(api_key=api_key, folder_id=folder_id, model=cfg.model_id)

    raise ValueError(f"Unknown provider: {cfg.provider}")


async def _run_one(cfg: ModelConfig, prompt: str, system_prompt: str) -> ModelResult:
    result = ModelResult(
        model_id=cfg.id,
        display_name=cfg.display_name,
        provider=cfg.provider,
        is_free=cfg.is_free,
    )
    try:
        provider = _build_provider(cfg)
        start = time.monotonic()
        result.text = await provider.generate(
            prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
        )
        result.elapsed_sec = round(time.monotonic() - start, 2)
        result.eval = evaluate(result.text)
    except Exception as exc:  # noqa: BLE001
        result.error = str(exc)
    return result


async def _run_one_delayed(cfg: ModelConfig, prompt: str, system_prompt: str, delay: float) -> ModelResult:
    if delay > 0:
        await asyncio.sleep(delay)
    return await _run_one(cfg, prompt, system_prompt)


async def run_comparison(
    prompt: str,
    *,
    system_prompt: str = "",
    model_ids: list[str] | None = None,
    free_only: bool = False,
) -> list[ModelResult]:
    """Run selected models on a prompt in parallel.

    Free OpenRouter models are staggered by 0.7s to avoid 429 rate limits.

    Args:
        prompt: The user prompt / task for each model.
        system_prompt: Optional system prompt prepended to all models.
        model_ids: Subset of model IDs to run. Defaults to all MODELS.
        free_only: If True, only free-tier models.

    Returns:
        List of ModelResult sorted by score descending (errors last).
    """
    pool = MODELS
    if model_ids is not None:
        pool = [m for m in pool if m.id in model_ids]
    if free_only:
        pool = [m for m in pool if m.is_free]

    # Stagger free OpenRouter requests to avoid rate limits (429)
    free_delay = 0.0
    tasks = []
    for cfg in pool:
        delay = 0.0
        if cfg.is_free and cfg.provider == "openrouter":
            delay = free_delay
            free_delay += 0.7
        tasks.append(_run_one_delayed(cfg, prompt, system_prompt, delay))

    results = await asyncio.gather(*tasks)

    def sort_key(r: ModelResult) -> int:
        return r.eval.score if r.ok and r.eval else -1

    return sorted(results, key=sort_key, reverse=True)
