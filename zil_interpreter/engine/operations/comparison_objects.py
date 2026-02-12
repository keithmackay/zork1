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

        # Get object - evaluate to handle GlobalRef/LocalRef
        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])

        # Get object
        obj = evaluator.world.get_object(obj_val)
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

    # Direction index to name mapping (from DIRECTIONS directive order)
    DIRECTION_NAMES = ['NORTH', 'EAST', 'WEST', 'SOUTH', 'NE', 'NW',
                       'SE', 'SW', 'UP', 'DOWN', 'IN', 'OUT', 'LAND']

    @property
    def name(self) -> str:
        return "GETPT"

    def execute(self, args: list, evaluator) -> Any:
        """Get property table entry (returns property reference or FALSE)."""
        if len(args) < 2:
            return False

        # Get object - evaluate to handle GlobalRef/LocalRef
        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        # Get property name - evaluate argument
        raw_prop = args[1].value if isinstance(args[1], Atom) else evaluator.evaluate(args[1])

        # If property is a numeric direction index, convert to direction name
        if isinstance(raw_prop, (int, float)):
            idx = int(raw_prop)
            if 0 <= idx < len(self.DIRECTION_NAMES):
                prop_arg = self.DIRECTION_NAMES[idx]
            else:
                return False
        else:
            prop_arg = str(raw_prop)

        # Get object
        obj = evaluator.world.get_object(obj_val)
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

    # Direction property names
    DIRECTIONS = {'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN',
                  'NE', 'NW', 'SE', 'SW', 'IN', 'OUT', 'LAND',
                  'IN'}

    def execute(self, args: list, evaluator) -> int:
        """Get property table size.

        For direction properties, returns exit type constants:
        UEXIT=1 (simple room), NEXIT=2 (no-exit message),
        FEXIT=3 (function exit), CEXIT=4 (conditional), DEXIT=5 (door).
        For non-direction properties, returns byte size.
        """
        if not args:
            return 0

        prop_ref = evaluator.evaluate(args[0])

        # If prop_ref is FALSE, return 0
        if prop_ref is False or prop_ref == 0 or prop_ref is None:
            return 0

        # If prop_ref is a tuple (obj, prop_name) from GETPT
        if isinstance(prop_ref, tuple) and len(prop_ref) == 2:
            obj, prop_name = prop_ref
            value = obj.get_property(prop_name)

            if value is None:
                return 0

            # Check if this is a direction property
            if prop_name.upper() in self.DIRECTIONS:
                return self._exit_type(value)

            # Non-direction property: return byte size
            if isinstance(value, str):
                return len(value)
            elif isinstance(value, list):
                return len(value) * 2
            elif isinstance(value, int):
                return 2
            else:
                return 2

        return 0

    def _exit_type(self, value) -> int:
        """Determine exit type from property value.

        ZIL exit types:
        UEXIT (1): Simple room reference - value is an uppercase room name
        NEXIT (2): No-exit message - value is a descriptive string
        FEXIT (3): Function exit - value is callable
        CEXIT (4): Conditional exit - value is a list with IF condition
        DEXIT (5): Door exit - value is a list with door object
        """
        import re
        if isinstance(value, str):
            # Room names are ALL UPPERCASE with optional hyphens/digits
            # e.g., "WEST-OF-HOUSE", "FOREST-1", "PATH", "KITCHEN"
            if re.match(r'^[A-Z][A-Z0-9\-]*$', value):
                return 1  # UEXIT - simple room reference
            return 2  # NEXIT - no-exit message
        elif isinstance(value, list):
            if len(value) >= 2:
                str_values = [str(v).upper() for v in value]
                if 'IF' in str_values:
                    return 4  # CEXIT - conditional
                if any(v.upper().endswith('BIT') for v in str_values if isinstance(v, str)):
                    return 5  # DEXIT - door
            return 3  # FEXIT - function
        elif callable(value):
            return 3  # FEXIT - function
        return 1  # Default UEXIT
