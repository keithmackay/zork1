"""Control flow operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation


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
