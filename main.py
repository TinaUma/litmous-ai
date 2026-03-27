"""Litmous.ai — LLM arena and content quality analyzer."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import compare

app = FastAPI(title="Litmous.ai", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compare.router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
