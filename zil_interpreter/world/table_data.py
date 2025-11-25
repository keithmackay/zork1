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

    def get_byte(self, byte_index: int) -> int:
        """Get byte at byte index (2 bytes per word)."""
        word_index = byte_index // 2
        if word_index >= len(self.data):
            raise IndexError(f"Byte index {byte_index} out of range for table '{self.name}'")
        word = self.data[word_index]
        if byte_index % 2 == 0:
            return (word >> 8) & 0xFF  # High byte
        else:
            return word & 0xFF  # Low byte

    def put_byte(self, byte_index: int, value: int) -> None:
        """Set byte at byte index."""
        word_index = byte_index // 2
        if word_index >= len(self.data):
            raise IndexError(f"Byte index {byte_index} out of range for table '{self.name}'")
        word = self.data[word_index]
        if byte_index % 2 == 0:
            # Set high byte, preserve low byte
            self.data[word_index] = ((value & 0xFF) << 8) | (word & 0xFF)
        else:
            # Preserve high byte, set low byte
            self.data[word_index] = (word & 0xFF00) | (value & 0xFF)

    def __len__(self) -> int:
        """Return table length."""
        return len(self.data)
