# TableType enum from original schema.py
# TODO: Move relevant code here

from enum import Enum

class TableType(Enum):
    """Types of tables in the system."""
    REFERENCE = "reference"
    ENTITY = "entity"
    EVENT = "event"
    ANALYSIS = "analysis"

    def __str__(self) -> str:
        return self.value
