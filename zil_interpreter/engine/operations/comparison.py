"""Comparison operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom, GlobalRef
from zil_interpreter.world.game_object import ObjectFlag


class EqualOperation(Operation):
    """EQUAL? - Value equality check."""

    @property
    def name(self) -> str:
        return "EQUAL?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        # EQUAL? can take multiple comparison values
        from zil_interpreter.world.game_object import GameObject
        for arg in args[1:]:
            val2 = evaluator.evaluate(arg)
            if val1 == val2:
                return True
            # Handle GameObject comparison by name
            if isinstance(val1, GameObject) and isinstance(val2, str):
                if val1.name == val2.upper():
                    return True
            elif isinstance(val2, GameObject) and isinstance(val1, str):
                if val2.name == val1.upper():
                    return True
        return False


class FsetCheckOperation(Operation):
    """FSET? - Check if object has flag set."""

    @property
    def name(self) -> str:
        return "FSET?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False

        # Get object - evaluate to handle GlobalRef/LocalRef
        obj_val = evaluator.evaluate(args[0]) if not isinstance(args[0], Atom) else args[0].value
        # Get flag name - GlobalRef to a flag should use the name directly
        if isinstance(args[1], Atom):
            flag_name = args[1].value
        elif isinstance(args[1], GlobalRef):
            # Flag references like ,CONTBIT - use the name directly
            flag_name = args[1].name
        else:
            flag_name = str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_val)
        if not obj:
            return False

        return obj.has_flag(flag_name.upper())


class VerbCheckOperation(Operation):
    """VERB? - Check current verb in parser state."""

    @property
    def name(self) -> str:
        return "VERB?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False

        current_verb = evaluator.world.get_global("PRSA")
        if current_verb is None:
            return False

        # VERB? can take multiple verbs to check against
        for arg in args:
            verb_name = arg.value if isinstance(arg, Atom) else str(evaluator.evaluate(arg))
            verb_upper = verb_name.upper()
            if current_verb == verb_upper or current_verb == f"V-{verb_upper}":
                return True
        return False


class InCheckOperation(Operation):
    """IN? - Check if object is contained in another."""

    @property
    def name(self) -> str:
        return "IN?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        container_val = args[1].value if isinstance(args[1], Atom) else evaluator.evaluate(args[1])

        obj = evaluator.world.get_object(obj_val)
        container = evaluator.world.get_object(container_val)

        if not obj or not container:
            return False

        return obj.parent == container


class FirstCheckOperation(Operation):
    """FIRST? - Get first child of object."""

    @property
    def name(self) -> str:
        return "FIRST?"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return None

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_val)

        if not obj or not obj.children:
            return None

        # Return first child object
        return obj.children[0]


class LessThanOperation(Operation):
    """< (L?) - Less than comparison."""

    @property
    def name(self) -> str:
        return "<"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        if val1 is None:
            val1 = 0
        if val2 is None:
            val2 = 0
        return val1 < val2


class GreaterThanOperation(Operation):
    """> (G?) - Greater than comparison."""

    @property
    def name(self) -> str:
        return ">"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        if val1 is None:
            val1 = 0
        if val2 is None:
            val2 = 0
        return val1 > val2


class LessEqualOperation(Operation):
    """<= - Less than or equal comparison."""

    @property
    def name(self) -> str:
        return "<="

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        if val1 is None:
            val1 = 0
        if val2 is None:
            val2 = 0
        return val1 <= val2


class GreaterEqualOperation(Operation):
    """>= - Greater than or equal comparison."""

    @property
    def name(self) -> str:
        return ">="

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        if val1 is None:
            val1 = 0
        if val2 is None:
            val2 = 0
        return val1 >= val2


class ZeroCheckOperation(Operation):
    """ZERO? - Check if value is zero."""

    @property
    def name(self) -> str:
        return "ZERO?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return True
        val = evaluator.evaluate(args[0])
        return val == 0


class NumericEqualOperation(Operation):
    """== - Numeric equality comparison."""

    @property
    def name(self) -> str:
        return "=="

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False

        # Evaluate first argument as reference
        first_val = evaluator.evaluate(args[0])

        # Check if all remaining arguments equal the first
        for arg in args[1:]:
            val = evaluator.evaluate(arg)
            if val != first_val:
                return False

        return True


class AssignOrEqualOperation(Operation):
    """= - Assignment or equality depending on context.

    In ZIL, = can be used for:
    - Assignment: <SET var val>
    - Equality test: <= val1 val2>

    This implements the equality test semantics.
    """

    @property
    def name(self) -> str:
        return "="

    def execute(self, args: list, evaluator) -> bool:
        """Test equality between values."""
        if len(args) < 2:
            return False

        # Handle special =? compile-time macro
        first_arg = args[0]
        if isinstance(first_arg, Atom) and first_arg.value == "=?":
            # Skip the =? marker and compare remaining args
            if len(args) < 3:
                return False
            val1 = evaluator.evaluate(args[1])
            val2 = evaluator.evaluate(args[2])
        else:
            val1 = evaluator.evaluate(args[0])
            val2 = evaluator.evaluate(args[1])

        return val1 == val2


class DlessOperation(Operation):
    """DLESS? - Decrement global variable and test if result is less than value.

    Decrements a global variable by 1, then tests if the new value is less than
    the comparison value.
    Arguments: <DLESS? var-name test-value> → TRUE/FALSE

    Used in loops and counters (common in game logic).
    """

    @property
    def name(self) -> str:
        return "DLESS?"

    def execute(self, args: list, evaluator) -> bool:
        """Decrement and test less than.

        Args:
            args: Variable name and comparison value
            evaluator: Evaluator for argument evaluation

        Returns:
            True if decremented value < test value, False otherwise
        """
        if len(args) < 2:
            return False

        # Get variable name (might be Atom or string)
        var_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        test_value = evaluator.evaluate(args[1])

        # Get current value, decrement, and store back
        current_value = evaluator.world.get_global(var_name)
        if not isinstance(current_value, int):
            return False

        new_value = current_value - 1
        evaluator.world.set_global(var_name, new_value)

        # Test if new value < test value
        return new_value < test_value
