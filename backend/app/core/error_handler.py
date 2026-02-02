"""Error response formatting and exception handlers."""

from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import StudioException

logger = structlog.get_logger(__name__)


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """Create a standardized error response."""
    content: dict[str, Any] = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }

    if details:
        content["error"]["details"] = details

    if request_id:
        content["error"]["request_id"] = request_id

    return JSONResponse(status_code=status_code, content=content)


def get_request_id(request: Request) -> str | None:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", None)


async def studio_exception_handler(request: Request, exc: StudioException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.warning(
        "Application error",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )

    return create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details if exc.details else None,
        request_id=get_request_id(request),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI request validation errors."""
    errors = []
    for error in exc.errors():
        loc = ".".join(str(x) for x in error["loc"])
        errors.append({"field": loc, "message": error["msg"], "type": error["type"]})

    logger.warning("Validation error", errors=errors)

    return create_error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": errors},
        request_id=get_request_id(request),
    )


async def pydantic_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        loc = ".".join(str(x) for x in error["loc"])
        errors.append({"field": loc, "message": error["msg"], "type": error["type"]})

    logger.warning("Pydantic validation error", errors=errors)

    return create_error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Data validation failed",
        details={"errors": errors},
        request_id=get_request_id(request),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions."""
    logger.exception("Unhandled exception", exc_info=exc)

    return create_error_response(
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        request_id=get_request_id(request),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the application."""
    app.add_exception_handler(StudioException, studio_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
