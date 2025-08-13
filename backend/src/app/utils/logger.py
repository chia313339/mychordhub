"""
Logging configuration for the application.
"""
import logging
import sys
from pathlib import Path

from app.core.config import settings


def setup_logging():
    """Setup application logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for application logs
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    
    # SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.WARNING)
    
    # FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # Application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(f"app.{name}")


# Setup logging when module is imported
setup_logging()