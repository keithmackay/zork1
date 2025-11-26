"""I/O operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


class TellOperation(Operation):
    """TELL - Output text to player."""

    @property
    def name(self) -> str:
        return "TELL"

    def execute(self, args: list, evaluator) -> None:
        """Output strings and atoms to output buffer."""
        for arg in args:
            if isinstance(arg, Atom):
                if arg.value.upper() in ("CR", "CRLF"):
                    evaluator.output.write("\n")
                else:
                    # Variable lookup
                    value = evaluator.evaluate(arg)
                    if value is not None:
                        evaluator.output.write(str(value))
            else:
                value = evaluator.evaluate(arg)
                if value is not None:
                    evaluator.output.write(str(value))


class PrintnOperation(Operation):
    """PRINTN - Print number.

    Usage: <PRINTN number>

    Prints a numeric value to output buffer.
    Always returns TRUE.

    Example: <PRINTN 42> ; prints "42"
    """

    @property
    def name(self) -> str:
        return "PRINTN"

    def execute(self, args: list, evaluator) -> bool:
        """Print number to output buffer."""
        if not args:
            return True

        value = evaluator.evaluate(args[0])

        # Convert to number if possible
        if isinstance(value, (int, float)):
            evaluator.output.write(str(int(value)))
        elif isinstance(value, str):
            # Try to parse as number
            try:
                num = int(value)
                evaluator.output.write(str(num))
            except (ValueError, TypeError):
                # Not a valid number, print as-is
                evaluator.output.write(value)
        else:
            # Print whatever we got
            evaluator.output.write(str(value))

        return True


class PrintOperation(Operation):
    """PRINT - Print global string variable.

    Usage: <PRINT variable>

    Prints the value of a global variable (typically a string).
    Always returns TRUE.

    Example: <PRINT ,MESSAGE> ; prints value of MESSAGE global
    """

    @property
    def name(self) -> str:
        return "PRINT"

    def execute(self, args: list, evaluator) -> bool:
        """Print global variable value."""
        if not args:
            return True

        # Evaluate the argument to get the value
        value = evaluator.evaluate(args[0])

        if value is not None:
            evaluator.output.write(str(value))

        return True


class PrintiOperation(Operation):
    """PRINTI - Print immediate string.

    Usage: <PRINTI "text">

    Prints an immediate string literal to output buffer.
    Similar to PRINT but for string literals rather than variables.
    Always returns TRUE.

    Example: <PRINTI "Hello, world!"> ; prints "Hello, world!"
    """

    @property
    def name(self) -> str:
        return "PRINTI"

    def execute(self, args: list, evaluator) -> bool:
        """Print immediate string."""
        if not args:
            return True

        # Evaluate the argument (typically a string literal)
        value = evaluator.evaluate(args[0])

        if value is not None:
            evaluator.output.write(str(value))

        return True


class YesQuestionOp(Operation):
    """YES? - prompt for Y/N answer.

    Usage: <YES?>

    Prompts user and returns true for Y, false for N.
    In non-interactive mode, defaults to True.
    """

    @property
    def name(self) -> str:
        return "YES?"

    def execute(self, args: list, evaluator) -> bool:
        """Prompt for yes/no and return boolean."""
        # In a real implementation, this would read input
        # For now, check if there's an input method on evaluator
        if hasattr(evaluator, 'get_input'):
            response = evaluator.get_input()
            return response.lower().startswith('y')

        # Default: prompt via output and return True
        evaluator.output.write("? ")
        return True  # Default to yes for non-interactive


class ReadOp(Operation):
    """READ - read player input.

    Usage: <READ buffer lexv>

    Reads input from evaluator.input_buffer if available.
    Returns the input string or empty string if none available.
    """

    @property
    def name(self) -> str:
        return "READ"

    def execute(self, args: list, evaluator) -> str:
        """Read input from evaluator's input buffer."""
        # Get input from evaluator if available
        if hasattr(evaluator, 'input_buffer'):
            return evaluator.input_buffer
        return ""


class LexOp(Operation):
    """LEX - tokenize input string.

    Usage: <LEX input-buffer lexv-table>

    Tokenizes input string into words by splitting on whitespace.
    Returns a list of words.
    """

    @property
    def name(self) -> str:
        return "LEX"

    def execute(self, args: list, evaluator) -> list:
        """Tokenize input string into words."""
        if not args:
            return []

        input_str = evaluator.evaluate(args[0])
        if isinstance(input_str, str):
            return input_str.split()
        return []
