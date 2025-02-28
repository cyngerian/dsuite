from typing import Dict, List, Set
import networkx as nx
from ..models.column import Column, Index

class SchemaValidator:
    """Validate database schema definitions."""
    
    def __init__(self, schema: Dict):
        self.schema = schema
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """
        Validate entire schema.
        Returns True if no errors (warnings are okay).
        """
        self.errors = []
        self.warnings = []
        
        # Validate schema structure
        self._validate_schema_structure()
        
        # Validate table dependencies
        self._validate_dependencies()
        
        # Validate individual tables
        self._validate_tables()
        
        # Validate naming conventions
        self._validate_naming()
        
        return len(self.errors) == 0

    def _validate_schema_structure(self):
        """Validate overall schema structure."""
        if not isinstance(self.schema, dict):
            self.errors.append("Schema must be a dictionary")
            return
        
        required_sections = {"CORE_TABLES", "ANALYSIS_TABLES"}
        missing_sections = required_sections - set(self.schema.keys())
        if missing_sections:
            self.errors.append(f"Missing required sections: {missing_sections}")

    def _validate_dependencies(self):
        """Validate table dependencies and check for cycles."""
        G = nx.DiGraph()
        
        # Build dependency graph
        for section in self.schema.values():
            for subsection in section.values():
                for table_name, table_def in subsection.items():
                    G.add_node(table_name)
                    
                    # Add edges for foreign key dependencies
                    for col in table_def["columns"].values():
                        if col.foreign_key:
                            ref_table = col.foreign_key["table"]
                            G.add_edge(ref_table, table_name)
                            
                            # Check if referenced table exists
                            if not self._table_exists(ref_table):
                                self.errors.append(
                                    f"Table '{table_name}' references non-existent "
                                    f"table '{ref_table}'"
                                )
        
        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                self.errors.append(
                    f"Circular dependencies detected: {cycles}"
                )
        except nx.NetworkXError:
            self.errors.append("Error checking for circular dependencies")

    def _validate_tables(self):
        """Validate individual table definitions."""
        for section in self.schema.values():
            for subsection in section.values():
                for table_name, table_def in subsection.items():
                    self._validate_table(table_name, table_def)

    def _validate_table(self, table_name: str, table_def: Dict):
        """Validate a single table definition."""
        # Check required fields
        if "columns" not in table_def:
            self.errors.append(f"Table '{table_name}' missing columns definition")
            return
        
        if "type" not in table_def:
            self.warnings.append(f"Table '{table_name}' missing type definition")
        
        # Validate columns
        self._validate_columns(table_name, table_def["columns"])
        
        # Validate indices
        if "indices" in table_def:
            self._validate_indices(table_name, table_def["indices"], 
                                 table_def["columns"])

    def _validate_columns(self, table_name: str, columns: Dict[str, Column]):
        """Validate column definitions."""
        if not columns:
            self.errors.append(f"Table '{table_name}' has no columns")
            return
        
        # Check for primary key
        has_primary_key = any(col.primary_key for col in columns.values())
        if not has_primary_key:
            self.warnings.append(f"Table '{table_name}' has no primary key")
        
        # Validate individual columns
        for col_name, col in columns.items():
            col_errors = col.validate()
            if col_errors:
                self.errors.extend(
                    f"Table '{table_name}', column '{col_name}': {err}" 
                    for err in col_errors
                )

    def _validate_indices(self, table_name: str, indices: List[Index], 
                         columns: Dict[str, Column]):
        """Validate index definitions."""
        for idx in indices:
            # Validate index definition
            idx_errors = idx.validate()
            if idx_errors:
                self.errors.extend(
                    f"Table '{table_name}', index '{idx.name}': {err}" 
                    for err in idx_errors
                )
            
            # Check that referenced columns exist
            for col_name in idx.columns:
                if col_name not in columns:
                    self.errors.append(
                        f"Table '{table_name}', index '{idx.name}' references "
                        f"non-existent column '{col_name}'"
                    )

    def _validate_naming(self):
        """Validate naming conventions."""
        for section in self.schema.values():
            for subsection in section.values():
                for table_name in subsection.keys():
                    if not table_name.islower():
                        self.warnings.append(
                            f"Table name '{table_name}' should be lowercase"
                        )
                    if not table_name.isidentifier():
                        self.errors.append(
                            f"Invalid table name '{table_name}'"
                        )

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the schema."""
        for section in self.schema.values():
            for subsection in section.values():
                if table_name in subsection:
                    return True
        return False

    def get_validation_report(self) -> str:
        """Get formatted validation report."""
        report = []
        if self.errors:
            report.append("Errors:")
            report.extend(f"  - {err}" for err in self.errors)
        if self.warnings:
            report.append("\nWarnings:")
            report.extend(f"  - {warn}" for warn in self.warnings)
        if not report:
            report.append("Schema validation passed with no issues.")
        return "\n".join(report)
