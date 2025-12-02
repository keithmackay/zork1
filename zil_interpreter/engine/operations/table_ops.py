"""Table and data structure operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation


class GetOperation(Operation):
    """GET - Get element from table at index."""

    @property
    def name(self) -> str:
        return "GET"

    def execute(self, args: list, evaluator) -> Any:
        """Get element from table at index.

        Args:
            args: [table, index]
            evaluator: Evaluator instance

        Returns:
            Element at index or None if invalid
        """
        if len(args) < 2:
            return None

        table = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])

        if not isinstance(index, int):
            return None

        if isinstance(table, list):
            try:
                return table[index]
            except (IndexError, TypeError):
                return None

        return None


class PutOperation(Operation):
    """PUT - Put element into table at index."""

    @property
    def name(self) -> str:
        return "PUT"

    def execute(self, args: list, evaluator) -> Any:
        """Put element into table at index.

        Args:
            args: [table, index, value]
            evaluator: Evaluator instance

        Returns:
            Value that was stored or None if invalid
        """
        if len(args) < 3:
            return None

        table = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])
        value = evaluator.evaluate(args[2])

        if not isinstance(index, int):
            return None

        if isinstance(table, list):
            try:
                table[index] = value
                return value
            except (IndexError, TypeError):
                return None

        return None


class GetbOperation(Operation):
    """GETB - Get byte from table at offset."""

    @property
    def name(self) -> str:
        return "GETB"

    def execute(self, args: list, evaluator) -> Any:
        """Get byte from table at offset.

        Args:
            args: [byte-table, offset]
            evaluator: Evaluator instance

        Returns:
            Byte value (0-255) or None if invalid
        """
        if len(args) < 2:
            return None

        table = evaluator.evaluate(args[0])
        offset = evaluator.evaluate(args[1])

        if not isinstance(offset, int):
            return None

        # Handle property reference tuples from GETPT
        if isinstance(table, tuple) and len(table) == 2:
            obj, prop_name = table
            if hasattr(obj, 'get_property'):
                table = obj.get_property(prop_name)

        # For lists of integers, treat as byte array
        if isinstance(table, list):
            try:
                value = table[offset]
                # Ensure byte range (0-255)
                if isinstance(value, int):
                    return value & 0xFF
                return value
            except (IndexError, TypeError):
                return None

        # For byte strings/bytearray
        if isinstance(table, (bytes, bytearray)):
            try:
                return table[offset]
            except IndexError:
                return None

        return None


class PutbOperation(Operation):
    """PUTB - Put byte into table at offset."""

    @property
    def name(self) -> str:
        return "PUTB"

    def execute(self, args: list, evaluator) -> Any:
        """Put byte into table at offset.

        Args:
            args: [byte-table, offset, value]
            evaluator: Evaluator instance

        Returns:
            Byte value that was stored or None if invalid
        """
        if len(args) < 3:
            return None

        table = evaluator.evaluate(args[0])
        offset = evaluator.evaluate(args[1])
        value = evaluator.evaluate(args[2])

        if not isinstance(offset, int) or not isinstance(value, int):
            return None

        # Truncate to byte range
        byte_value = value & 0xFF

        if isinstance(table, list):
            try:
                table[offset] = byte_value
                return byte_value
            except (IndexError, TypeError):
                return None

        if isinstance(table, bytearray):
            try:
                table[offset] = byte_value
                return byte_value
            except IndexError:
                return None

        return None


class LtableOperation(Operation):
    """LTABLE - Create length-prefixed table."""

    @property
    def name(self) -> str:
        return "LTABLE"

    def execute(self, args: list, evaluator) -> list:
        """Create length-prefixed table.

        Args:
            args: Elements to include in table
            evaluator: Evaluator instance

        Returns:
            List with [0] = count, [1..n] = elements
        """
        # Evaluate all arguments
        elements = [evaluator.evaluate(arg) for arg in args]

        # Create table with length prefix
        # [0] = count, [1..n] = elements
        return [len(elements)] + elements


class ItableOperation(Operation):
    """ITABLE - Create initialized table."""

    @property
    def name(self) -> str:
        return "ITABLE"

    def execute(self, args: list, evaluator) -> list:
        """Create initialized table with all elements set to initial value.

        Args:
            args: [initial-value, size]
            evaluator: Evaluator instance

        Returns:
            List of length 'size' with all elements = initial-value
        """
        if len(args) < 2:
            return []

        initial_value = evaluator.evaluate(args[0])
        size = evaluator.evaluate(args[1])

        if not isinstance(size, int) or size < 0:
            return []

        # Create table with all elements set to initial_value
        return [initial_value] * size


class TableOperation(Operation):
    """TABLE - Create bare table (no length prefix)."""

    @property
    def name(self) -> str:
        return "TABLE"

    def execute(self, args: list, evaluator) -> list:
        """Create bare table without length prefix.

        Args:
            args: Elements to include in table
            evaluator: Evaluator instance

        Returns:
            List of evaluated elements
        """
        # Evaluate all arguments and return as list
        return [evaluator.evaluate(arg) for arg in args]
