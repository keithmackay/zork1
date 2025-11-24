"""Comparison and object operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


class NextQuestionOperation(Operation):
    """NEXT? - Get next sibling object in tree."""

    @property
    def name(self) -> str:
        return "NEXT?"

    def execute(self, args: list, evaluator) -> Any:
        """Get next sibling object in tree."""
        if not args:
            return False

        # Get object name directly from Atom or evaluate
        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))

        # Get object
        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return False

        # Get parent's children to find next sibling
        parent = obj.parent
        if not parent or not hasattr(parent, 'children'):
            return False

        # Find this object in parent's children (children is a set, convert to list)
        children = list(parent.children)
        try:
            current_index = children.index(obj)
            # Return next sibling if exists
            if current_index + 1 < len(children):
                return children[current_index + 1]
            else:
                return False
        except (ValueError, IndexError):
            return False


class GetptOperation(Operation):
    """GETPT - Get property table entry (returns property reference or FALSE)."""

    @property
    def name(self) -> str:
        return "GETPT"

    def execute(self, args: list, evaluator) -> Any:
        """Get property table entry (returns property reference or FALSE)."""
        if len(args) < 2:
            return False

        # Get object name directly from Atom or evaluate
        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        # Get property name directly from Atom or evaluate
        prop_arg = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        # Get object
        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return False

        # Check if property exists - try both upper and as-is
        prop_name = prop_arg.upper()

        # Try exact match first, then uppercase
        if prop_arg in obj.properties:
            return (obj, prop_arg)
        elif prop_name in obj.properties:
            return (obj, prop_name)

        return False


class PtsizeOperation(Operation):
    """PTSIZE - Get property table size."""

    @property
    def name(self) -> str:
        return "PTSIZE"

    def execute(self, args: list, evaluator) -> int:
        """Get property table size."""
        if not args:
            return 0

        prop_ref = evaluator.evaluate(args[0])

        # If prop_ref is FALSE, return 0
        if prop_ref is False or prop_ref == 0:
            return 0

        # If prop_ref is a tuple (obj, prop_name) from GETPT
        if isinstance(prop_ref, tuple) and len(prop_ref) == 2:
            obj, prop_name = prop_ref
            value = obj.get_property(prop_name)

            # Return size based on value type
            if value is None:
                return 0
            elif isinstance(value, list):
                # Table: size is number of elements * 2 (16-bit words)
                return len(value) * 2
            elif isinstance(value, str):
                # String: size is length
                return len(value)
            elif isinstance(value, int):
                # Integer: size is 2 bytes (16-bit word)
                return 2
            else:
                # Default size
                return 2

        return 0
