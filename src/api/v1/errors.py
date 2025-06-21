from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import datetime
import traceback

ERROR_MESSAGES = {
    status.HTTP_400_BAD_REQUEST: "Bad Request",
    status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    status.HTTP_403_FORBIDDEN: "Forbidden",
    status.HTTP_404_NOT_FOUND: "Not Found",
    status.HTTP_406_NOT_ACCEPTABLE: "Not Acceptable",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
}


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": exc.status_code,
            "error": ERROR_MESSAGES.get(exc.status_code, "HTTP Exception"),
            "message": exc.detail,
            "path": request.url.path,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": status.HTTP_400_BAD_REQUEST,
            "error": "Bad Request",
            "message": "Validation error",
            "details": exc.errors(),
            "path": request.url.path,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "path": request.url.path,
            "trace": traceback.format_exc().splitlines(),
        },
    )


def add_exception_handlers(app):
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
