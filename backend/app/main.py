from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router as main_router
from app.api.auth_routes import router as auth_router
from app.api.analysis_routes import router as analysis_router
from app.api.report_routes import router as report_router
from app.database.database import init_db
from app.middleware.security import (
    RateLimitMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create SQLite tables if they do not exist.
    init_db()
    yield


app = FastAPI(
    title="EmailShield AI",
    version="1.0",
    lifespan=lifespan,
)


# ============================================================
# Security Middleware
# ============================================================

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RateLimitMiddleware)

# ============================================================
# API Routers
# ============================================================

app.include_router(main_router)
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(report_router)
