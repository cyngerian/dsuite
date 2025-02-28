#!/usr/bin/env python3
"""
Compare JSON schema fields with core schema definitions.
Generates a report showing which fields are covered and which are missing.
"""
import json
import os
import re
import sys
from collections import defaultdict
from typing import Any, Dict, List, Tuple, cast

# Add project root to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from services.transformation.src.schema.core import (  # noqa: E402
    game_play_schema,
    play_detail_schema,
    reference_schema,
    team_player_schema,
)


def extract_json_from_markdown(md_file: str) -> Dict[str, Any]:
    """Extract JSON content from a markdown file.

    Args:
        md_file: Path to the markdown file containing JSON content.

    Returns:
        Extracted JSON content as a dictionary.

    Raises:
        ValueError: If no JSON content is found in the markdown file.
    """
    with open(md_file) as f:
        content = f.read()
        # Look for JSON content between ```json blocks
        json_blocks = re.findall(r"```json\n(.*?)\n```", content, re.DOTALL)
        if not json_blocks:
            raise ValueError("No JSON content found in markdown file")
        return cast(Dict[str, Any], json.loads(json_blocks[0]))


def read_json_schema_fields(schema_file: str) -> Dict[str, List[str]]:
    """Read JSON schema file and extract field names.

    Args:
        schema_file: Path to the schema file.

    Returns:
        Dictionary mapping schema names to lists of field names.
    """
    fields: Dict[str, List[str]] = {}
    schema = extract_json_from_markdown(schema_file)
    for key, value in schema.items():
        if isinstance(value, dict) and "properties" in value:
            fields[key] = list(value["properties"].keys())
    return fields


def get_schema_fields() -> Dict[str, Dict[str, str]]:
    """Get all fields defined in the core schema files with their locations.

    Returns:
        Dictionary mapping normalized field names to their schema information.
    """
    schema_fields: Dict[str, Dict[str, str]] = {}

    # Combine all schema definitions
    all_schemas = {
        "reference": reference_schema,
        "team_player": team_player_schema,
        "game_play": game_play_schema,
        "play_detail": play_detail_schema,
    }

    # Extract fields from each table definition with their locations
    for schema_name, schema in all_schemas.items():
        for table_name, table_def in schema.items():
            if isinstance(table_def, dict) and "columns" in table_def:
                columns = cast(Dict[str, Any], table_def["columns"])
                for column_name in columns:
                    normalized_name = normalize_field_name(column_name)
                    schema_fields[normalized_name] = {
                        "original_name": column_name,
                        "table": table_name,
                        "schema": schema_name,
                    }

    return schema_fields


def normalize_field_name(field: str) -> str:
    """Normalize field names for comparison.

    Args:
        field: Field name to normalize.

    Returns:
        Normalized field name.
    """
    # Convert camelCase to snake_case
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", field)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    # Remove common prefixes/suffixes
    name = re.sub(r"^(game_data_|live_data_)", "", name)
    name = re.sub(r"_data$", "", name)

    return name


def analyze_coverage(
    json_fields: Dict[str, List[str]], schema_fields: Dict[str, Dict[str, str]]
) -> Dict[str, Dict[str, Any]]:
    """Analyze which fields are covered and which are missing.

    Args:
        json_fields: Dictionary mapping schema names to lists of field names.
        schema_fields: Dictionary mapping normalized field names to schema info.

    Returns:
        Dictionary containing coverage analysis results.
    """
    coverage_by_category: Dict[str, Dict[str, Any]] = {}

    for category, fields in json_fields.items():
        category_fields: List[Tuple[str, str, bool, str]] = []
        for field_name in fields:
            normalized_name = normalize_field_name(field_name)
            schema_match = schema_fields.get(normalized_name)
            is_covered = schema_match is not None

            # Create match info string if covered
            match_info = ""
            if is_covered and schema_match:
                match_info = (
                    f"{schema_match['schema']}.{schema_match['table']}."
                    f"{schema_match['original_name']}"
                )

            category_fields.append(
                (field_name, normalized_name, is_covered, match_info)
            )

        # Calculate category statistics
        total = len(category_fields)
        covered = sum(1 for f in category_fields if f[2])
        coverage = (covered / total * 100) if total > 0 else 0

        coverage_by_category[category] = {
            "fields": category_fields,
            "total": total,
            "covered": covered,
            "coverage": coverage,
        }

    return coverage_by_category


