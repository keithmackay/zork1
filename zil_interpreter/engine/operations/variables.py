"""Variable operations for ZIL interpreter."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


class SetOperation(Operation):
    """SET - Set local variable."""

    @property
    def name(self) -> str:
        return "SET"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None

        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        value = evaluator.evaluate(args[1])

        # Set in local scope if it exists
        if hasattr(evaluator, 'local_scope'):
            evaluator.local_scope[var_name.upper()] = value
        else:
            # Fallback to global if no local scope
            evaluator.world.set_global(var_name.upper(), value)

        return value


class SetgOperation(Operation):
    """SETG - Set global variable."""

    @property
    def name(self) -> str:
        return "SETG"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None

        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        value = evaluator.evaluate(args[1])

        evaluator.world.set_global(var_name.upper(), value)
        return value
