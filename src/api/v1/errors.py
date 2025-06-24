from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging
from datetime import datetime
from typing import Union

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API Exception"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation Error"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(APIError):
    """Resource Not Found Error"""

    def __init__(self, resource: str, identifier: Union[str, int]):
        super().__init__(
            message=f"{resource} with identifier {identifier} not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)},
        )


class DuplicateError(APIError):
    """Duplicate Resource Error"""

    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            status_code=409,
            error_code="DUPLICATE_RESOURCE",
            details={"resource": resource, "field": field, "value": value},
        )


class AuthenticationError(APIError):
    """Authentication Error"""

    def __init__(self, message: str = "Invalid or missing API Token"):
        super().__init__(
            message=message, status_code=401, error_code="AUTHENTICATION_ERROR"
        )


class BusinessLogicError(APIError):
    """Business Logic Error"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details,
        )


class DatabaseTimeoutError(APIError):
    """Database Timeout Error"""

    def __init__(self, message: str = "Database operation timed out"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="DATABASE_TIMEOUT",
            details={"retry_after": "30"}
        )


class ServiceUnavailableError(APIError):
    """Service Unavailable Error - System under heavy load"""

    def __init__(self, message: str = "Service temporarily unavailable due to high load"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details={"retry_after": "60"}
        )


class RateLimitError(APIError):
    """Rate Limit Exceeded Error"""

    def __init__(self, message: str = "Too many requests", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": str(retry_after)}
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: dict = None,
    path: str = None,
) -> JSONResponse:
    """Create standardized error response"""

    error_response = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": status_code,
        "error": get_status_text(status_code),
        "message": message,
        "path": path,
    }

    if error_code:
        error_response["error_code"] = error_code

    if details:
        error_response["details"] = details

    return JSONResponse(status_code=status_code, content=error_response)


def get_status_text(status_code: int) -> str:
    """Get HTTP status text"""
    status_texts = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }
    return status_texts.get(status_code, "Unknown Error")


def add_exception_handlers(app):
    """Add comprehensive exception handlers to the FastAPI app"""

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle custom API errors"""
        logger.error(f"API Error: {exc.message} - Details: {exc.details}")

        return create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            path=str(request.url.path),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions"""
        logger.error(f"Value Error: {str(exc)}")

        return create_error_response(
            status_code=400,
            message=str(exc),
            error_code="VALUE_ERROR",
            path=str(request.url.path),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        logger.error(f"Validation Error: {exc.errors()}")

        # Format validation errors nicely
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append(
                {"field": field, "message": error["msg"], "type": error["type"]}
            )

        return create_error_response(
            status_code=422,
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details={"validation_errors": errors},
            path=str(request.url.path),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")

        return create_error_response(
            status_code=exc.status_code,
            message=exc.detail,
            error_code="HTTP_ERROR",
            path=str(request.url.path),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")

        # In production, don't expose internal error details
        return create_error_response(
            status_code=500,
            message="An internal server error occurred",
            error_code="INTERNAL_ERROR",
            path=str(request.url.path),
        )
