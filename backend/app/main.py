"""app/main.py – FastAPI entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import auth, query, training

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title="Vanna AI – Multi-DB NL Query API",
    version="1.0.0",
    description="Natural language to SQL with role-based access, context memory, and feedback-driven training.",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(query.router)
app.include_router(training.router)


@app.get("/")
async def root():
    return {"message": "Vanna AI API is running", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}