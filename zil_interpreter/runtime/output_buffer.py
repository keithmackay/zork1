"""Output buffer for game text."""

from typing import List


class OutputBuffer:
    """Manages game output text."""

    def __init__(self):
        self._buffer: List[str] = []

    def write(self, text: str) -> None:
        """Write text to buffer without newline.

        Args:
            text: Text to write
        """
        self._buffer.append(text)

    def writeln(self, text: str) -> None:
        """Write text to buffer with newline.

        Args:
            text: Text to write
        """
        self._buffer.append(text)
        self._buffer.append("\n")

    def tell(self, text: str) -> None:
        """Write text in TELL format (for ZIL TELL directive).

        Args:
            text: Text to output
        """
        self.write(text)

    def get_output(self) -> str:
        """Get current buffer contents.

        Returns:
            Buffer contents as string
        """
        return "".join(self._buffer)

    def flush(self) -> str:
        """Get buffer contents and clear buffer.

        Returns:
            Buffer contents as string
        """
        output = self.get_output()
        self._buffer.clear()
        return output

    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer.clear()
