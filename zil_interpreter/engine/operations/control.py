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
        """Evaluate clauses until one succeeds.

        In ZIL, when a clause's condition is true, ALL expressions
        in that clause are evaluated in sequence, and the value of
        the LAST expression is returned.
        """
        for clause in args:
            if isinstance(clause, list) and len(clause) >= 1:
                condition = clause[0]

                if evaluator.evaluate(condition):
                    # Evaluate ALL remaining expressions in the clause
                    result = None
                    for expr in clause[1:]:
                        result = evaluator.evaluate(expr)
                    return result

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


class RfatalOperation(Operation):
    """RFATAL - Return false after a fatal error (used after error messages)."""

    @property
    def name(self) -> str:
        return "RFATAL"

    def execute(self, args: list, evaluator) -> None:
        # Import here to avoid circular dependency
        from zil_interpreter.engine.evaluator import ReturnValue
        # RFATAL is like RFALSE but indicates a fatal error occurred
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
        """Loop construct - executes body repeatedly until RETURN/RTRUE/RFALSE.

        In ZIL, REPEAT takes an optional binding list as first arg,
        then body expressions. It loops forever until broken by
        RETURN, RTRUE, or RFALSE.
        """
        from zil_interpreter.engine.evaluator import ReturnValue

        if not args:
            return None

        # First arg is bindings list (may be empty)
        bindings = args[0] if args else []
        body = args[1:] if len(args) > 1 else []

        # Set up bindings if any
        if isinstance(bindings, list):
            for binding in bindings:
                if isinstance(binding, list) and len(binding) >= 2:
                    from zil_interpreter.parser.ast_nodes import Atom
                    var_name = binding[0].value if isinstance(binding[0], Atom) else str(binding[0])
                    value = evaluator.evaluate(binding[1])
                    if hasattr(evaluator, 'local_scope'):
                        evaluator.local_scope[var_name.upper()] = value
                    else:
                        evaluator.world.set_global(var_name.upper(), value)

        # Execute body repeatedly until RETURN breaks out
        from zil_interpreter.engine.operations.advanced import AgainException
        max_iterations = 10000  # Safety limit
        result = None
        for _ in range(max_iterations):
            try:
                for expr in body:
                    result = evaluator.evaluate(expr)
            except ReturnValue:
                raise  # Let ReturnValue propagate up
            except AgainException:
                continue  # Restart loop
            # If no RETURN was hit, loop again

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

    def execute(self, args: list, evaluator: Any) -> Any:
        if not args:
            return None

        # First arg is bindings list
        bindings = args[0] if args else []
        body = args[1:] if len(args) > 1 else []

        # Set up bindings if any
        if isinstance(bindings, list):
            for binding in bindings:
                if isinstance(binding, list) and len(binding) >= 2:
                    from zil_interpreter.parser.ast_nodes import Atom
                    var_name = binding[0].value if isinstance(binding[0], Atom) else str(binding[0])
                    value = evaluator.evaluate(binding[1])
                    if hasattr(evaluator, 'local_scope'):
                        evaluator.local_scope[var_name.upper()] = value
                    else:
                        evaluator.world.set_global(var_name.upper(), value)
                elif isinstance(binding, (Atom,)):
                    from zil_interpreter.parser.ast_nodes import Atom
                    var_name = binding.value
                    if hasattr(evaluator, 'local_scope'):
                        evaluator.local_scope[var_name.upper()] = None
                    else:
                        evaluator.world.set_global(var_name.upper(), None)

        # Execute body expressions
        result = None
        for expr in body:
            result = evaluator.evaluate(expr)

        return result


class DoOperation(Operation):
    """DO - counted iteration loop.

    Usage: <DO (var start end) body...>
    Iterates var from start to end (inclusive), executing body each time.
    """

    @property
    def name(self) -> str:
        return "DO"

    def execute(self, args: list[Any], evaluator: Any) -> Any:
        if len(args) < 3:
            return None

        var_name = args[0]
        start = evaluator.evaluate(args[1])
        end = evaluator.evaluate(args[2])
        body = args[3:] if len(args) > 3 else []

        # Iterate from start to end inclusive
        for i in range(start, end + 1):
            # Set loop variable
            evaluator.world.set_global(str(var_name), i)
            # Execute body
            for expr in body:
                evaluator.evaluate(expr)

        return None


class QuitOperation(Operation):
    """QUIT - exit the game.

    Usage: <QUIT>
    Sets QUIT flag to signal game loop to exit.
    """

    @property
    def name(self) -> str:
        return "QUIT"

    def execute(self, args: list[Any], evaluator: Any) -> Any:
        evaluator.world.set_global("QUIT", True)
        return True
