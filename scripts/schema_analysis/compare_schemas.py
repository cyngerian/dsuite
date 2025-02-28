#!/usr/bin/env python3
"""
Compare JSON schema fields with core schema definitions.
Generates a report showing which fields are covered and which are missing.
"""
import os
from pathlib import Path
from typing import Dict, Set, List, Tuple, DefaultDict, Any
from collections import defaultdict
import re
import sys

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from services.transformation.src.schema.core.reference import reference_schema
from services.transformation.src.schema.core.team_player import team_player_schema
from services.transformation.src.schema.core.game_play import game_play_schema
from services.transformation.src.schema.core.play_detail import play_detail_schema

def read_json_schema_fields(schema_file: str) -> Dict[str, List[str]]:
    """Read field paths from the JSON schema markdown file and group by category."""
    field_groups = defaultdict(list)
    
    with open(schema_file, 'r') as f:
        for line in f:
            if '|' in line:  # It's a table row
                parts = line.split('|')
                if len(parts) >= 3 and parts[1].strip() != 'Field Path':
                    field_path = parts[1].strip()
                    # Determine category from path
                    path_parts = field_path.split('.')
                    if len(path_parts) > 1:
                        if path_parts[0] == 'gameData':
                            if 'teams' in path_parts:
                                category = 'Team Data'
                            elif 'players' in path_parts:
                                category = 'Player Data'
                            elif 'venue' in path_parts:
                                category = 'Venue Data'
                            elif 'weather' in path_parts:
                                category = 'Weather Data'
                            elif 'game' in path_parts:
                                category = 'Game Info'
                            elif 'review' in path_parts:
                                category = 'Review Data'
                            else:
                                category = 'Game Metadata'
                        elif path_parts[0] == 'liveData':
                            if 'boxscore' in path_parts:
                                category = 'Boxscore Data'
                            elif 'plays' in path_parts:
                                category = 'Play Data'
                            elif 'linescore' in path_parts:
                                category = 'Linescore Data'
                            else:
                                category = 'Live Game Data'
                        else:
                            category = 'Other'
                    else:
                        category = 'Root Level'
                    
                    # Add the field to its category
                    field_name = path_parts[-1]
                    field_groups[category].append((field_name, field_path))
    
    return field_groups

def get_schema_fields() -> Dict[str, Dict[str, str]]:
    """Get all fields defined in the core schema files with their locations."""
    schema_fields = {}
    
    # Combine all schema definitions
    all_schemas = {
        'reference': reference_schema,
        'team_player': team_player_schema,
        'game_play': game_play_schema,
        'play_detail': play_detail_schema
    }
    
    # Extract fields from each table definition with their locations
    for schema_name, schema in all_schemas.items():
        for table_name, table_def in schema.items():
            for column_name in table_def.get('columns', {}).keys():
                normalized_name = normalize_field_name(column_name)
                schema_fields[normalized_name] = {
                    'original_name': column_name,
                    'table': table_name,
                    'schema': schema_name
                }
    
    return schema_fields

def normalize_field_name(field: str) -> str:
    """Normalize field names for comparison."""
    # Convert camelCase to snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # Remove common prefixes/suffixes
    name = re.sub(r'^(game_data_|live_data_)', '', name)
    name = re.sub(r'_data$', '', name)
    
    return name

def analyze_coverage(json_fields: Dict[str, List[str]], schema_fields: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    """Analyze which fields are covered and which are missing."""
    coverage_by_category = {}
    
    for category, fields in json_fields.items():
        category_fields = []
        for field_name, full_path in fields:
            normalized_name = normalize_field_name(field_name)
            schema_match = schema_fields.get(normalized_name)
            is_covered = schema_match is not None
            
            # Create match info string if covered
            match_info = ""
            if is_covered:
                match_info = f"{schema_match['schema']}.{schema_match['table']}.{schema_match['original_name']}"
            
            category_fields.append((field_name, full_path, is_covered, match_info))
        
        # Calculate category statistics
        total = len(category_fields)
        covered = sum(1 for f in category_fields if f[2])
        coverage = (covered / total * 100) if total > 0 else 0
        
        coverage_by_category[category] = {
            'fields': category_fields,
            'total': total,
            'covered': covered,
            'coverage': coverage
        }
    
    return coverage_by_category

def generate_report(coverage_by_category: Dict[str, Dict[str, Any]]) -> str:
    """Generate a markdown report of the analysis."""
    # Calculate overall statistics
    total_fields = sum(cat['total'] for cat in coverage_by_category.values())
    total_covered = sum(cat['covered'] for cat in coverage_by_category.values())
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
        "## Coverage by Category"
    ]
    
    # Add category summaries
    categories = sorted(coverage_by_category.keys())
    for i, category in enumerate(categories):
        cat_data = coverage_by_category[category]
        report.extend([
            "",
            category_separator if i > 0 else "",  # Add separator between categories, but not before first one
            "",
            f"### {category}",
            f"- Fields: {cat_data['total']}",
            f"- Covered: {cat_data['covered']}",
            f"- Coverage: {cat_data['coverage']:.2f}%",
            ""
        ])
        
        # Group fields by base name
        field_groups = defaultdict(list)
        for field_name, full_path, is_covered, match_info in sorted(cat_data['fields']):
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
    report.extend([
        category_separator,
        "",
        "End of Report",
        major_separator
    ])
    
    return "\n".join(report)

def main():
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
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"Report generated: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing schemas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 