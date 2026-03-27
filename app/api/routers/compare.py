"""Compare endpoint — POST /api/v1/compare runs multiple LLMs in parallel."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.api.schemas.compare import CompareRequest, CompareResponse, ModelResultResponse, EvalBreakdown
from app.services.llm_compare import run_comparison

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/compare", tags=["compare"])


@router.post("", response_model=CompareResponse)
async def compare_models(
    body: CompareRequest,
) -> CompareResponse:
    """Run a prompt through multiple LLMs in parallel and return scored results."""
    try:
        results = await run_comparison(
            body.prompt,
            system_prompt=body.system_prompt,
            model_ids=body.model_ids,
            free_only=body.free_only,
        )
    except Exception as exc:
        logger.exception("compare failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    items: list[ModelResultResponse] = []
    for r in results:
        breakdown = None
        ai_isms: list[str] = []
        score = None
        zone = None
        if r.eval:
            bd = r.eval.breakdown
            breakdown = EvalBreakdown(
                length=bd.get("length", 0),
                first_person=bd.get("first_person", 0),
                digits=bd.get("digits", 0),
                structure=bd.get("structure", 0),
                no_opener=bd.get("no_opener", 0),
                readability=bd.get("readability", 0),
                ai_isms_penalty=bd.get("ai_isms_penalty", 0),
            )
            ai_isms = r.eval.ai_isms_found
            score = r.eval.score
            zone = r.eval.zone

        items.append(ModelResultResponse(
            model_id=r.model_id,
            display_name=r.display_name,
            provider=r.provider,
            is_free=r.is_free,
            text=r.text,
            elapsed_sec=r.elapsed_sec,
            error=r.error,
            score=score,
            zone=zone,
            breakdown=breakdown,
            ai_isms_found=ai_isms,
        ))

    successful = sum(1 for r in results if r.ok)
    return CompareResponse(
        results=items,
        total_models=len(items),
        successful=successful,
        prompt=body.prompt,
    )
