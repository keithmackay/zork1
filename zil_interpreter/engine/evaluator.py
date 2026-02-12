"""ZIL expression evaluator."""

from typing import Any, Optional
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number, ASTNode, GlobalRef, LocalRef, PercentEval
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.operations import create_default_registry


class ReturnValue(Exception):
    """Exception to implement early return from routines."""
    def __init__(self, value):
        self.value = value


class Evaluator:
    """Evaluates ZIL expressions in the context of world state."""

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

        elif isinstance(expr, GlobalRef):
            # Global variable reference (,VAR)
            # First check globals, then fall back to object lookup
            name_upper = expr.name.upper()
            value = self.world.get_global(name_upper)
            if value is not None:
                return value
            # In ZIL, objects are also accessible via ,OBJNAME
            obj = self.world.get_object(name_upper)
            if obj is not None:
                return obj
            return None

        elif isinstance(expr, LocalRef):
            # Local variable reference (.VAR)
            var_name = expr.name.upper()
            if hasattr(self, 'local_scope') and var_name in self.local_scope:
                return self.local_scope[var_name]
            return None

        elif isinstance(expr, PercentEval):
            # Compile-time evaluation - evaluate the inner form, then if the
            # result is an AST node (e.g. from a quoted form), evaluate it
            # again. This simulates compile-time macro expansion where the
            # result is inserted as code to be run at runtime.
            result = self.evaluate(expr.form)
            if isinstance(result, (Form, PercentEval)):
                return self.evaluate(result)
            return result

        elif isinstance(expr, Atom):
            atom_value = expr.value.upper()

            # Check for local variable reference (.VAR syntax - legacy)
            if atom_value.startswith('.'):
                var_name = atom_value[1:]  # Remove leading dot
                if hasattr(self, 'local_scope') and var_name in self.local_scope:
                    return self.local_scope[var_name]
                return None

            # Handle special true/false atoms
            if atom_value in ('T', 'ELSE', 'TRUE'):
                return True
            if atom_value in ('FALSE', '<>'):
                return False

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
        # Handle operator - may be Atom, GlobalRef, LocalRef, or Form
        if isinstance(form.operator, Atom):
            op = form.operator.value.upper()
        elif isinstance(form.operator, (GlobalRef, LocalRef)):
            # Evaluate to get the routine name
            val = self.evaluate(form.operator)
            if isinstance(val, str):
                op = val.upper()
            else:
                op = str(val).upper() if val else ""
        elif isinstance(form.operator, Form):
            # Nested form evaluation (e.g., <<GETP .OBJ ACTION> ...>)
            val = self.evaluate(form.operator)
            if isinstance(val, str):
                op = val.upper()
            else:
                op = str(val).upper() if val else ""
        else:
            op = str(form.operator).upper()

        # Check registry first
        operation = self.registry.get(op)
        if operation:
            return operation.execute(form.args, self)

        # Check if it's a routine call
        if hasattr(self, 'routine_executor'):
            executor = self.routine_executor
            if op in executor.routines:
                # Evaluate arguments
                args = [self.evaluate(arg) for arg in form.args]
                return executor.call_routine(op, args)

        # Graceful fallback for unimplemented operations
        # Return None instead of crashing - allows game to continue
        return None
