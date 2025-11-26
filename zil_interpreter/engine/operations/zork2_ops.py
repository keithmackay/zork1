"""Zork II specific ZIL operations.

These operations are used in Zork II but not in Zork I:
- NEXTP: Get next property of an object
- FIXED-FONT-ON/OFF: Font control operations
- PUSH/RSTACK: Stack manipulation operations
"""
from typing import Any, List

from .base import Operation


class NextpOp(Operation):
    """NEXTP - Get next property of an object.

    <NEXTP object prop> returns the next property after prop.
    <NEXTP object 0> returns the first property.
    Returns 0 if there are no more properties.
    """

    @property
    def name(self) -> str:
        return "NEXTP"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            return 0

        obj_arg = evaluator.evaluate(args[0])
        prop_arg = evaluator.evaluate(args[1])

        # Get the object
        if hasattr(obj_arg, 'properties'):
            obj = obj_arg
        elif hasattr(evaluator, 'world') and hasattr(evaluator.world, 'get_object'):
            obj = evaluator.world.get_object(obj_arg)
        else:
            return 0

        if obj is None or not hasattr(obj, 'properties'):
            return 0

        prop_names = list(obj.properties.keys())
        if not prop_names:
            return 0

        # If prop_arg is 0 or falsy, return first property
        if not prop_arg:
            return prop_names[0] if prop_names else 0

        # Find the next property after prop_arg
        try:
            idx = prop_names.index(prop_arg)
            if idx + 1 < len(prop_names):
                return prop_names[idx + 1]
            return 0  # No more properties
        except ValueError:
            # Property not found, return 0
            return 0


class FixedFontOnOp(Operation):
    """FIXED-FONT-ON - Enable fixed-width font mode."""

    @property
    def name(self) -> str:
        return "FIXED-FONT-ON"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if hasattr(evaluator, 'world') and hasattr(evaluator.world, 'set_global'):
            evaluator.world.set_global("FIXED-FONT", True)
        return True


class FixedFontOffOp(Operation):
    """FIXED-FONT-OFF - Disable fixed-width font mode."""

    @property
    def name(self) -> str:
        return "FIXED-FONT-OFF"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if hasattr(evaluator, 'world') and hasattr(evaluator.world, 'set_global'):
            evaluator.world.set_global("FIXED-FONT", False)
        return True


class PushOp(Operation):
    """PUSH - Push a value onto the game stack.

    <PUSH value> pushes value onto the stack.
    Returns the pushed value.
    """

    @property
    def name(self) -> str:
        return "PUSH"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None

        value = evaluator.evaluate(args[0])

        # Ensure evaluator has a stack
        if not hasattr(evaluator, 'stack'):
            evaluator.stack = []

        evaluator.stack.append(value)
        return value


class RstackOp(Operation):
    """RSTACK - Pop and return value from the game stack.

    <RSTACK> pops the top value from the stack and returns it.
    Returns None if the stack is empty.
    """

    @property
    def name(self) -> str:
        return "RSTACK"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not hasattr(evaluator, 'stack') or not evaluator.stack:
            return None

        return evaluator.stack.pop()
