from typing import Any
from zil_interpreter.engine.operations.base import Operation


class AndOperation(Operation):
    """AND - Short-circuit logical AND.

    Returns the first false value encountered, or the last value if all are true.
    With no arguments, returns False.
    """

    @property
    def name(self) -> str:
        return "AND"

    def execute(self, args: list, evaluator) -> Any:
        """Returns first false value or last value."""
        if not args:
            return False

        result = None
        for arg in args:
            result = evaluator.evaluate(arg)
            if not result:
                return result
        return result


class OrOperation(Operation):
    """OR - Short-circuit logical OR.

    Returns the first true value encountered, or the last value if all are false.
    With no arguments, returns False.
    """

    @property
    def name(self) -> str:
        return "OR"

    def execute(self, args: list, evaluator) -> Any:
        """Returns first true value or last value."""
        if not args:
            return False

        result = None
        for arg in args:
            result = evaluator.evaluate(arg)
            if result:
                return result
        return result


class NotOperation(Operation):
    """NOT - Logical negation.

    Returns the logical inverse of the argument.
    With no arguments, returns True.
    """

    @property
    def name(self) -> str:
        return "NOT"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return True
        return not evaluator.evaluate(args[0])
