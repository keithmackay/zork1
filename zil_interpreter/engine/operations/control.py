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


class ReturnOperation(Operation):
    """RETURN - Return arbitrary value from routine."""

    @property
    def name(self) -> str:
        return "RETURN"

    def execute(self, args: list, evaluator) -> None:
        """Return arbitrary value from routine."""
        from zil_interpreter.engine.evaluator import ReturnValue

        if not args:
            raise ReturnValue(None)

        value = evaluator.evaluate(args[0])
        raise ReturnValue(value)


class RepeatOperation(Operation):
    """REPEAT - Loop construct."""

    @property
    def name(self) -> str:
        return "REPEAT"

    def execute(self, args: list, evaluator) -> Any:
        """Loop construct - executes body repeatedly.

        Note: In ZIL, REPEAT loops are typically broken by RETURN/RTRUE/RFALSE
        within COND statements. For now, we implement basic iteration semantics.
        A complete implementation would require more sophisticated control flow.
        """
        if not args:
            return None

        # First arg is loop specification (variables/conditions)
        loop_spec = args[0] if args else []
        body = args[1:] if len(args) > 1 else []

        # For basic implementation: execute body once
        # Full implementation would need break conditions
        result = None
        for expr in body:
            result = evaluator.evaluate(expr)

        return result


class MapfOperation(Operation):
    """MAPF - Map function over collection."""

    @property
    def name(self) -> str:
        return "MAPF"

    def execute(self, args: list, evaluator) -> list:
        """Map function over collection."""
        if len(args) < 2:
            return []

        func_arg = args[0]
        collection = evaluator.evaluate(args[1])

        if not isinstance(collection, list):
            return []

        results = []
        for item in collection:
            # Create a form that calls the function with the item
            from zil_interpreter.parser.ast_nodes import Atom, Form

            if isinstance(func_arg, Atom):
                call = Form(func_arg, [item])
            else:
                # If func_arg is already evaluated or complex, skip
                continue

            try:
                result = evaluator.evaluate(call)
                results.append(result)
            except Exception:
                # If evaluation fails, skip this item
                continue

        return results


class ProgOperation(Operation):
    """PROG - block scope with optional bindings.

    Usage: <PROG (bindings) body...>
    Executes body expressions in sequence, returns last value.
    """

    @property
    def name(self) -> str:
        return "PROG"

    def execute(self, args: list[Any], evaluator: Any) -> Any:
        if not args:
            return None

        # First arg is bindings (may be empty list)
        bindings = evaluator.evaluate(args[0]) if args else []
        body = args[1:] if len(args) > 1 else []

        # Execute body expressions
        result = None
        for expr in body:
            result = evaluator.evaluate(expr)

        return result
