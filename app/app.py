"""FastAPI application entrypoint.

Run with:
    uvicorn app.app:app --reload

Modules here only construct the FastAPI instance, register middleware
and include routers. Business logic lives in app/core and app/ai.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.template_converter import router as template_converter_router
from app.config.settings import Paths


@asynccontextmanager
async def lifespan(app: FastAPI):
    Paths().ensure()
    yield


app = FastAPI(
    title="Template Beautifier API",
    description="Convert input PPTX decks into styled output decks using a template.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(template_converter_router)

@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}