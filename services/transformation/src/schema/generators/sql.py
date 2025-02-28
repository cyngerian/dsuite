from typing import Dict, List, Set
from ..models.column import Column, Index
import networkx as nx

class SQLGenerator:
    """Generate SQL DDL statements."""
    
    def __init__(self, schema: Dict):
        self.schema = schema
        self.table_deps = self._build_dependency_graph()

    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build a directed graph of table dependencies."""
        G = nx.DiGraph()
        
        # Add all tables as nodes
        for section in self.schema.values():
            for subsection in section.values():
                for table_name, table_def in subsection.items():
                    G.add_node(table_name)
                    
                    # Add edges for foreign key dependencies
                    for col in table_def["columns"].values():
                        if col.foreign_key:
                            G.add_edge(col.foreign_key["table"], table_name)
        
        return G

    def get_table_creation_order(self) -> List[str]:
        """Get tables in topologically sorted order."""
        try:
            return list(nx.topological_sort(self.table_deps))
        except nx.NetworkXUnfeasible:
            raise ValueError("Circular dependencies detected in schema")

    def generate_create_table(self, table_name: str, table_def: Dict) -> str:
        """Generate CREATE TABLE statement for a single table."""
        columns = []
        for col_name, col in table_def["columns"].items():
            col_def = [col_name, col.type]
            if col.primary_key:
                col_def.append("PRIMARY KEY")
            if not col.nullable:
                col_def.append("NOT NULL")
            if col.default:
                col_def.append(f"DEFAULT {col.default}")
            if col.foreign_key:
                fk = col.foreign_key
                col_def.append(f"REFERENCES {fk['table']}({fk['column']})")
            columns.append(" ".join(col_def))
        
        sql = [
            f"-- {table_def.get('description', '')}",
            f"CREATE TABLE IF NOT EXISTS {table_name} (",
            ",\n    ".join(columns),
            ");"
        ]
        
        # Add indices
        for idx in table_def.get("indices", []):
            idx_name = idx.name or f"idx_{table_name}_{'_'.join(idx.columns)}"
            unique = "UNIQUE " if idx.unique else ""
            sql.append(
                f"CREATE {unique}INDEX IF NOT EXISTS {idx_name} "
                f"ON {table_name}({', '.join(idx.columns)});"
            )
        
        return "\n".join(sql)

    def generate_all_tables(self) -> str:
        """Generate all CREATE TABLE statements in correct order."""
        statements = []
        for table_name in self.get_table_creation_order():
            table_def = self._find_table_def(table_name)
            if table_def:
                statements.append(self.generate_create_table(table_name, table_def))
                statements.append("")  # Empty line between tables
        
        return "\n".join(statements)

    def _find_table_def(self, table_name: str) -> Dict:
        """Find table definition in schema."""
        for section in self.schema.values():
            for subsection in section.values():
                if table_name in subsection:
                    return subsection[table_name]
        return None

    def generate_drop_tables(self) -> str:
        """Generate DROP TABLE statements in reverse dependency order."""
        statements = []
        for table_name in reversed(self.get_table_creation_order()):
            statements.append(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        return "\n".join(statements)
