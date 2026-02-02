"""Request ID middleware for request tracing."""

import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import bind_request_context, clear_request_context

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that adds a unique request ID to each request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request with a unique request ID."""
        # Get request ID from header or generate new one
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Store request ID in request state
        request.state.request_id = request_id

        # Bind request context for logging
        bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_request_context()