def generate_report(coverage_by_category: Dict[str, Dict[str, Any]]) -> str:
    """Generate a markdown report of the analysis.

    Args:
        coverage_by_category: Dictionary containing coverage analysis results.

    Returns:
        Generated markdown report as a string.
    """
    # Calculate overall statistics
    total_fields = sum(cat["total"] for cat in coverage_by_category.values())
    total_covered = sum(cat["covered"] for cat in coverage_by_category.values())
    overall_coverage = (total_covered / total_fields * 100) if total_fields > 0 else 0

    # Decorative separators
    major_separator = "=" * 80
    category_separator = "-" * 80

    report = [
        "# Schema Coverage Analysis",
        "",
        major_separator,
        "",
        "## Overall Summary",
        f"- Total Fields: {total_fields}",
        f"- Covered Fields: {total_covered}",
        f"- Missing Fields: {total_fields - total_covered}",
        f"- Overall Coverage: {overall_coverage:.2f}%",
        "",
        major_separator,
        "",
        "## Coverage by Category",
    ]

    # Add category summaries
    categories = sorted(coverage_by_category.keys())
    for i, category in enumerate(categories):
        cat_data = coverage_by_category[category]
        report.extend(
            [
                "",
                (category_separator if i > 0 else ""),
                "",
                f"### {category}",
                f"- Fields: {cat_data['total']}",
                f"- Covered: {cat_data['covered']}",
                f"- Coverage: {cat_data['coverage']:.2f}%",
                "",
            ]
        )

        # Group fields by base name
        field_groups = defaultdict(list)
        for field_name, full_path, is_covered, match_info in sorted(
            cast(List[Tuple[str, str, bool, str]], cat_data["fields"])
        ):
            field_groups[field_name].append((full_path, is_covered, match_info))

        # Output each field group
        for field_name, paths in sorted(field_groups.items()):
            # Determine if any path is covered
            any_covered = any(is_covered for _, is_covered, _ in paths)
            status = "✅ Covered" if any_covered else "❌ Missing"

            report.append(f"#### {field_name} {status}")
            report.append("")

            # Output each path
            for path, is_covered, match_info in paths:
                status_icon = "✅" if is_covered else "❌"
                report.append(f"- {status_icon} `{path}`")
                if match_info:
                    report.append(f"  - Maps to: `{match_info}`")
            report.append("")

    # Add final separator
    report.extend([category_separator, "", "End of Report", major_separator])

    return "\n".join(report)


def compare_schemas(schema1: Dict, schema2: Dict) -> List[str]:
    """Compare two schemas and return a list of differences."""
    differences = []
    for key in set(schema1.keys()) | set(schema2.keys()):
        if key not in schema1:
            differences.append(f"Key '{key}' only in schema2")
        elif key not in schema2:
            differences.append(f"Key '{key}' only in schema1")
        elif schema1[key] != schema2[key]:
            differences.append(
                f"Value for '{key}' differs: {schema1[key]} vs {schema2[key]}"
            )
    return differences


def main() -> None:
    """Main entry point for schema comparison."""
    try:
        # Read JSON schema fields
        json_schema_file = "docs/schema/mlb-historical_schema.md"
        json_fields = read_json_schema_fields(json_schema_file)

        # Get schema fields
        schema_fields = get_schema_fields()

        # Analyze coverage
        coverage_by_category = analyze_coverage(json_fields, schema_fields)

        # Generate and save report
        report = generate_report(coverage_by_category)
        output_file = "docs/schema/schema_coverage.md"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as f:
            f.write(report)

        print(f"Report generated: {output_file}")

    except Exception as e:
        print(f"Error analyzing schemas: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
