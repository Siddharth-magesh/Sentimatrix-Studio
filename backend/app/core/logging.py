"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.core.config import get_settings


def add_service_context(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add service context to all log events."""
    settings = get_settings()
    event_dict["service"] = "sentimatrix-studio"
    event_dict["environment"] = settings.app_env
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Determine processors based on log format
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        add_service_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        # JSON format for production
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        # Console format for development
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    log_level = getattr(logging, settings.log_level)

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger(name)


def bind_request_context(request_id: str, **kwargs: Any) -> None:
    """Bind request context to all subsequent log messages."""
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, **kwargs)


def clear_request_context() -> None:
    """Clear the request context."""
    structlog.contextvars.clear_contextvars()


class RequestLogger:
    """Logger for HTTP request/response logging."""

    def __init__(self) -> None:
        self.logger = get_logger("http.request")

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        request_id: str | None = None,
        user_id: str | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Log an HTTP request with timing and context."""
        log_data: dict[str, Any] = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }

        if request_id:
            log_data["request_id"] = request_id
        if user_id:
            log_data["user_id"] = user_id
        if client_ip:
            log_data["client_ip"] = client_ip
        if user_agent:
            log_data["user_agent"] = user_agent[:100]

        # Log level based on status code
        if status_code >= 500:
            self.logger.error("Request completed", **log_data)
        elif status_code >= 400:
            self.logger.warning("Request completed", **log_data)
        else:
            self.logger.info("Request completed", **log_data)


class AuditLogger:
    """Logger for security audit events."""

    def __init__(self) -> None:
        self.logger = get_logger("audit")

    def log_auth_event(
        self,
        event_type: str,
        success: bool,
        user_id: str | None = None,
        email: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log an authentication event."""
        log_data: dict[str, Any] = {
            "event_type": event_type,
            "success": success,
            "category": "auth",
        }

        if user_id:
            log_data["user_id"] = user_id
        if email:
            log_data["email"] = email
        if ip_address:
            log_data["ip_address"] = ip_address
        if user_agent:
            log_data["user_agent"] = user_agent[:100]
        if details:
            log_data["details"] = details

        if success:
            self.logger.info("Auth event", **log_data)
        else:
            self.logger.warning("Auth event failed", **log_data)

    def log_data_access(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        ip_address: str | None = None,
    ) -> None:
        """Log a data access event."""
        self.logger.info(
            "Data access",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            ip_address=ip_address,
            category="data",
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log a security event."""
        log_data: dict[str, Any] = {
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "category": "security",
        }

        if user_id:
            log_data["user_id"] = user_id
        if ip_address:
            log_data["ip_address"] = ip_address
        if details:
            log_data["details"] = details

        if severity == "critical":
            self.logger.critical("Security event", **log_data)
        elif severity == "high":
            self.logger.error("Security event", **log_data)
        elif severity == "medium":
            self.logger.warning("Security event", **log_data)
        else:
            self.logger.info("Security event", **log_data)


# Global logger instances
request_logger = RequestLogger()
audit_logger = AuditLogger()
