# Column and Index class definitions from original schema.py
# TODO: Move relevant code here

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Column:
    """Column definition with validation."""

    type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[Dict[str, str]] = None
    default: Optional[str] = None
    description: Optional[str] = None

    def validate(self) -> List[str]:
        """Validate column definition."""
        errors = []
        if not self.type:
            errors.append("Column type is required")
        if self.foreign_key and not all(
            k in self.foreign_key for k in ["table", "column"]
        ):
            errors.append("Foreign key must specify table and column")
        return errors


@dataclass
class Index:
    """Index definition with validation."""

    columns: List[str]
    unique: bool = False
    name: Optional[str] = None

    def validate(self) -> List[str]:
        """Validate index definition."""
        errors = []
        if not self.columns:
            errors.append("Index must have at least one column")
        return errors


# Common column patterns
class Columns:
    """Reusable column definitions."""

    ID = Column("SERIAL", nullable=False, primary_key=True)
    CREATED_AT = Column("TIMESTAMP", default="CURRENT_TIMESTAMP")
    UPDATED_AT = Column("TIMESTAMP", default="CURRENT_TIMESTAMP")
    ACTIVE = Column("BOOLEAN", default="true")

    @staticmethod
    def foreign_key(table: str, nullable: bool = True) -> Column:
        return Column(
            "INTEGER", nullable=nullable, foreign_key={"table": table, "column": "id"}
        )

    @staticmethod
    def varchar(length: int, nullable: bool = True) -> Column:
        return Column(f"VARCHAR({length})", nullable=nullable)

    @staticmethod
    def decimal(precision: int, scale: int, nullable: bool = True) -> Column:
        return Column(f"DECIMAL({precision},{scale})", nullable=nullable)
