import logging
import logging.config
import os
import sys
from typing import Dict, Any

def setup_logging(service_name: str = "products-api", log_level: str = "INFO") -> None:
    """Configure le logging structuré pour l'application."""
    
    log_level = os.getenv("LOG_LEVEL", log_level).upper()
    
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s [%(request_id)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(request_id)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": f"/app/logs/{service_name}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "api": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "api.errors": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    # Créer le répertoire de logs s'il n'existe pas
    os.makedirs("/app/logs", exist_ok=True)
    
    # Appliquer la configuration
    logging.config.dictConfig(logging_config)
    
    # Logger de test
    logger = logging.getLogger("api")
    logger.info(f"🚀 Logging configured for {service_name} at level {log_level}")

class RequestContextFilter(logging.Filter):
    """Filtre pour ajouter le contexte de requête aux logs."""
    
    def filter(self, record):
        # Ajouter des valeurs par défaut si pas de contexte
        if not hasattr(record, 'request_id'):
            record.request_id = 'no-request'
        return True 