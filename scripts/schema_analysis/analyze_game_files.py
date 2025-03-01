#!/usr/bin/env python3
"""
Analyze MLB game files stored in MinIO to document their JSON schema structure.
This script will:
1. Connect to MinIO and retrieve sample game files
2. Analyze the JSON structure of these files
3. Generate schema documentation
4. Identify common patterns and variations
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

from config import (
    BUCKET_CURRENT,
    BUCKET_HISTORICAL,
    BUCKET_LIVE,
    OUTPUT_DIR,
    SAMPLE_SIZE,
)
from minio.error import S3Error

from minio import Minio

MINIO_CONFIG: dict[str, str] = {
    "endpoint": str(os.getenv("MINIO_ENDPOINT", "localhost:9000")),
    "access_key": str(os.getenv("MINIO_ACCESS_KEY", "minioadmin")),
    "secret_key": str(os.getenv("MINIO_SECRET_KEY", "minioadmin")),
    "secure": str(os.getenv("MINIO_SECURE", "false")),
}


class SchemaAnalyzer:
    """Analyzes JSON schema of MLB game files."""

    def __init__(self) -> None:
        """Initialize the SchemaAnalyzer with MinIO client."""
        secure = MINIO_CONFIG["secure"].lower() == "true"
        self.client = Minio(
            endpoint=MINIO_CONFIG["endpoint"],
            access_key=MINIO_CONFIG["access_key"],
            secret_key=MINIO_CONFIG["secret_key"],
            secure=secure,
        )
        self.ensure_output_dir()

    def ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        # Create main schema directory
        schema_dir = Path(OUTPUT_DIR)
        schema_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created/verified schema directory: {schema_dir.absolute()}")

        # Create samples directory
        samples_dir = schema_dir / "samples"
        samples_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created/verified samples directory: {samples_dir.absolute()}")

    def get_sample_files(self, bucket_name: str) -> List[str]:
        """
        Get a sample of JSON files from the specified bucket.

        Args:
            bucket_name: Name of the MinIO bucket

        Returns:
            List[str]: List of object names
        """
        try:
            # Get all objects recursively
            print(f"Listing objects in {bucket_name}...")
            objects = list(self.client.list_objects(bucket_name, recursive=True))
            print(f"Found {len(objects)} total objects in {bucket_name}")

            # Filter for .json files only
            json_files = [
                obj.object_name
                for obj in objects
                if obj.object_name.endswith(".json") and not obj.is_dir
            ]
            print(f"Found {len(json_files)} JSON files in {bucket_name}")

            selected_files = json_files[:SAMPLE_SIZE]
            print(
                f"Selected {len(selected_files)} files for analysis: {selected_files}"
            )
            return selected_files
        except S3Error as e:
            print(f"Error accessing bucket {bucket_name}: {e}")
            return []

    def read_json_file(self, bucket_name: str, object_name: str) -> Dict[str, Any]:
        """
        Read a JSON file from MinIO.

        Args:
            bucket_name: Name of the MinIO bucket
            object_name: Name of the object to read

        Returns:
            Dict[str, Any]: Parsed JSON data or empty dict if error occurs
        """
        response = None
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = json.loads(response.read())
            return data if isinstance(data, dict) else {}
        except S3Error as e:
            print(f"Error reading {object_name} from {bucket_name}: {e}")
            return {}
        finally:
            if response:
                response.close()
                response.release_conn()

    def analyze_json_structure(
        self, data: Dict[str, Any], prefix: str = ""
    ) -> Dict[str, Set[str]]:
        """
        Recursively analyze JSON structure to identify field types.

        Args:
            data: JSON data to analyze
            prefix: Current path prefix for nested fields

        Returns:
            Dict[str, Set[str]]: Mapping of field paths to their observed types
        """
        schema: Dict[str, Set[str]] = {}

        for key, value in data.items():
            # Special handling for player IDs in various locations
            if (
                prefix == "gameData.players"
                or prefix.endswith(".boxscore.teams.away.players")
                or prefix.endswith(".boxscore.teams.home.players")
            ) and key.startswith("ID"):
                # Use a generic "player" prefix instead of specific IDs
                full_path = f"{prefix}.player"
                if full_path not in schema:
                    schema[full_path] = {"object"}
                    if isinstance(value, dict):
                        nested_schema = self.analyze_json_structure(value, full_path)
                        schema.update(nested_schema)
                continue

            full_path = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                schema[full_path] = {"object"}
                nested_schema = self.analyze_json_structure(value, full_path)
                schema.update(nested_schema)
            elif isinstance(value, list):
                schema[full_path] = {"array"}
                if value:  # Analyze first item if list is not empty
                    if isinstance(value[0], dict):
                        nested_schema = self.analyze_json_structure(
                            value[0], f"{full_path}[]"
                        )
                        schema.update(nested_schema)
                    else:
                        schema[f"{full_path}[]"] = {type(value[0]).__name__}
            else:
                schema[full_path] = {type(value).__name__}

        return schema

    def merge_schemas(self, schemas: List[Dict[str, Set[str]]]) -> Dict[str, Set[str]]:
        """
        Merge multiple schema definitions.

        Args:
            schemas: List of schema definitions to merge

        Returns:
            Dict[str, Set[str]]: Merged schema with all observed types
        """
        merged: Dict[str, Set[str]] = {}

        for schema in schemas:
            for field, types in schema.items():
                if field in merged:
                    merged[field].update(types)
                else:
                    merged[field] = types

        return merged

    def generate_schema_documentation(
        self, schema: Dict[str, Set[str]], bucket_name: str
    ) -> None:
        """
        Generate markdown documentation for the schema.

        Args:
            schema: Schema definition to document
            bucket_name: Name of the bucket being documented
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_file = os.path.join(OUTPUT_DIR, f"{bucket_name}_schema.md")

        with open(output_file, "w") as f:
            f.write(f"# {bucket_name} Schema Documentation\n\n")
            f.write(f"Generated on: {timestamp}\n\n")
            f.write("## Field Definitions\n\n")
            f.write("| Field Path | Types |\n")
            f.write("|------------|--------|\n")

            for field, types in sorted(schema.items()):
                types_str = ", ".join(sorted(types))
                f.write(f"| {field} | {types_str} |\n")

    def save_sample_json(
        self, data: Dict[str, Any], bucket_name: str, file_name: str
    ) -> None:
        """
        Save a sample JSON file to the docs directory.

        Args:
            data: JSON data to save
            bucket_name: Name of the bucket the data came from
            file_name: Original file name from MinIO
        """
        try:
            # Create a more descriptive filename using original path
            base_name = os.path.basename(file_name)
            samples_dir = os.path.join(OUTPUT_DIR, "samples")

            # Ensure samples directory exists
            Path(samples_dir).mkdir(parents=True, exist_ok=True)

            sample_file = os.path.join(samples_dir, f"{bucket_name}_{base_name}")
            print(f"Attempting to save sample file to: {sample_file}")

            # Write the file
            with open(sample_file, "w") as f:
                json.dump(data, f, indent=2)

            # Verify file was created
            if os.path.exists(sample_file):
                print(f"Successfully saved sample JSON file: {sample_file}")
                print(f"File size: {os.path.getsize(sample_file)} bytes")
            else:
                print(f"Warning: File was not created at {sample_file}")

        except Exception as e:
            print(f"Error saving sample file: {e}")
            import traceback

            traceback.print_exc()

    def analyze_bucket(self, bucket_name: str) -> None:
        """
        Analyze all sample files in a bucket.

        Args:
            bucket_name: Name of the bucket to analyze
        """
        print(f"\nAnalyzing {bucket_name}...")

        sample_files = self.get_sample_files(bucket_name)
        if not sample_files:
            print(f"No JSON files found in {bucket_name}")
            return

        print(f"Found {len(sample_files)} JSON files to analyze")
        schemas = []
        sample_saved = False

        for file_name in sample_files:
            print(f"\nProcessing {file_name}")
            data = self.read_json_file(bucket_name, file_name)
            if data:
                print(f"Successfully read JSON data from {file_name}")
                schema = self.analyze_json_structure(data)
                schemas.append(schema)
                # Save the first valid JSON file as a sample
                if not sample_saved:
                    print(f"Attempting to save sample from {file_name}")
                    self.save_sample_json(data, bucket_name, file_name)
                    sample_saved = True
            else:
                print(f"No valid JSON data found in {file_name}")

        if schemas:
            merged_schema = self.merge_schemas(schemas)
            self.generate_schema_documentation(merged_schema, bucket_name)
            print(f"Schema documentation generated for {bucket_name}")
        else:
            print(f"No valid schemas generated for {bucket_name}")

    def analyze_all_buckets(self) -> None:
        """Analyze all MLB data buckets."""
        for bucket in [BUCKET_CURRENT, BUCKET_HISTORICAL, BUCKET_LIVE]:
            self.analyze_bucket(bucket)


def main() -> None:
    """Main entry point for schema analysis."""
    try:
        analyzer = SchemaAnalyzer()
        analyzer.analyze_all_buckets()
        print("\nSchema analysis complete. Documentation generated in", OUTPUT_DIR)
    except Exception as e:
        print(f"Error during schema analysis: {e}")


if __name__ == "__main__":
    main()
