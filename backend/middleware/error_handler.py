"""Global error handling for consistent API error responses."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle pydantic validation errors with a clean response."""
        errors = exc.errors()
        first_error = errors[0] if errors else {"msg": "Validation error"}
        field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        message = first_error.get("msg", "Invalid input")

        detail = f"{field}: {message}" if field else message

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": detail,
                "status": 422,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request,
        exc: ValueError,
    ) -> JSONResponse:
        """Handle ValueError as 400 Bad Request."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Bad Request",
                "detail": str(exc),
                "status": 400,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch-all handler — never leak stack traces."""
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later.",
                "status": 500,
            },
        )
