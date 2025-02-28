from typing import Dict, List, Set
from dataclasses import dataclass
from ..models.column import Column

@dataclass
class TableDiff:
    """Represents differences between old and new table definitions."""
    added_columns: Dict[str, Column]
    removed_columns: Set[str]
    modified_columns: Dict[str, Column]
    added_indices: List[str]
    removed_indices: List[str]

class MigrationGenerator:
    """Generate database migrations between schema versions."""
    
    def __init__(self, old_schema: Dict, new_schema: Dict):
        self.old_schema = old_schema
        self.new_schema = new_schema

    def generate_migration(self) -> List[str]:
        """Generate migration SQL."""
        statements = []
        
        # Find schema differences
        added_tables = self._find_added_tables()
        removed_tables = self._find_removed_tables()
        modified_tables = self._find_modified_tables()
        
        # Generate statements in correct order
        statements.extend(self._generate_drop_statements(removed_tables))
        statements.extend(self._generate_create_statements(added_tables))
        statements.extend(self._generate_alter_statements(modified_tables))
        
        return statements

    def _find_added_tables(self) -> Dict:
        """Find tables that exist in new schema but not in old."""
        return self._diff_dict_keys(self.new_schema, self.old_schema)

    def _find_removed_tables(self) -> Dict:
        """Find tables that exist in old schema but not in new."""
        return self._diff_dict_keys(self.old_schema, self.new_schema)

    def _find_modified_tables(self) -> Dict[str, TableDiff]:
        """Find tables that exist in both schemas but have differences."""
        modified = {}
        common_tables = set(self._get_all_tables(self.old_schema)) & \
                       set(self._get_all_tables(self.new_schema))
        
        for table_name in common_tables:
            old_table = self._find_table_def(table_name, self.old_schema)
            new_table = self._find_table_def(table_name, self.new_schema)
            
            if old_table and new_table:
                diff = self._compare_tables(old_table, new_table)
                if any([diff.added_columns, diff.removed_columns, 
                       diff.modified_columns, diff.added_indices, 
                       diff.removed_indices]):
                    modified[table_name] = diff
        
        return modified

    def _compare_tables(self, old_table: Dict, new_table: Dict) -> TableDiff:
        """Compare two table definitions and return differences."""
        old_cols = old_table["columns"]
        new_cols = new_table["columns"]
        
        added_cols = {k: v for k, v in new_cols.items() if k not in old_cols}
        removed_cols = set(k for k in old_cols if k not in new_cols)
        modified_cols = {
            k: v for k, v in new_cols.items() 
            if k in old_cols and v != old_cols[k]
        }
        
        old_indices = {idx.name for idx in old_table.get("indices", [])}
        new_indices = {idx.name for idx in new_table.get("indices", [])}
        
        return TableDiff(
            added_columns=added_cols,
            removed_columns=removed_cols,
            modified_columns=modified_cols,
            added_indices=list(new_indices - old_indices),
            removed_indices=list(old_indices - new_indices)
        )

    @staticmethod
    def _diff_dict_keys(dict1: Dict, dict2: Dict) -> Dict:
        """Return items from dict1 whose keys don't exist in dict2."""
        return {k: v for k, v in dict1.items() if k not in dict2}

    @staticmethod
    def _get_all_tables(schema: Dict) -> Set[str]:
        """Get all table names from schema."""
        tables = set()
        for section in schema.values():
            for subsection in section.values():
                tables.update(subsection.keys())
        return tables

    def _find_table_def(self, table_name: str, schema: Dict) -> Dict:
        """Find table definition in schema."""
        for section in schema.values():
            for subsection in section.values():
                if table_name in subsection:
                    return subsection[table_name]
        return None

    def _generate_drop_statements(self, tables: Dict) -> List[str]:
        """Generate DROP TABLE statements."""
        return [f"DROP TABLE IF EXISTS {table} CASCADE;" 
                for table in tables]

    def _generate_create_statements(self, tables: Dict) -> List[str]:
        """Generate CREATE TABLE statements."""
        from .sql import SQLGenerator
        sql_gen = SQLGenerator({"new": {"tables": tables}})
        return [sql_gen.generate_create_table(name, table) 
                for name, table in tables.items()]

    def _generate_alter_statements(self, modified: Dict[str, TableDiff]) -> List[str]:
        """Generate ALTER TABLE statements."""
        statements = []
        for table_name, diff in modified.items():
            # Drop removed columns
            for col_name in diff.removed_columns:
                statements.append(
                    f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {col_name};"
                )
            
            # Add new columns
            for col_name, col in diff.added_columns.items():
                col_def = [col_name, col.type]
                if not col.nullable:
                    col_def.append("NOT NULL")
                if col.default:
                    col_def.append(f"DEFAULT {col.default}")
                if col.foreign_key:
                    fk = col.foreign_key
                    col_def.append(
                        f"REFERENCES {fk['table']}({fk['column']})"
                    )
                statements.append(
                    f"ALTER TABLE {table_name} ADD COLUMN {' '.join(col_def)};"
                )
            
            # Modify existing columns
            for col_name, col in diff.modified_columns.items():
                statements.append(
                    f"ALTER TABLE {table_name} ALTER COLUMN {col_name} "
                    f"TYPE {col.type};"
                )
                
                if not col.nullable:
                    statements.append(
                        f"ALTER TABLE {table_name} ALTER COLUMN {col_name} "
                        "SET NOT NULL;"
                    )
                else:
                    statements.append(
                        f"ALTER TABLE {table_name} ALTER COLUMN {col_name} "
                        "DROP NOT NULL;"
                    )
            
            # Drop removed indices
            for idx_name in diff.removed_indices:
                statements.append(f"DROP INDEX IF EXISTS {idx_name};")
            
            # Add new indices
            for idx_name in diff.added_indices:
                statements.append(
                    f"CREATE INDEX {idx_name} ON {table_name}(...);")  # TODO
        
        return statements
