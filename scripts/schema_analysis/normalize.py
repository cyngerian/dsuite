"""Tools for normalizing nested JSON schemas into relational database structures."""

from typing import Any, Dict, List, Set, Tuple


def identify_entities(
    schema: Dict[str, Set[str]], prefix: str = ""
) -> List[Tuple[str, Dict[str, str]]]:
    """
    Identify potential database entities from nested JSON structure.

    Args:
        schema: Schema definition from SchemaAnalyzer
        prefix: Current path prefix for nested fields

    Returns:
        List of tuples containing (entity_name, field_definitions)
    """
    entities: List[Tuple[str, Dict[str, str]]] = []
    current_entity: Dict[str, str] = {}
    arrays_found: Dict[str, str] = {}

    for path, types in schema.items():
        parts = path.split(".")
        field_name = parts[-1]
        parent_path = ".".join(parts[:-1])

        # Skip array markers but record their parent paths
        if field_name == "[]":
            arrays_found[parent_path] = "array_table"
            continue

        # Handle array item fields
        if "[]" in path:
            array_path = path[: path.index("[]")]
            entity_name = array_path.split(".")[-1]
            field_path = path[path.index("[]") + 2 :]

            # Find or create entity for this array
            array_entity = next((e for e, _ in entities if e == entity_name), None)
            if not array_entity:
                entities.append((entity_name, {}))

            # Add field to array entity
            entity_dict = next(d for _, d in entities if _ == entity_name)
            entity_dict[field_path] = list(types)[0]
            continue

        # Handle regular fields and nested objects
        if "object" in types:
            # This is a nested object - might be a separate entity
            if any(p.startswith(path + ".") for p in schema.keys() if p != path):
                entity_name = field_name
                nested_fields = {
                    k.replace(path + ".", ""): list(v)[0]
                    for k, v in schema.items()
                    if k.startswith(path + ".")
                    and k != path
                    and "object" not in v
                    and "array" not in v
                }
                if nested_fields:
                    entities.append((entity_name, nested_fields))
        else:
            # Regular field
            current_entity[field_name] = list(types)[0]

    # Add root entity if it has fields
    if current_entity:
        entities.insert(0, ("root", current_entity))

    return entities


def suggest_relationships(
    entities: List[Tuple[str, Dict[str, str]]]
) -> List[Tuple[str, str, str]]:
    """
    Suggest relationships between identified entities.

    Args:
        entities: List of entities with their fields

    Returns:
        List of tuples containing (from_entity, to_entity, relationship_type)
    """
    relationships: List[Tuple[str, str, str]] = []
    entity_names = [name for name, _ in entities]

    for entity_name, fields in entities:
        # Look for potential foreign keys
        for field_name in fields:
            # Common patterns for foreign keys
            if field_name.endswith("_id") or field_name.endswith("Id"):
                referenced_entity = field_name.replace("_id", "").replace("Id", "")
                if referenced_entity in entity_names:
                    relationships.append(
                        (entity_name, referenced_entity, "many_to_one")
                    )

        # Look for array relationships from schema analysis
        for other_entity in entity_names:
            if other_entity.lower() in entity_name.lower():
                relationships.append((entity_name, other_entity, "one_to_many"))

    return relationships


def generate_table_definitions(
    entities: List[Tuple[str, Dict[str, str]]],
    relationships: List[Tuple[str, str, str]],
) -> Dict[str, Dict[str, Any]]:
    """
    Generate SQL table definitions from entities and relationships.

    Args:
        entities: List of entities with their fields
        relationships: List of relationships between entities

    Returns:
        Dictionary containing table definitions with fields and relationships
    """
    tables: Dict[str, Dict[str, Any]] = {}

    # Create base tables from entities
    for entity_name, fields in entities:
        tables[entity_name] = {
            "fields": fields.copy(),
            "primary_key": "id",
            "foreign_keys": [],
            "indexes": ["id"],
        }

    # Add relationship fields
    for from_entity, to_entity, rel_type in relationships:
        if rel_type == "many_to_one":
            # Add foreign key to the "many" side
            if from_entity in tables:
                fk_name = f"{to_entity}_id"
                tables[from_entity]["fields"][fk_name] = "INTEGER"
                tables[from_entity]["foreign_keys"].append(
                    {
                        "field": fk_name,
                        "references": {"table": to_entity, "field": "id"},
                    }
                )
                tables[from_entity]["indexes"].append(fk_name)

        elif rel_type == "one_to_many":
            # Add foreign key to the "many" side
            if to_entity in tables:
                fk_name = f"{from_entity}_id"
                tables[to_entity]["fields"][fk_name] = "INTEGER"
                tables[to_entity]["foreign_keys"].append(
                    {
                        "field": fk_name,
                        "references": {"table": from_entity, "field": "id"},
                    }
                )
                tables[to_entity]["indexes"].append(fk_name)

    return tables


def generate_migration_sql(table_definitions: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate SQL migration statements from table definitions.

    Args:
        table_definitions: Dictionary containing table definitions

    Returns:
        String containing SQL migration statements
    """
    sql_statements = []

    for table_name, definition in table_definitions.items():
        # Create table
        fields = []
        for field_name, field_type in definition["fields"].items():
            if field_name == definition["primary_key"]:
                fields.append(f"{field_name} SERIAL PRIMARY KEY")
            else:
                fields.append(f"{field_name} {field_type}")

        fields_str = ",\n    ".join(fields)
        create_table = f"""CREATE TABLE {table_name} (
    {fields_str}
);"""
        sql_statements.append(create_table)

        # Add foreign key constraints
        for fk in definition["foreign_keys"]:
            fk_constraint = (
                f"ALTER TABLE {table_name} "
                f"ADD CONSTRAINT fk_{table_name}_{fk['field']} "
                f"FOREIGN KEY ({fk['field']}) "
                f"REFERENCES {fk['references_table']} ({fk['references_field']});"
            )
            sql_statements.append(fk_constraint)

        # Add indexes
        for field in definition["indexes"]:
            if field != definition["primary_key"]:  # Skip PK, it's already indexed
                index = f"""
CREATE INDEX idx_{table_name}_{field}
ON {table_name} ({field});"""
                sql_statements.append(index)

    return "\\n".join(sql_statements)


def analyze_and_normalize_schema(
    schema: Dict[str, Set[str]]
) -> Tuple[List[Tuple[str, Dict[str, str]]], str]:
    """
    Analyze a JSON schema and generate normalized database structure.

    Args:
        schema: Schema definition from SchemaAnalyzer

    Returns:
        Tuple containing (entities, sql_migration)
    """
    # Identify entities from schema
    entities = identify_entities(schema)

    # Suggest relationships between entities
    relationships = suggest_relationships(entities)

    # Generate table definitions
    table_definitions = generate_table_definitions(entities, relationships)

    # Generate SQL migration
    sql_migration = generate_migration_sql(table_definitions)

    return entities, sql_migration
