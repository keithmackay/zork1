"""Object manipulation operations for ZIL interpreter."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom
from zil_interpreter.world.game_object import ObjectFlag


class MoveOperation(Operation):
    """MOVE - Move object to new location."""

    @property
    def name(self) -> str:
        return "MOVE"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        dest_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        dest = evaluator.world.get_object(dest_name)

        if obj and dest:
            obj.move_to(dest)


class FsetOperation(Operation):
    """FSET - Set flag on object."""

    FLAG_MAP = {
        "OPENBIT": ObjectFlag.OPEN,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "TAKEABLEBIT": ObjectFlag.TAKEABLE,
        "LOCKEDBIT": ObjectFlag.LOCKED,
        "NDESCBIT": ObjectFlag.NDESCBIT,
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "ONBIT": ObjectFlag.ONBIT,
    }

    @property
    def name(self) -> str:
        return "FSET"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        flag_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return

        flag = self.FLAG_MAP.get(flag_name.upper())
        if flag:
            obj.set_flag(flag)


class FclearOperation(Operation):
    """FCLEAR - Clear flag on object."""

    FLAG_MAP = FsetOperation.FLAG_MAP

    @property
    def name(self) -> str:
        return "FCLEAR"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        flag_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return

        flag = self.FLAG_MAP.get(flag_name.upper())
        if flag:
            obj.clear_flag(flag)


class GetpOperation(Operation):
    """GETP - Get property value from object."""

    @property
    def name(self) -> str:
        return "GETP"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        prop_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

        obj = evaluator.world.get_object(obj_name)
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

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        prop_name = args[1].value if isinstance(args[1], Atom) else str(args[1])
        value = evaluator.evaluate(args[2])

        obj = evaluator.world.get_object(obj_name)
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

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        obj = evaluator.world.get_object(obj_name)

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

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        obj = evaluator.world.get_object(obj_name)

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

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        obj = evaluator.world.get_object(obj_name)

        if not obj:
            return False

        # Get player object from global PLAYER variable
        player_name = evaluator.world.get_global("PLAYER")
        if not player_name:
            return False

        player = evaluator.world.get_object(player_name)
        if not player:
            return False

        # Check if object's parent is the player
        return obj.parent == player
