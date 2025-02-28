"""Test module to verify GitHub Actions workflow."""

from typing import List


def test_style_issues() -> None:
    """Test with deliberate style issues to verify GitHub Actions checks."""
    test_string = "This is a test string that uses double quotes"
    test_list = ["This now uses double quotes consistently"]

    assert len(test_string) > 0
    assert len(test_list) > 0


def test_type_issues() -> int:
    """Test with proper type annotations."""
    values: List[int] = [1, 2, 3]
    result = sum(values)
    return result
