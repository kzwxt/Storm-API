"""
Request ID Middleware Module

This module provides middleware for generating and tracking unique request IDs
across all HTTP requests. This enables distributed tracing and debugging.

Components:
    - generate_request_id: Generate unique UUID-based request IDs
    - get_request_id: Retrieve current request ID from context
    - RequestIDMiddleware: FastAPI middleware for automatic request ID injection
"""

import uuid
from contextvars import ContextVar
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send


request_id_context: ContextVar[str] = ContextVar("request_id", default="")


def generate_request_id() -> str:
    """
    Generate a unique request ID using UUID4.

    Returns:
        str: UUID4-formatted request ID (36 characters with hyphens)

    Example:
        >>> request_id = generate_request_id()
        >>> print(request_id)
        >>> "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    """
    return str(uuid.uuid4())


def get_request_id() -> str:
    """
    Get the current request ID from context.

    Returns:
        str: Current request ID, or empty string if not set

    Example:
        >>> request_id = get_request_id()
        >>> if request_id:
        ...     print(f"Processing request: {request_id}")
    """
    return request_id_context.get("")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to each HTTP request.

    This middleware generates a unique ID for each incoming request, stores it
    in a context variable for access throughout the request lifecycle, and adds
    it to the response headers for client-side tracking.

    Attributes:
        app: The ASGI application to wrap

    Example:
        >>> app = FastAPI()
        >>> app.add_middleware(RequestIDMiddleware)
        >>> # Now all requests have X-Request-ID header
    """

    def __init__(self, app: ASGIApp) -> None:
        """
        Initialize the middleware.

        Args:
            app: The ASGI application to wrap
        """
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process request and add request ID to headers.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware/route handler in the chain

        Returns:
            Response: HTTP response with X-Request-ID header added

        Example:
            >>> # Automatically called by FastAPI for each request
            >>> response = await call_next(request)
            >>> response.headers["X-Request-ID"] = "uuid-here"
        """
        # Generate and set request ID in context
        request_id: str = generate_request_id()
        token: Any = request_id_context.set(request_id)
        request.state.request_id = request_id

        try:
            # Process the request
            response: Response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Clean up context (important for async/await)
            request_id_context.reset(token)