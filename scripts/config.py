"""Configuration settings for the baseball statistics tracking system."""

from pathlib import Path

# MinIO bucket names
BUCKET_CURRENT = "mlb-current"
BUCKET_HISTORICAL = "mlb-historical"
BUCKET_LIVE = "mlb-live"

# Analysis settings
SAMPLE_SIZE = 10  # Number of files to sample from each bucket
OUTPUT_DIR = str(Path(__file__).parent.parent / "docs" / "schema")

# Type hint for mypy
__all__ = [
    "BUCKET_CURRENT",
    "BUCKET_HISTORICAL",
    "BUCKET_LIVE",
    "SAMPLE_SIZE",
    "OUTPUT_DIR",
]
