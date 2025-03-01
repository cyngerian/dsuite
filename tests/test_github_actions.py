"""Test module for verifying GitHub Actions CI setup."""

from typing import Dict

import pytest


def test_ci_setup() -> None:
    """Basic test to verify CI is working."""
    assert True


@pytest.mark.asyncio
async def test_async_setup() -> None:
    """Test to verify async test configuration."""
    result = await async_operation()
    assert result == {"status": "success"}


async def async_operation() -> Dict[str, str]:
    """Simulate an async operation."""
    return {"status": "success"}
