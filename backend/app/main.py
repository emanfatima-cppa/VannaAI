"""app/main.py – FastAPI entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import auth, query, training, share

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cortexaai")
settings = get_settings()

app = FastAPI(
    title="Vanna AI – Multi-DB NL Query API",
    version="1.0.0",
    description="Natural language to SQL with role-based access, context memory, and feedback-driven training.",
)

@app.on_event("startup")
def on_startup():
    from app.db.auth_db import init_db
    logger.info("=" * 55)
    logger.info("  Vanna AI – Backend Starting Up")
    logger.info("=" * 55)
    logger.info(f"  CORS allowed origins: {_CORS_ORIGINS}")
    logger.info("-" * 55)
    logger.info("  Connecting to PostgreSQL auth database...")
    try:
        init_db()
        logger.info("  ✅ PostgreSQL auth DB connected and initialized OK")
    except Exception as e:
        logger.error(f"  ❌ PostgreSQL auth DB FAILED to initialize: {e}")
    logger.info("=" * 55)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Covers all ports Vite may choose (5173-5176) on localhost and network IP
_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://192.168.11.232:5173",
    "http://192.168.11.232:5174",
    "http://192.168.11.232:5175",
    "http://192.168.11.232:5176",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(query.router)
app.include_router(training.router)
app.include_router(share.router)


@app.get("/")
async def root():
    return {"message": "Vanna AI API is running", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}