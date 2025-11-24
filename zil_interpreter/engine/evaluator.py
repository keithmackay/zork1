"""ZIL expression evaluator."""

from typing import Any, Optional
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number, ASTNode
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import ObjectFlag
from zil_interpreter.runtime.output_buffer import OutputBuffer


class Evaluator:
    """Evaluates ZIL expressions in the context of world state."""

    # Map ZIL flag names to ObjectFlag enum
    FLAG_MAP = {
        "OPENBIT": ObjectFlag.OPEN,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "TAKEABLEBIT": ObjectFlag.TAKEABLE,
        "LOCKEDBIT": ObjectFlag.LOCKED,
        "NDESCBIT": ObjectFlag.NDESCBIT,
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "ONBIT": ObjectFlag.ONBIT,
    }

    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()

    def evaluate(self, expr: Any) -> Any:
        """Evaluate a ZIL expression.

        Args:
            expr: Expression to evaluate

        Returns:
            Result of evaluation
        """
        if isinstance(expr, Number):
            return expr.value

        elif isinstance(expr, String):
            return expr.value

        elif isinstance(expr, Atom):
            # Variable lookup
            return self.world.get_global(expr.value)

        elif isinstance(expr, Form):
            return self._evaluate_form(expr)

        elif isinstance(expr, list):
            # Evaluate each element
            return [self.evaluate(item) for item in expr]

        else:
            return expr

    def _evaluate_form(self, form: Form) -> Any:
        """Evaluate a form (function call).

        Args:
            form: Form to evaluate

        Returns:
            Result of form evaluation
        """
        op = form.operator.value.upper()

        if op == "EQUAL?":
            return self._eval_equal(form.args)

        elif op == "FSET?":
            return self._eval_fset_check(form.args)

        elif op == "VERB?":
            return self._eval_verb_check(form.args)

        elif op == "COND":
            return self._eval_cond(form.args)

        elif op == "TELL":
            return self._eval_tell(form.args)

        elif op == "MOVE":
            return self._eval_move(form.args)

        else:
            raise NotImplementedError(f"Form not implemented: {op}")

    def _eval_equal(self, args: list) -> bool:
        """Evaluate EQUAL? comparison."""
        if len(args) < 2:
            return False
        val1 = self.evaluate(args[0])
        val2 = self.evaluate(args[1])
        return val1 == val2

    def _eval_fset_check(self, args: list) -> bool:
        """Evaluate FSET? flag check."""
        if len(args) < 2:
            return False

        # Get object name - if it's an Atom, use its value directly (not as variable lookup)
        obj_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        # Get flag name - same pattern
        flag_name = args[1].value if isinstance(args[1], Atom) else str(self.evaluate(args[1]))

        obj = self.world.get_object(obj_name)
        if not obj:
            return False

        flag = self.FLAG_MAP.get(flag_name.upper())
        if not flag:
            return False

        return obj.has_flag(flag)

    def _eval_verb_check(self, args: list) -> bool:
        """Evaluate VERB? check."""
        if not args:
            return False

        verb_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        current_verb = self.world.get_global("PRSA")

        return current_verb == verb_name.upper()

    def _eval_cond(self, args: list) -> Any:
        """Evaluate COND conditional.

        Args:
            args: List of [condition, result] pairs

        Returns:
            Result of first true condition
        """
        for clause in args:
            if isinstance(clause, list) and len(clause) >= 2:
                condition = clause[0]
                result_expr = clause[1]

                if self.evaluate(condition):
                    return self.evaluate(result_expr)

        return None

    def _eval_tell(self, args: list) -> None:
        """Evaluate TELL form - output text."""
        for arg in args:
            if isinstance(arg, Atom):
                if arg.value.upper() in ("CR", "CRLF"):
                    self.output.write("\n")
                else:
                    # Variable lookup
                    value = self.evaluate(arg)
                    if value is not None:
                        self.output.write(str(value))
            else:
                value = self.evaluate(arg)
                if value is not None:
                    self.output.write(str(value))

    def _eval_move(self, args: list) -> None:
        """Evaluate MOVE form - move object to new location."""
        if len(args) < 2:
            return

        # Get object name directly from atoms (don't evaluate as variables)
        obj_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        dest_name = args[1].value if isinstance(args[1], Atom) else str(self.evaluate(args[1]))

        obj = self.world.get_object(obj_name)
        dest = self.world.get_object(dest_name)

        if obj and dest:
            obj.move_to(dest)
