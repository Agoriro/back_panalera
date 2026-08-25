# Paso 18: src/main.py
import asyncio
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from src.interfaces.api.dependencies.database import engine
from src.interfaces.api.v1.routers.auth import limiter
from src.interfaces.api.v1.routers.auth import router as auth_router
from src.interfaces.api.v1.routers.catalog import router as catalog_router
from src.interfaces.api.v1.routers.inventory import router as inventory_router
from src.interfaces.api.v1.routers.movements import router as movements_router
from src.interfaces.api.v1.routers.reports import router as reports_router
from src.interfaces.api.v1.routers.roles import router as roles_router
from src.interfaces.api.v1.routers.users import router as users_router
from src.shared.config.settings import settings
from src.shared.exceptions.domain_exceptions import (
    BusinessRuleValidationException,
    DomainException,
    ForbiddenException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
    UnauthorizedException,
)
from src.shared.logging.logger import get_logger, setup_logging

# Configurar logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Panalera Backend API",
    description="API para la gestión de inventario y ventas de Panalera",
    version="0.1.0",
)

app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middlewares personalizados (Request Logging y Secure Headers)
@app.middleware("http")
async def add_security_headers_and_log(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time_ms = (time.time() - start_time) * 1000
    logger.info(
        "request_processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time_ms=f"{process_time_ms:.2f}",
    )

    # Secure headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    return response


# Manejadores de excepciones
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests"},
    )


@app.exception_handler(ResourceNotFoundException)
async def not_found_handler(request: Request, exc: ResourceNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
    )


@app.exception_handler(ResourceAlreadyExistsException)
async def already_exists_handler(request: Request, exc: ResourceAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message}
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exc.message}
    )


@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": exc.message}
    )


@app.exception_handler(BusinessRuleValidationException)
async def business_rule_handler(request: Request, exc: BusinessRuleValidationException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


@app.exception_handler(DomainException)
async def domain_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
    )


# Incluir routers
api_v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(roles_router, prefix=api_v1_prefix)
app.include_router(users_router, prefix=api_v1_prefix)
app.include_router(catalog_router, prefix=api_v1_prefix)
app.include_router(inventory_router, prefix=api_v1_prefix)
app.include_router(movements_router, prefix=api_v1_prefix)
app.include_router(reports_router, prefix=api_v1_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    """Compatibilidad: confirma que proceso HTTP está vivo."""
    return {"status": "ok"}


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness no depende de servicios externos."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness confirma conexión DB dentro de timeout acotado."""
    try:
        async with asyncio.timeout(settings.DB_HEALTH_TIMEOUT_SECONDS):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("database_health_check_failed", error=type(exc).__name__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "database": "down"},
        )
    return {"status": "ok", "database": "up"}
