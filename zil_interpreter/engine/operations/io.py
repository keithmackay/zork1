"""I/O operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


def _printable(value: Any) -> str:
    """Convert a value to a printable string, handling GameObjects."""
    from zil_interpreter.world.game_object import GameObject
    if isinstance(value, GameObject):
        # Print the object's DESC property (short description)
        return value.description or value.name
    if value is None:
        return ""
    return str(value)


def _printable_desc(value: Any) -> str:
    """Print object's DESC property (used by TELL D indicator)."""
    from zil_interpreter.world.game_object import GameObject
    if isinstance(value, GameObject):
        desc = value.get_property("DESC")
        if desc:
            return str(desc)
        return value.description or value.name
    if value is None:
        return ""
    # If value is a string name, just return it (can't look up object here)
    return str(value)


class TellOperation(Operation):
    """TELL - Output text to player."""

    @property
    def name(self) -> str:
        return "TELL"

    def execute(self, args: list, evaluator) -> None:
        """Output strings and atoms to output buffer."""
        print_desc = False
        for arg in args:
            if isinstance(arg, Atom):
                atom_upper = arg.value.upper()
                if atom_upper in ("CR", "CRLF"):
                    evaluator.output.write("\n")
                    print_desc = False
                elif atom_upper == "D":
                    # D indicator: next arg is an object, print its DESC
                    print_desc = True
                    continue
                else:
                    # Variable lookup
                    value = evaluator.evaluate(arg)
                    if value is not None:
                        if print_desc:
                            evaluator.output.write(_printable_desc(value))
                        else:
                            evaluator.output.write(_printable(value))
                    print_desc = False
            else:
                value = evaluator.evaluate(arg)
                if value is not None:
                    if print_desc:
                        evaluator.output.write(_printable_desc(value))
                    else:
                        evaluator.output.write(_printable(value))
                print_desc = False


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

        value = evaluator.evaluate(args[0])
        if value is not None:
            evaluator.output.write(_printable(value))

        return True


class PrintiOperation(Operation):
    """PRINTI - Print immediate string."""

    @property
    def name(self) -> str:
        return "PRINTI"

    def execute(self, args: list, evaluator) -> bool:
        """Print immediate string."""
        if not args:
            return True

        value = evaluator.evaluate(args[0])
        if value is not None:
            evaluator.output.write(_printable(value))

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


class WordQuestionOp(Operation):
    """WORD? - check word type/property.

    Usage: <WORD? word type>

    Returns true if word has specified type.
    In the simplified implementation, checks if the word is in a predefined
    set of verb words when type is "VERB".
    """

    @property
    def name(self) -> str:
        return "WORD?"

    def execute(self, args: list, evaluator) -> bool:
        """Check if word has specified type."""
        if len(args) < 2:
            return False

        word = evaluator.evaluate(args[0])
        word_type = evaluator.evaluate(args[1])

        # Simplified: check if word matches common types
        # In full implementation, would check vocabulary table
        verb_words = {"TAKE", "GET", "DROP", "LOOK", "OPEN", "CLOSE", "GO"}

        if word_type == "VERB":
            return str(word).upper() in verb_words

        return False
