"""
P0-5/P0-6: Unified API Error Handler + Request ID Middleware

Features:
- Global exception handlers for all CheckToolBaseError subtypes
- Unified JSON error response: {error_code, message, request_id, details}
- Request ID: auto-generated (UUID4) or propagated from X-Request-ID header
- Request ID injected into all log entries during request lifecycle
- Never exposes raw Python traceback to API consumers
"""

import traceback
import uuid
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.crosscutting.errors.exceptions import (
    CheckToolBaseError, PersistenceError, PersistenceCorruptionError,
    PersistenceRecoveryError, DomainError, ConfigurationError,
    ValidationError, ErrorCode, ConcurrencyError
)
from src.crosscutting.logging.logger import get_logger
from src.crosscutting.observation.recorder import record_event

logger = get_logger(__name__)


def _generate_request_id() -> str:
    return str(uuid.uuid4())


class ErrorResponseBuilder:
    """Builds unified error response DTOs."""

    @staticmethod
    def build(
        error_code: str,
        message: str,
        request_id: str,
        status_code: int = 500,
        details: Optional[dict] = None
    ) -> JSONResponse:
        body = {
            "error_code": error_code,
            "message": message,
            "request_id": request_id,
            "details": details or {}
        }
        return JSONResponse(status_code=status_code, content=body)


def register_error_handlers(app: FastAPI):
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(CheckToolBaseError)
    async def checktool_error_handler(request: Request, exc: CheckToolBaseError):
        request_id = getattr(request.state, "request_id", _generate_request_id())
        actor = request.headers.get("X-Actor")
        
        # Inject request_id into the exception if not already set
        if not exc.request_id:
            exc.request_id = request_id

        # Determine HTTP status code from error type
        status_code = 500
        if isinstance(exc, (ValidationError, DomainError)):
            status_code = 422
        elif isinstance(exc, ConcurrencyError):
            status_code = 409
            record_event(
                event_type="occ_conflict",
                baseline_id=_try_extract_baseline_id(request.url.path),
                request_id=request_id,
                actor=actor,
                context={"path": request.url.path, "method": request.method},
            )
        elif isinstance(exc, PersistenceCorruptionError):
            status_code = 503  # Service unavailable - data corrupted
        elif isinstance(exc, PersistenceRecoveryError):
            status_code = 503
        elif isinstance(exc, PersistenceError):
            status_code = 500
        elif isinstance(exc, ConfigurationError):
            status_code = 500

        logger.error(
            f"[{exc.error_code}] {exc.message} | request_id={request_id} | "
            f"path={request.url.path} | details={exc.details}"
        )

        return ErrorResponseBuilder.build(
            error_code=exc.error_code,
            message=exc.message,
            request_id=request_id,
            status_code=status_code,
            details=exc.details
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", _generate_request_id())
        
        # Log full traceback for debugging (never sent to client)
        logger.error(
            f"[{ErrorCode.UNEXPECTED}] Unhandled exception | request_id={request_id} | "
            f"path={request.url.path} | error={str(exc)}\n"
            f"{traceback.format_exc()}"
        )

        return ErrorResponseBuilder.build(
            error_code=ErrorCode.UNEXPECTED,
            message="An unexpected error occurred. Please try again or contact support.",
            request_id=request_id,
            status_code=500,
            details={"hint": "Check server logs with request_id for details"}
        )


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    P0-6: Request ID Middleware
    
    - Generates a UUID4 request_id for each incoming request
    - Accepts X-Request-ID header from callers for trace propagation
    - Stores request_id in request.state for downstream use
    - Adds X-Request-ID to response headers
    - Injects request_id into log context
    """

    async def dispatch(self, request: Request, call_next):
        # Use caller-provided ID or generate new one
        request_id = request.headers.get("X-Request-ID") or _generate_request_id()
        request.state.request_id = request_id

        logger.info(f">> {request.method} {request.url.path} | request_id={request_id}")

        try:
            response = await call_next(request)
        except Exception as exc:
            # If the exception is not caught by FastAPI handlers, we still log it
            logger.error(
                f"!! Uncaught exception in middleware | request_id={request_id} | "
                f"path={request.url.path} | error={str(exc)}"
            )
            raise

        response.headers["X-Request-ID"] = request_id
        
        logger.info(
            f"<< {request.method} {request.url.path} {response.status_code} | request_id={request_id}"
        )

        return response


def _try_extract_baseline_id(path: str) -> Optional[str]:
    try:
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 4 and parts[0] == "api" and parts[1] == "rules":
            if parts[2] == "publish":
                return parts[3]
            if parts[2] == "draft":
                return parts[3]
        if len(parts) >= 3 and parts[0] == "api" and parts[1] == "baselines":
            return parts[2]
        return None
    except Exception:
        return None
