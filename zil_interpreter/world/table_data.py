"""Table data structure for ZIL arrays."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TableData:
    """Represents a ZIL table (array of words)."""

    name: str
    data: List[int] = field(default_factory=list)

    def get_word(self, index: int) -> int:
        """Get word at index."""
        if index < 0 or index >= len(self.data):
            raise IndexError(f"Table index {index} out of range for table '{self.name}'")
        return self.data[index]

    def put_word(self, index: int, value: int) -> None:
        """Set word at index."""
        if index < 0 or index >= len(self.data):
            raise IndexError(f"Table index {index} out of range for table '{self.name}'")
        self.data[index] = value

    def __len__(self) -> int:
        """Return table length."""
        return len(self.data)
