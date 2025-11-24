"""ZIL expression evaluator."""

from typing import Any, Optional
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number, ASTNode
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import ObjectFlag
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.operations import create_default_registry


class ReturnValue(Exception):
    """Exception to implement early return from routines."""
    def __init__(self, value):
        self.value = value


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
        self.registry = create_default_registry()

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
            atom_value = expr.value.upper()

            # Check for local variable reference (.VAR syntax)
            if atom_value.startswith('.'):
                var_name = atom_value[1:]  # Remove leading dot
                if hasattr(self, 'local_scope') and var_name in self.local_scope:
                    return self.local_scope[var_name]
                return None

            # Global variable lookup
            return self.world.get_global(atom_value)

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

        # Check registry first
        operation = self.registry.get(op)
        if operation:
            return operation.execute(form.args, self)

        if op == "FSET?":
            return self._eval_fset_check(form.args)

        elif op == "VERB?":
            return self._eval_verb_check(form.args)

        elif op == "COND":
            return self._eval_cond(form.args)

        elif op == "TELL":
            return self._eval_tell(form.args)

        elif op == "MOVE":
            return self._eval_move(form.args)

        elif op == "FSET":
            return self._eval_fset(form.args)

        elif op == "FCLEAR":
            return self._eval_fclear(form.args)

        elif op == "GETP":
            return self._eval_getp(form.args)

        elif op == "PUTP":
            return self._eval_putp(form.args)

        elif op == "IN?":
            return self._eval_in(form.args)

        elif op == "FIRST?":
            return self._eval_first(form.args)

        elif op == "+":
            return self._eval_add(form.args)

        elif op == "SET":
            return self._eval_set(form.args)

        elif op == "SETG":
            return self._eval_setg(form.args)

        elif op == "RTRUE":
            raise ReturnValue(True)

        elif op == "RFALSE":
            raise ReturnValue(False)

        else:
            # Check if it's a routine call
            if hasattr(self, 'routine_executor'):
                executor = self.routine_executor
                if op in executor.routines:
                    # Evaluate arguments
                    args = [self.evaluate(arg) for arg in form.args]
                    return executor.call_routine(op, args)

            raise NotImplementedError(f"Form not implemented: {op}")

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

    def _eval_fset(self, args: list) -> None:
        """Evaluate FSET form - set object flag."""
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        flag_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

        obj = self.world.get_object(obj_name)
        if not obj:
            return

        flag = self.FLAG_MAP.get(flag_name.upper())
        if flag:
            obj.set_flag(flag)

    def _eval_fclear(self, args: list) -> None:
        """Evaluate FCLEAR form - clear object flag."""
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        flag_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

        obj = self.world.get_object(obj_name)
        if not obj:
            return

        flag = self.FLAG_MAP.get(flag_name.upper())
        if flag:
            obj.clear_flag(flag)

    def _eval_getp(self, args: list) -> Any:
        """Evaluate GETP form - get object property."""
        if len(args) < 2:
            return None

        obj_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        prop_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

        obj = self.world.get_object(obj_name)
        if not obj:
            return None

        return obj.get_property(prop_name.upper())

    def _eval_putp(self, args: list) -> None:
        """Evaluate PUTP form - set object property."""
        if len(args) < 3:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        prop_name = args[1].value if isinstance(args[1], Atom) else str(args[1])
        value = self.evaluate(args[2])

        obj = self.world.get_object(obj_name)
        if obj:
            obj.set_property(prop_name.upper(), value)

    def _eval_in(self, args: list) -> bool:
        """Evaluate IN? form - check if object is in container."""
        if len(args) < 2:
            return False

        obj_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        container_name = args[1].value if isinstance(args[1], Atom) else str(self.evaluate(args[1]))

        obj = self.world.get_object(obj_name)
        container = self.world.get_object(container_name)

        if not obj or not container:
            return False

        return obj.parent == container

    def _eval_first(self, args: list) -> Optional[str]:
        """Evaluate FIRST? form - get first child of container."""
        if not args:
            return None

        container_name = args[0].value if isinstance(args[0], Atom) else str(self.evaluate(args[0]))
        container = self.world.get_object(container_name)

        if not container or not container.children:
            return None

        # Return first child's name
        return next(iter(container.children)).name

    def _eval_add(self, args: list) -> Any:
        """Evaluate + (addition)."""
        result = 0
        for arg in args:
            value = self.evaluate(arg)
            if isinstance(value, (int, float)):
                result += value
        return result

    def _eval_set(self, args: list) -> Any:
        """Evaluate SET form - set local variable."""
        if len(args) < 2:
            return None

        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        value = self.evaluate(args[1])

        # Set in local scope if it exists
        if hasattr(self, 'local_scope'):
            self.local_scope[var_name.upper()] = value
        else:
            # Fallback to global if no local scope
            self.world.set_global(var_name.upper(), value)

        return value

    def _eval_setg(self, args: list) -> Any:
        """Evaluate SETG form - set global variable."""
        if len(args) < 2:
            return None

        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        value = self.evaluate(args[1])

        self.world.set_global(var_name.upper(), value)
        return value
