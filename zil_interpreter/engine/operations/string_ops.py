"""String operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import String


class ConcatOperation(Operation):
    """CONCAT - Concatenate strings."""

    @property
    def name(self) -> str:
        return "CONCAT"

    def execute(self, args: list, evaluator) -> str:
        """Concatenate all arguments as strings.

        Args:
            args: List of arguments to concatenate
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Concatenated string
        """
        result = ""
        for arg in args:
            val = evaluator.evaluate(arg)
            result += str(val)
        return result


class SubstringOperation(Operation):
    """SUBSTRING - Extract substring from string."""

    @property
    def name(self) -> str:
        return "SUBSTRING"

    def execute(self, args: list, evaluator) -> str:
        """Extract substring from start to end index.

        Args:
            args: [string, start, end] where start and end are 0-indexed
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Substring or empty string if invalid arguments
        """
        if len(args) < 3:
            return ""

        string_val = evaluator.evaluate(args[0])
        start = evaluator.evaluate(args[1])
        end = evaluator.evaluate(args[2])

        # Convert to string if needed
        string_val = str(string_val)

        # Validate indices
        if not isinstance(start, int) or not isinstance(end, int):
            return ""

        # Handle negative or invalid indices
        if start < 0 or start >= end:
            return ""

        # Extract substring (Python slicing handles end > length)
        return string_val[start:end]


class PrintcOperation(Operation):
    """PRINTC - Print single character from ASCII code."""

    @property
    def name(self) -> str:
        return "PRINTC"

    def execute(self, args: list, evaluator) -> str:
        """Print character from ASCII code.

        Args:
            args: [char_code] - ASCII character code
            evaluator: Evaluator instance for recursive evaluation and output

        Returns:
            The character printed, or empty string if invalid
        """
        if not args:
            return ""

        char_code = evaluator.evaluate(args[0])

        # Validate character code
        if not isinstance(char_code, int):
            return ""

        # Limit to standard ASCII/extended ASCII range (0-255)
        # ZIL games typically use this range
        if char_code < 0 or char_code > 255:
            return ""

        try:
            # Convert ASCII code to character
            char = chr(char_code)

            # Write to output buffer
            evaluator.output.write(char)

            return char
        except (ValueError, OverflowError):
            # Invalid character code
            return ""
