"""
Configuration settings for MinIO connection and schema analysis.
"""

import os
from pathlib import Path
from typing import Dict, Union

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get project root directory (two levels up from this file)
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)

# MinIO configuration
MINIO_CONFIG: Dict[str, Union[str, bool]] = {
    "endpoint": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    "secure": False,  # Set to True if using HTTPS
}

# Bucket names
BUCKET_CURRENT = "mlb-current"
BUCKET_HISTORICAL = "mlb-historical"
BUCKET_LIVE = "mlb-live"

# Analysis settings
SAMPLE_SIZE = 5  # Number of files to analyze from each bucket
OUTPUT_DIR = os.path.join(
    PROJECT_ROOT, "docs", "schema"
)  # Directory to store schema documentation
