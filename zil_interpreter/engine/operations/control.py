"""Control flow operations for ZIL."""

from typing import Any, TYPE_CHECKING
from zil_interpreter.engine.operations.base import Operation

if TYPE_CHECKING:
    from zil_interpreter.engine.evaluator import ReturnValue


class CondOperation(Operation):
    """COND - Conditional branching."""

    @property
    def name(self) -> str:
        return "COND"

    def execute(self, args: list, evaluator) -> Any:
        """Evaluate clauses until one succeeds."""
        for clause in args:
            if isinstance(clause, list) and len(clause) >= 2:
                condition = clause[0]
                result_expr = clause[1]

                if evaluator.evaluate(condition):
                    return evaluator.evaluate(result_expr)

        return None


class RtrueOperation(Operation):
    """RTRUE - Return true from routine."""

    @property
    def name(self) -> str:
        return "RTRUE"

    def execute(self, args: list, evaluator) -> None:
        # Import here to avoid circular dependency
        from zil_interpreter.engine.evaluator import ReturnValue
        raise ReturnValue(True)


class RfalseOperation(Operation):
    """RFALSE - Return false from routine."""

    @property
    def name(self) -> str:
        return "RFALSE"

    def execute(self, args: list, evaluator) -> None:
        # Import here to avoid circular dependency
        from zil_interpreter.engine.evaluator import ReturnValue
        raise ReturnValue(False)
