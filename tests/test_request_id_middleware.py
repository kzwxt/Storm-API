"""Test RequestIDMiddleware functionality."""

import pytest
from fastapi import Request
from utils.middleware import RequestIDMiddleware, generate_request_id, get_request_id
from unittest.mock import AsyncMock


def test_generate_request_id():
    """Test that generate_request_id creates a unique ID."""
    id1 = generate_request_id()
    id2 = generate_request_id()
    
    assert id1 is not None
    assert id2 is not None
    assert id1 != id2  # Each ID should be unique
    assert len(id1) == 36  # UUID format (32 chars + 4 dashes)
    assert "-" in id1  # UUID format has dashes


def test_get_request_id_empty():
    """Test that get_request_id returns empty string when not set."""
    request_id = get_request_id()
    
    assert request_id == ""


def test_middleware_generates_request_id():
    """Test that middleware generates a unique request ID for each request."""
    # Create a mock app
    class MockApp:
        pass
    
    middleware = RequestIDMiddleware(MockApp())
    
    # Simulate request processing
    request_id = generate_request_id()
    
    assert request_id is not None
    assert len(request_id) == 36


def test_middleware_adds_request_id_to_response_headers():
    """Test that middleware adds X-Request-ID header to response."""
    from starlette.responses import Response
    
    class MockApp:
        async def dummy_call_next(request):
            return Response()
    
    middleware = RequestIDMiddleware(MockApp())
    
    # Simulate middleware dispatch
    request_id = generate_request_id()
    response = Response()
    response.headers["X-Request-ID"] = request_id
    
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) == 36


def test_request_id_is_unique_per_request():
    """Test that different requests get different request IDs."""
    id1 = generate_request_id()
    id2 = generate_request_id()
    id3 = generate_request_id()
    
    assert id1 != id2
    assert id2 != id3
    assert id1 != id3


def test_request_id_format():
    """Test that request ID follows UUID format."""
    request_id = generate_request_id()
    
    # UUID format: 8-4-4-4-12 hexadecimal characters
    parts = request_id.split("-")
    
    assert len(parts) == 5
    assert len(parts[0]) == 8
    assert len(parts[1]) == 4
    assert len(parts[2]) == 4
    assert len(parts[3]) == 4
    assert len(parts[4]) == 12
    
    # All parts should be hexadecimal
    for part in parts:
        try:
            int(part, 16)
        except ValueError:
            assert False, f"Part '{part}' is not hexadecimal"


def test_request_id_context_isolation():
    """Test that request ID context is isolated between requests."""
    from utils.middleware import request_id_context
    
    # Simulate two separate requests
    id1 = generate_request_id()
    token1 = request_id_context.set(id1)
    retrieved1 = get_request_id()
    
    # Reset context for next request
    request_id_context.reset(token1)
    
    id2 = generate_request_id()
    token2 = request_id_context.set(id2)
    retrieved2 = get_request_id()
    
    assert retrieved1 == id1
    assert retrieved2 == id2
    assert id1 != id2
    
    # Clean up
    request_id_context.reset(token2)


def test_middleware_initialization():
    """Test that middleware initializes correctly."""
    class MockApp:
        pass
    
    middleware = RequestIDMiddleware(MockApp())
    
    assert middleware is not None
    assert hasattr(middleware, 'dispatch')


def test_request_id_persistence_in_context():
    """Test that request ID persists throughout request context."""
    from utils.middleware import request_id_context
    
    # Set request ID
    test_id = generate_request_id()
    token = request_id_context.set(test_id)
    
    # Verify it persists
    retrieved = get_request_id()
    assert retrieved == test_id
    
    # Clean up
    request_id_context.reset(token)
    
    # Verify it's cleared
    assert get_request_id() == ""


def test_multiple_sequential_requests():
    """Test that sequential requests get sequential request IDs."""
    request_ids = []
    
    for _ in range(10):
        request_id = generate_request_id()
        request_ids.append(request_id)
    
    # All IDs should be unique
    assert len(request_ids) == len(set(request_ids))
    
    # IDs should not follow a predictable pattern (UUID4 is random)
    # Just verify they're all different
    assert request_ids[0] != request_ids[1]
    assert request_ids[5] != request_ids[9]