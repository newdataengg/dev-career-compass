"""
Logging utilities for DevCareerCompass
"""
import logging
import sys
from typing import Optional
import structlog
from structlog import configure, get_logger
from structlog.stdlib import LoggerFactory

from src.config.settings import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Setup structured logging for the application"""
    level = log_level or settings.log_level
    
    # Configure structlog
    configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )


def get_application_logger(name: str = "devcareer_compass") -> logging.Logger:
    """Get a structured logger for the application"""
    return get_logger(name)


# Initialize logging when module is imported
setup_logging() 