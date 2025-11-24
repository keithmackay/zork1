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
