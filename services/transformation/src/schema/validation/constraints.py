from typing import Dict, List, Set
from ..models.column import Column

class ConstraintValidator:
    """Validate database constraints and relationships."""
    
    def __init__(self, schema: Dict):
        self.schema = schema
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """
        Validate all database constraints.
        Returns True if no errors (warnings are okay).
        """
        self.errors = []
        self.warnings = []
        
        # Validate foreign key constraints
        self._validate_foreign_keys()
        
        # Validate unique constraints
        self._validate_unique_constraints()
        
        # Validate check constraints
        self._validate_check_constraints()
        
        return len(self.errors) == 0

    def _validate_foreign_keys(self):
        """Validate foreign key relationships."""
        for section in self.schema.values():
            for subsection in section.values():
                for table_name, table_def in subsection.items():
                    for col_name, col in table_def["columns"].items():
                        if col.foreign_key:
                            self._validate_foreign_key(
                                table_name, col_name, col
                            )

    def _validate_foreign_key(self, table_name: str, col_name: str, col: Column):
        """Validate a single foreign key relationship."""
        fk = col.foreign_key
        ref_table = fk["table"]
        ref_column = fk["column"]
        
        # Find referenced table
        ref_table_def = self._find_table_def(ref_table)
        if not ref_table_def:
            self.errors.append(
                f"Foreign key {table_name}.{col_name} references "
                f"non-existent table {ref_table}"
            )
            return
        
        # Check referenced column
        if ref_column not in ref_table_def["columns"]:
            self.errors.append(
                f"Foreign key {table_name}.{col_name} references "
                f"non-existent column {ref_table}.{ref_column}"
            )
            return
        
        # Check data type compatibility
        ref_col = ref_table_def["columns"][ref_column]
        if col.type != ref_col.type:
            self.errors.append(
                f"Foreign key {table_name}.{col_name} type ({col.type}) "
                f"doesn't match referenced column {ref_table}.{ref_column} "
                f"type ({ref_col.type})"
            )

    def _validate_unique_constraints(self):
        """Validate unique constraints and indices."""
        for section in self.schema.values():
            for subsection in section.values():
                for table_name, table_def in subsection.items():
                    # Check unique indices
                    if "indices" in table_def:
                        for idx in table_def["indices"]:
                            if idx.unique:
                                self._validate_unique_index(
                                    table_name, idx, table_def["columns"]
                                )

    def _validate_unique_index(self, table_name: str, idx, columns: Dict[str, Column]):
        """Validate a unique index definition."""
        # Check that all columns in the unique index exist
        for col_name in idx.columns:
            if col_name not in columns:
                self.errors.append(
                    f"Unique index in table '{table_name}' references "
                    f"non-existent column '{col_name}'"
                )

    def _validate_check_constraints(self):
        """Validate check constraints (if any)."""
        # Add specific check constraint validation logic here
        pass

    def _find_table_def(self, table_name: str) -> Dict:
        """Find table definition in schema."""
        for section in self.schema.values():
            for subsection in section.values():
                if table_name in subsection:
                    return subsection[table_name]
        return None

    def get_validation_report(self) -> str:
        """Get formatted validation report."""
        report = []
        if self.errors:
            report.append("Constraint Errors:")
            report.extend(f"  - {err}" for err in self.errors)
        if self.warnings:
            report.append("\nConstraint Warnings:")
            report.extend(f"  - {warn}" for warn in self.warnings)
        if not report:
            report.append("Constraint validation passed with no issues.")
        return "\n".join(report)
