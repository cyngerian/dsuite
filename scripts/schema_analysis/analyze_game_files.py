#!/usr/bin/env python3
"""
Analyze MLB game files stored in MinIO to document their JSON schema structure.
This script will:
1. Connect to MinIO and retrieve sample game files
2. Analyze the JSON structure of these files
3. Generate schema documentation
4. Identify common patterns and variations
5. Generate schema visualization
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from graphviz import Digraph
from minio.error import S3Error

from minio import Minio

from ..config import (
    BUCKET_CURRENT,
    BUCKET_HISTORICAL,
    BUCKET_LIVE,
    OUTPUT_DIR,
    SAMPLE_SIZE,
)

MINIO_CONFIG: dict[str, str] = {
    "endpoint": str(os.getenv("MINIO_ENDPOINT", "localhost:9000")),
    "access_key": str(os.getenv("MINIO_ACCESS_KEY", "minioadmin")),
    "secret_key": str(os.getenv("MINIO_SECRET_KEY", "minioadmin")),
    "secure": str(os.getenv("MINIO_SECURE", "false")),
}

# Common patterns in MLB data
COMMON_PATTERNS = {
    "player": ["id", "fullName", "firstName", "lastName", "primaryNumber"],
    "team": ["id", "name", "abbreviation", "teamName", "locationName"],
    "game": ["id", "type", "season", "dateTime", "status"],
    "venue": ["id", "name"],
    "position": ["code", "name", "type", "abbreviation"],
    "stats": ["batting", "pitching", "fielding"],
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

        # Create visualizations directory
        viz_dir = schema_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created/verified visualizations directory: {viz_dir.absolute()}")

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

    def identify_entities(
        self, schema: Dict[str, Set[str]]
    ) -> List[Tuple[str, Dict[str, str], str]]:
        """
        Identify potential database entities from schema.

        Args:
            schema: Schema definition from analyze_json_structure

        Returns:
            List of tuples containing (entity_name, fields, parent_entity)
        """
        entities: List[Tuple[str, Dict[str, str], str]] = []
        current_entity: Dict[str, str] = {}
        arrays_found: Dict[str, str] = {}

        for path, types in schema.items():
            parts = path.split(".")
            field_name = parts[-1]
            parent_path = ".".join(parts[:-1])

            # Skip array markers but record their parent paths
            if field_name == "[]":
                arrays_found[parent_path] = parent_path.split(".")[-1]
                continue

            # Handle array item fields
            if "[]" in path:
                array_path = path[: path.index("[]")]
                entity_name = array_path.split(".")[-1]
                parent_entity = ".".join(array_path.split(".")[:-1])
                field_path = path[path.index("[]") + 2 :]

                # Find or create entity for this array
                array_entity = None
                for e, f, p in entities:
                    if e == entity_name:
                        array_entity = (e, f, p)
                        break

                if not array_entity:
                    array_entity = (entity_name, {}, parent_entity)
                    entities.append(array_entity)

                # Add field to array entity
                array_entity[1][field_path] = list(types)[0]
                continue

            # Handle regular fields and nested objects
            if "object" in types:
                # This is a nested object - might be a separate entity
                if any(p.startswith(path + ".") for p in schema.keys() if p != path):
                    entity_name = field_name
                    parent_entity = parent_path
                    nested_fields = {
                        k.replace(path + ".", ""): list(v)[0]
                        for k, v in schema.items()
                        if k.startswith(path + ".")
                        and k != path
                        and "object" not in v
                        and "array" not in v
                    }
                    if nested_fields:
                        entities.append((entity_name, nested_fields, parent_entity))
            else:
                # Regular field
                current_entity[field_name] = list(types)[0]

        # Add root entity if it has fields
        if current_entity:
            entities.insert(0, ("root", current_entity, ""))

        return entities

    def generate_schema_graph(
        self, entities: List[Tuple[str, Dict[str, str], str]], bucket_name: str
    ) -> None:
        """
        Generate a visual representation of the schema using Graphviz.

        Args:
            entities: List of entities with their fields and parent relationships
            bucket_name: Name of the bucket for output file naming
        """
        dot = Digraph(comment=f"Schema for {bucket_name}")
        dot.attr(rankdir="LR")  # Left to right layout

        # Add nodes for each entity
        for entity_name, fields, _ in entities:
            # Create HTML-like label for entity
            label = (
                "<"  # Start HTML-like label
                '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">'
                f'<TR><TD PORT="title" BGCOLOR="#E0E0E0"><B>{entity_name}</B></TD></TR>'
            )

            # Add fields
            for field_name, field_type in fields.items():
                label += (
                    f'<TR><TD PORT="{field_name}" ALIGN="LEFT">'
                    f"{field_name}: {field_type}</TD></TR>"
                )

            label += "</TABLE>>"

            dot.node(entity_name, label=label)

        # Add edges for relationships
        for entity_name, _, parent in entities:
            if parent:
                # Create edge from parent to child
                dot.edge(parent, entity_name)

        # Save the graph
        output_path = os.path.join(
            OUTPUT_DIR, "visualizations", f"{bucket_name}_schema"
        )
        dot.render(output_path, format="png", cleanup=True)
        print(f"Generated schema visualization: {output_path}.png")

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
        self,
        schema: Dict[str, Set[str]],
        entities: List[Tuple[str, Dict[str, str], str]],
        bucket_name: str,
    ) -> None:
        """
        Generate markdown documentation for the schema.

        Args:
            schema: Schema definition to document
            entities: List of entities with their fields and parent relationships
            bucket_name: Name of the bucket being documented
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_file = os.path.join(OUTPUT_DIR, f"{bucket_name}_schema.md")

        with open(output_file, "w") as f:
            f.write(f"# {bucket_name} Schema Documentation\n\n")
            f.write(f"Generated on: {timestamp}\n\n")

            # Document entities and their relationships
            f.write("## Entities\n\n")
            for entity_name, fields, parent in entities:
                f.write(f"### {entity_name}\n")
                if parent:
                    f.write(f"Parent: `{parent}`\n\n")
                f.write("| Field | Type |\n")
                f.write("|-------|------|\n")
                for field_name, field_type in fields.items():
                    f.write(f"| {field_name} | {field_type} |\n")
                f.write("\n")

            # Document raw field paths
            f.write("## Raw Field Paths\n\n")
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

    def identify_patterns(self, schema: Dict[str, Set[str]]) -> Dict[str, List[str]]:
        """
        Identify common patterns in the schema structure.

        Args:
            schema: Schema definition from analyze_json_structure

        Returns:
            Dict[str, List[str]]: Mapping of pattern names to matching field paths
        """
        patterns: Dict[str, List[str]] = {k: [] for k in COMMON_PATTERNS}

        # Group fields by their parent path
        field_groups: Dict[str, Set[str]] = {}
        for path in schema:
            parts = path.split(".")
            if len(parts) > 1:
                parent = ".".join(parts[:-1])
                field = parts[-1]
                if parent not in field_groups:
                    field_groups[parent] = set()
                field_groups[parent].add(field)

        # Match field groups against common patterns
        for parent, fields in field_groups.items():
            for pattern_name, pattern_fields in COMMON_PATTERNS.items():
                # Check if this field group matches the pattern
                if all(f in fields for f in pattern_fields):
                    patterns[pattern_name].append(parent)

        return patterns

    def _clean_name(self, name: str) -> str:
        """Clean a name (table or column) to be SQL-friendly."""
        # Remove array markers
        name = name.replace("[]", "_array")
        # Convert camelCase to snake_case
        name = "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip(
            "_"
        )
        # Convert dots to underscores
        name = name.replace(".", "_")
        # Make lowercase
        name = name.lower()
        # Remove any other special characters
        name = "".join(c if c.isalnum() or c == "_" else "" for c in name)
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = "t" + name
        # Remove duplicate underscores
        while "__" in name:
            name = name.replace("__", "_")
        # Remove trailing underscore
        name = name.rstrip("_")
        return name

    def _clean_table_name(self, name: str) -> str:
        """Clean a table name to be SQL-friendly."""
        # For tables, we want to keep 'items' instead of 'array'
        name = name.replace("[]", "_items")
        return self._clean_name(name)

    def suggest_table_splits(
        self, schema: Dict[str, Set[str]], patterns: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest how to split the schema into tables.

        Args:
            schema: Schema definition from analyze_json_structure
            patterns: Identified patterns in the schema

        Returns:
            List[Dict[str, Any]]: List of suggested tables with their fields
            and relationships
        """
        tables: List[Dict[str, Any]] = []
        processed_paths: Set[str] = set()

        # First, create tables for identified patterns
        for pattern_name, pattern_paths in patterns.items():
            for path in pattern_paths:
                if path in processed_paths:
                    continue

                # Generate a meaningful table name based on path context
                path_parts = path.split(".")
                context = path_parts[-2] if len(path_parts) > 1 else ""
                table_name = f"{context}_{pattern_name}" if context else pattern_name
                table_name = self._clean_table_name(table_name)

                table: Dict[str, Any] = {
                    "name": table_name,
                    "source_path": path,
                    "fields": {},
                    "relationships": [],
                }

                # Add fields from the pattern
                for field in COMMON_PATTERNS[pattern_name]:
                    full_path = f"{path}.{field}"
                    if full_path in schema:
                        table["fields"][field] = list(schema[full_path])[0]

                # Add any additional fields at this level
                for full_path, types in schema.items():
                    if (
                        full_path.startswith(f"{path}.")
                        and "object" not in types
                        and "array" not in types
                    ):
                        field = full_path.replace(f"{path}.", "")
                        if "." not in field:  # Only direct fields
                            table["fields"][field] = list(types)[0]

                tables.append(table)
                processed_paths.add(path)

        # Then handle arrays, which often indicate one-to-many relationships
        for path, types in schema.items():
            if "array" in types and path not in processed_paths:
                # Generate a meaningful table name for array items
                path_parts = path.split(".")
                array_name = path_parts[-1]
                parent_context = path_parts[-2] if len(path_parts) > 1 else ""
                table_name = f"{parent_context}_{array_name}_items"
                table_name = self._clean_table_name(table_name)

                table = {
                    "name": table_name,
                    "source_path": path,
                    "fields": {},
                    "relationships": [],
                }

                # Add fields from array items
                array_prefix = f"{path}[]."
                for full_path, field_types in schema.items():
                    if full_path.startswith(array_prefix):
                        field = full_path.replace(array_prefix, "")
                        if "." not in field:  # Only direct fields
                            table["fields"][field] = list(field_types)[0]

                if table["fields"]:  # Only add if we found fields
                    tables.append(table)
                    processed_paths.add(path)

        return tables

    def generate_relationships(
        self, tables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate relationship mappings between tables.

        Args:
            tables: List of suggested tables

        Returns:
            List[Dict[str, Any]]: List of relationships between tables
        """
        relationships: List[Dict[str, Any]] = []

        for table in tables:
            source_path = table["source_path"]

            # Check for parent-child relationships based on paths
            for other_table in tables:
                if other_table == table:
                    continue

                other_path = other_table["source_path"]

                # If one path is a parent of another
                if other_path.startswith(f"{source_path}."):
                    relationships.append(
                        {
                            "from_table": table["name"],
                            "to_table": other_table["name"],
                            "type": "one_to_many",
                            "based_on": "path_hierarchy",
                        }
                    )

                # Check for ID fields that might indicate relationships
                for field in table["fields"]:
                    if field.endswith("_id") or field.endswith("Id"):
                        referenced_entity = field.replace("_id", "").replace("Id", "")
                        if referenced_entity.lower() in other_table["name"].lower():
                            relationships.append(
                                {
                                    "from_table": table["name"],
                                    "to_table": other_table["name"],
                                    "type": "many_to_one",
                                    "based_on": "id_field",
                                    "field": field,
                                }
                            )

        return relationships

    def create_normalized_schema(
        self, tables: List[Dict[str, Any]], relationships: List[Dict[str, Any]]
    ) -> str:
        """
        Create normalized SQL schema from tables and relationships.

        Args:
            tables: List of suggested tables
            relationships: List of relationships between tables

        Returns:
            str: SQL schema creation statements
        """
        sql_statements = []
        processed_tables = set()

        def format_column_list(columns: List[str], indent: int = 4) -> str:
            """Format a list of columns with proper indentation."""
            indent_str = " " * indent
            return f",\n{indent_str}".join(columns)

        def flatten_object(
            obj: Dict[str, Any], prefix: str = ""
        ) -> List[Tuple[str, str]]:
            """Flatten a nested object into column definitions."""
            columns = []
            for key, value in obj.items():
                col_name = self._clean_name(f"{prefix}{key}" if prefix else key)
                if isinstance(value, dict):
                    columns.extend(flatten_object(value, f"{col_name}_"))
                elif isinstance(value, list):
                    # Create a new table for array types
                    array_table_name = self._clean_table_name(
                        f"{table_name}_{col_name}_items"
                    )
                    if array_table_name not in processed_tables:
                        if isinstance(value[0], dict):
                            array_columns = flatten_object(value[0])
                            array_fields = [
                                f"{col[0]} {col[1]}" for col in array_columns
                            ]
                            array_fields.insert(0, "id SERIAL PRIMARY KEY")
                            array_fields.insert(
                                1,
                                f"{table_name}_id INTEGER REFERENCES {table_name}(id)",
                            )

                            create_array_table = f"""--
-- Table: {array_table_name}
--
CREATE TABLE {array_table_name} (
    {format_column_list(array_fields)}
);

COMMENT ON TABLE {array_table_name} IS 'Array items from {table["source_path"]}';"""
                            sql_statements.append(create_array_table)
                            processed_tables.add(array_table_name)
                        else:
                            # For primitive arrays, use array type
                            sql_type = self._map_type_to_sql(type(value[0]).__name__)
                            columns.append((col_name, f"{sql_type}[]"))
                else:
                    columns.append(
                        (col_name, self._map_type_to_sql(type(value).__name__))
                    )
            return columns

        # Create tables
        for table in tables:
            table_name = self._clean_table_name(table["name"])
            if table_name in processed_tables:
                continue

            fields = []
            fields.append("id SERIAL PRIMARY KEY")

            # Add standard fields
            for field_name, field_type in sorted(table["fields"].items()):
                clean_field_name = self._clean_name(field_name)
                if isinstance(field_type, dict):
                    # Flatten nested objects
                    nested_fields = flatten_object(field_type, f"{clean_field_name}_")
                    fields.extend(f"{col[0]} {col[1]}" for col in nested_fields)
                else:
                    sql_type = self._map_type_to_sql(field_type)
                    fields.append(f"{clean_field_name} {sql_type}")

            # Add header comment and create table
            create_table = f"""--
-- Table: {table_name}
-- Source: {table["source_path"]}
--
CREATE TABLE {table_name} (
    {format_column_list(fields)}
);

COMMENT ON TABLE {table_name} IS 'Generated from {table["source_path"]}';"""
            sql_statements.append(create_table)
            processed_tables.add(table_name)

            # Create indexes for commonly queried fields
            index_fields = ["id", "name", "date", "type", "season"]
            index_statements = []
            for field in index_fields:
                clean_field = self._clean_name(field)
                if clean_field in [self._clean_name(f) for f in table["fields"].keys()]:
                    index_name = f"idx_{table_name}_{clean_field}"
                    index_statements.append(
                        f"CREATE INDEX {index_name} ON {table_name}({clean_field});"
                    )
            if index_statements:
                sql_statements.append("\n".join(index_statements))

        # Add foreign key constraints
        fk_statements = []
        for rel in relationships:
            if rel["type"] == "many_to_one":
                from_table = self._clean_table_name(rel["from_table"])
                to_table = self._clean_table_name(rel["to_table"])
                field = self._clean_name(rel.get("field", "id"))
                constraint = f"""ALTER TABLE {from_table}
    ADD CONSTRAINT fk_{from_table}_{to_table}
    FOREIGN KEY ({field})
    REFERENCES {to_table} (id);"""
                fk_statements.append(constraint)

        if fk_statements:
            sql_statements.append(
                "\n--\n-- Foreign Key Constraints\n--\n" + "\n\n".join(fk_statements)
            )

        return "\n\n".join(sql_statements)

    def _map_type_to_sql(self, field_type: str) -> str:
        """Map JSON schema types to SQL types."""
        type_mapping = {
            "str": "VARCHAR(255)",
            "string": "VARCHAR(255)",
            "int": "INTEGER",
            "float": "NUMERIC(10,2)",
            "bool": "BOOLEAN",
            "datetime": "TIMESTAMP WITH TIME ZONE",
            "date": "DATE",
            "time": "TIME",
            "object": "JSONB",  # Only use JSONB for truly dynamic objects
            "array": "JSONB",  # Only use JSONB for truly dynamic arrays
            "null": "VARCHAR(255)",
        }
        return type_mapping.get(field_type.lower(), "VARCHAR(255)")

    def analyze_bucket(self, bucket_name: str) -> None:
        """Analyze all sample files in a bucket."""
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
                if not sample_saved:
                    print(f"Attempting to save sample from {file_name}")
                    self.save_sample_json(data, bucket_name, file_name)
                    sample_saved = True
            else:
                print(f"No valid JSON data found in {file_name}")

        if schemas:
            merged_schema = self.merge_schemas(schemas)

            # Identify patterns and suggest table structure
            patterns = self.identify_patterns(merged_schema)
            tables = self.suggest_table_splits(merged_schema, patterns)
            relationships = self.generate_relationships(tables)

            # Generate normalized SQL schema
            sql_schema = self.create_normalized_schema(tables, relationships)

            # Save the normalized schema
            schema_file = os.path.join(
                OUTPUT_DIR, f"{bucket_name}_normalized_schema.sql"
            )
            with open(schema_file, "w") as f:
                f.write(sql_schema)
            print(f"Generated normalized schema: {schema_file}")

            # Generate documentation and visualization
            entities = self.identify_entities(merged_schema)
            self.generate_schema_documentation(merged_schema, entities, bucket_name)
            self.generate_schema_graph(entities, bucket_name)

            # Save pattern analysis
            pattern_file = os.path.join(OUTPUT_DIR, f"{bucket_name}_patterns.md")
            with open(pattern_file, "w") as f:
                f.write(f"# {bucket_name} Schema Patterns\n\n")
                for pattern, paths in patterns.items():
                    if paths:
                        f.write(f"## {pattern}\n")
                        for path in paths:
                            f.write(f"- `{path}`\n")
                        f.write("\n")
            print(f"Generated pattern analysis: {pattern_file}")

            print(f"Schema analysis complete for {bucket_name}")
        else:
            print(f"No valid schemas generated for {bucket_name}")

    def analyze_all_buckets(self) -> None:
        """Analyze all MLB data buckets."""
        for bucket in [BUCKET_CURRENT, BUCKET_HISTORICAL, BUCKET_LIVE]:
            self.analyze_bucket(bucket)


def main() -> None:
    """Main entry point for schema analysis."""
    try:
        print("Initializing MinIO client...")
        analyzer = SchemaAnalyzer()
        print("Testing MinIO connection...")

        # Get one sample file
        sample_files = analyzer.get_sample_files(BUCKET_HISTORICAL)
        if not sample_files:
            print("No files found to analyze")
            return

        # Process just the first file
        file_name = sample_files[0]
        print(f"\nProcessing {file_name}")
        data = analyzer.read_json_file(BUCKET_HISTORICAL, file_name)
        if not data:
            print("No valid JSON data found")
            return

        print("Analyzing JSON structure...")
        schema = analyzer.analyze_json_structure(data)

        # Generate schema
        patterns = analyzer.identify_patterns(schema)
        tables = analyzer.suggest_table_splits(schema, patterns)
        relationships = analyzer.generate_relationships(tables)

        # Create and save SQL schema
        sql_schema = analyzer.create_normalized_schema(tables, relationships)
        schema_file = os.path.join(
            OUTPUT_DIR, f"{BUCKET_HISTORICAL}_normalized_schema.sql"
        )
        with open(schema_file, "w") as f:
            f.write(sql_schema)
        print(f"\nGenerated normalized schema: {schema_file}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback

        traceback.print_exc()


def get_field_type(value: Any) -> str:
    """
    Get the SQL field type for a given value.

    Args:
        value: The value to determine the type for

    Returns:
        str: The SQL field type name
    """
    if value is None:
        return "NULL"
    elif isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "FLOAT"
    elif isinstance(value, str):
        return "VARCHAR"
    elif isinstance(value, list):
        return "ARRAY"
    elif isinstance(value, dict):
        return "JSONB"
    else:
        return "VARCHAR"  # Default to VARCHAR for unknown types


def extract_field_types(data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extract field types from a list of dictionaries.

    Args:
        data: List of dictionaries to analyze

    Returns:
        Dict[str, str]: Mapping of field names to their SQL types
    """
    field_types: Dict[str, str] = {}

    for item in data:
        for field, value in item.items():
            field_type = get_field_type(value)
            if field in field_types:
                # If field already exists, only update if current type is NULL
                if field_types[field] == "NULL":
                    field_types[field] = field_type
            else:
                field_types[field] = field_type

    return field_types


async def analyze_game_files(data_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Analyze game files in the specified directory.

    Args:
        data_path: Path to the directory containing game files

    Returns:
        Dict[str, Dict[str, Any]]: Analysis results containing game and play data
    """
    return {
        "games": {},  # Placeholder for game analysis
        "plays": {},  # Placeholder for play analysis
    }


if __name__ == "__main__":
    main()
