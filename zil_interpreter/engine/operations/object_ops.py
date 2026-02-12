"""Object manipulation operations for ZIL interpreter."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom, GlobalRef, LocalRef
from zil_interpreter.world.game_object import ObjectFlag


class MoveOperation(Operation):
    """MOVE - Move object to new location."""

    @property
    def name(self) -> str:
        return "MOVE"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        dest_val = args[1].value if isinstance(args[1], Atom) else evaluator.evaluate(args[1])

        obj = evaluator.world.get_object(obj_val)
        dest = evaluator.world.get_object(dest_val)

        if obj and dest:
            obj.move_to(dest)


class FsetOperation(Operation):
    """FSET - Set flag on object."""

    @property
    def name(self) -> str:
        return "FSET"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_val = evaluator.evaluate(args[0]) if not isinstance(args[0], Atom) else args[0].value
        if isinstance(args[1], Atom):
            flag_name = args[1].value
        elif isinstance(args[1], GlobalRef):
            flag_name = args[1].name
        else:
            flag_name = str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_val)
        if not obj:
            return

        obj.set_flag(flag_name.upper())


class FclearOperation(Operation):
    """FCLEAR - Clear flag on object."""

    @property
    def name(self) -> str:
        return "FCLEAR"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_val = evaluator.evaluate(args[0]) if not isinstance(args[0], Atom) else args[0].value
        if isinstance(args[1], Atom):
            flag_name = args[1].value
        elif isinstance(args[1], GlobalRef):
            flag_name = args[1].name
        else:
            flag_name = str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_val)
        if not obj:
            return

        obj.clear_flag(flag_name.upper())


class GetpOperation(Operation):
    """GETP - Get property value from object."""

    @property
    def name(self) -> str:
        return "GETP"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])

        # Handle property name - could be Atom, GlobalRef (P?XXX), or string
        prop_arg = args[1]
        if isinstance(prop_arg, Atom):
            prop_name = prop_arg.value
        elif isinstance(prop_arg, GlobalRef):
            # In ZIL, ,P?ACTION means property slot "ACTION"
            # Extract property name from P?XXX format
            ref_name = prop_arg.name.upper()
            if ref_name.startswith("P?"):
                prop_name = ref_name[2:]  # Remove "P?" prefix
            else:
                prop_name = ref_name
        else:
            prop_name = str(evaluator.evaluate(prop_arg))

        obj = evaluator.world.get_object(obj_val)
        if not obj:
            return None

        return obj.get_property(prop_name.upper())


class PutpOperation(Operation):
    """PUTP - Set property value on object."""

    @property
    def name(self) -> str:
        return "PUTP"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 3:
            return

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        prop_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))
        value = evaluator.evaluate(args[2])

        obj = evaluator.world.get_object(obj_val)
        if obj:
            obj.set_property(prop_name.upper(), value)


class LocOperation(Operation):
    """LOC - Get object location/parent."""

    @property
    def name(self) -> str:
        return "LOC"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return None

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_val)

        if not obj:
            return None

        return obj.parent


class RemoveOperation(Operation):
    """REMOVE - Remove object from world (remove from parent)."""

    @property
    def name(self) -> str:
        return "REMOVE"

    def execute(self, args: list, evaluator) -> None:
        if not args:
            return

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_val)

        if not obj:
            return

        # Remove from parent by moving to None
        obj.move_to(None)


class HeldOperation(Operation):
    """HELD? - Check if player holds object."""

    @property
    def name(self) -> str:
        return "HELD?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False

        obj_val = args[0].value if isinstance(args[0], Atom) else evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_val)

        if not obj:
            return False

        # Get player object from global PLAYER variable
        player_val = evaluator.world.get_global("PLAYER")
        if not player_val:
            return False

        from zil_interpreter.world.game_object import GameObject
        if isinstance(player_val, GameObject):
            player = player_val
        else:
            player = evaluator.world.get_object(player_val)
        if not player:
            return False

        # Check if object's parent is the player
        return obj.parent == player


class MapContentsOperation(Operation):
    """MAP-CONTENTS - iterate over container's children.

    Usage: <MAP-CONTENTS (var container) body...>
    Sets var to each child of container and executes body.
    """

    @property
    def name(self) -> str:
        return "MAP-CONTENTS"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return None

        var_name = args[0]
        container_name = evaluator.evaluate(args[1])
        body = args[2:] if len(args) > 2 else []

        # Get container and its children
        container = evaluator.world.get_object(container_name)
        if not container:
            return None

        # Iterate over children
        for child in container.children:
            evaluator.world.set_global(str(var_name), child.name)
            for expr in body:
                evaluator.evaluate(expr)
