"""Pydantic schemas for /api/v1/compare endpoint."""

from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    prompt: str = Field(..., min_length=10, description="Prompt / task for all models")
    system_prompt: str = Field(default="", description="Optional system prompt")
    model_ids: list[str] | None = Field(
        default=None,
        description="Subset of model IDs to run. None = all models.",
    )
    free_only: bool = Field(default=False, description="Run only free-tier models")


class EvalBreakdown(BaseModel):
    length: int
    first_person: int
    digits: int
    structure: int
    no_opener: int
    readability: int
    ai_isms_penalty: int


class ModelResultResponse(BaseModel):
    model_id: str
    display_name: str
    provider: str
    is_free: bool
    text: str
    elapsed_sec: float
    error: str
    score: int | None
    zone: str | None        # "Green" | "Orange" | "Red" | None (on error)
    breakdown: EvalBreakdown | None
    ai_isms_found: list[str]


class CompareResponse(BaseModel):
    results: list[ModelResultResponse]
    total_models: int
    successful: int
    prompt: str
