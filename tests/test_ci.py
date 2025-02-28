"""Basic test module to verify CI workflow."""

from typing import Any


def test_basic_addition() -> None:
    """Test basic addition to verify CI workflow."""
    assert 1 + 1 == 2


def test_dict_operations() -> None:
    """Test dictionary operations to verify type checking."""
    test_dict: dict[str, Any] = {"key": "value"}
    test_dict["new_key"] = 123
    assert test_dict == {"key": "value", "new_key": 123}


def test_string_operations() -> None:
    """Test string operations to verify linting."""
    test_string = "Hello, "
    test_string += "World!"
    assert test_string == "Hello, World!"
