import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Configure logging for the FastAPI application"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Get log level from environment variable, default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Current date for log file names
    current_date = datetime.now().strftime("%Y-%m-%d")

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file_detailed": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": f"logs/api_{current_date}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "file_errors": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": f"logs/errors_{current_date}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8",
            },
            "file_business": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": f"logs/business_{current_date}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            # Root logger
            "": {
                "level": "DEBUG",
                "handlers": ["console", "file_detailed", "file_errors"],
            },
            # FastAPI and Uvicorn
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file_detailed"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file_detailed"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console", "file_detailed"],
                "propagate": False,
            },
            # Application specific loggers
            "api": {
                "level": "DEBUG",
                "handlers": ["console", "file_detailed", "file_errors"],
                "propagate": False,
            },
            "api.endpoints": {
                "level": "DEBUG",
                "handlers": ["console", "file_detailed", "file_business"],
                "propagate": False,
            },
            "api.services": {
                "level": "DEBUG",
                "handlers": ["console", "file_detailed", "file_business"],
                "propagate": False,
            },
            "api.repositories": {
                "level": "DEBUG",
                "handlers": ["console", "file_detailed"],
                "propagate": False,
            },
            "api.auth": {
                "level": "INFO",
                "handlers": ["console", "file_detailed", "file_errors"],
                "propagate": False,
            },
            "api.errors": {
                "level": "WARNING",
                "handlers": ["console", "file_detailed", "file_errors"],
                "propagate": False,
            },
            # Database
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["file_detailed"],
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "level": "WARNING",
                "handlers": ["file_detailed"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    # Log startup message
    logger = logging.getLogger("api")
    logger.info("=" * 50)
    logger.info("FastAPI Application Starting")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Logs directory: {logs_dir.absolute()}")
    logger.info("=" * 50)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


# Business operation logging helpers
def log_business_operation(
    logger: logging.Logger,
    operation: str,
    entity: str,
    entity_id: str = None,
    user: str = None,
    **kwargs,
):
    """Log business operations with structured data"""
    log_data = {
        "operation": operation,
        "entity": entity,
        "entity_id": entity_id,
        "user": user,
        **kwargs,
    }

    message = f"Business Operation: {operation} on {entity}"
    if entity_id:
        message += f" (ID: {entity_id})"
    if user:
        message += f" by user {user}"

    # Add extra data as structured info
    extra_info = ", ".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    if extra_info:
        message += f" - {extra_info}"

    logger.info(message, extra=log_data)


def log_api_call(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    status_code: int,
    response_time: float = None,
    user: str = None,
):
    """Log API calls with performance metrics"""
    message = f"API Call: {method} {endpoint} -> {status_code}"
    if response_time:
        message += f" ({response_time:.3f}s)"
    if user:
        message += f" [User: {user}]"

    log_data = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time": response_time,
        "user": user,
    }

    if status_code >= 400:
        logger.warning(message, extra=log_data)
    else:
        logger.info(message, extra=log_data)


def log_error_with_context(
    logger: logging.Logger, error: Exception, context: dict = None
):
    """Log errors with additional context"""
    context = context or {}

    message = f"Error occurred: {type(error).__name__}: {str(error)}"

    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **context,
    }

    logger.error(message, extra=log_data, exc_info=True)
