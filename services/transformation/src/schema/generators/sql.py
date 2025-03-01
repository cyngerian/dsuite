"""SQL generation utilities."""

from typing import Dict, List

import networkx as nx


class SQLGenerator:
    """SQL Generator class for creating SQL statements."""

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

    @staticmethod
    def generate_create_table(
        table_name: str,
        columns: Dict[str, str],
        primary_key: str = None,
        indexes: List[str] = None,
    ) -> str:
        """
        Generate a CREATE TABLE SQL statement.

        Args:
            table_name: Name of the table
            columns: Dictionary of column names and their SQL types
            primary_key: Name of the primary key column
            indexes: List of column names to create indexes for

        Returns:
            SQL statement for creating the table
        """
        columns_str = []
        for col_name, col_type in columns.items():
            col_def = [col_name, col_type]
            if primary_key == col_name:
                col_def.append("PRIMARY KEY")
            columns_str.append(" ".join(col_def))

        sql = [
            f"CREATE TABLE IF NOT EXISTS {table_name} (",
            ",\n    ".join(columns_str),
            ");",
        ]

        # Add indices
        if indexes:
            for idx in indexes:
                idx_name = f"idx_{table_name}_{idx}"
                sql.append(
                    f"CREATE INDEX IF NOT EXISTS {idx_name} " f"ON {table_name}({idx});"
                )

        return "\n".join(sql)

    def generate_all_tables(self) -> str:
        """Generate all CREATE TABLE statements in correct order."""
        statements = []
        for table_name in self.get_table_creation_order():
            table_def = self._find_table_def(table_name)
            if table_def:
                statements.append(
                    self.generate_create_table(
                        table_name,
                        table_def["columns"],
                        table_def.get("primary_key"),
                        table_def.get("indices", []),
                    )
                )
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
