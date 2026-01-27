"""Tests for global search API validation."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestSearchValidation:
    """Tests for /api/v1/search parameter validation."""

    async def test_search_query_too_long(self, client: AsyncClient) -> None:
        """Search query exceeding max_length (100) returns 422."""
        long_query = "a" * 101
        response = await client.get(f"/api/v1/search?q={long_query}")
        assert response.status_code == 422
        expected_err = "String should have at most 100 characters"
        assert expected_err in response.text or "less than or equal to 100" in response.text

    async def test_search_query_max_length_ok(self, client: AsyncClient) -> None:
        """Search query at max_length (100) is allowed."""
        max_query = "a" * 100
        response = await client.get(f"/api/v1/search?q={max_query}")
        assert response.status_code == 200
