"""Game logic operations: META-LOC, LIT?, ACCESSIBLE?."""
from typing import Any, List
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.world.game_object import GameObject, ObjectFlag


def _obj_name(val: Any) -> str:
    """Extract object name from a value that may be a string or GameObject."""
    if isinstance(val, GameObject):
        return val.name
    if isinstance(val, str):
        return val
    return str(val) if val is not None else ""


class MetaLocOp(Operation):
    """META-LOC - find ultimate container (room).

    Usage: <META-LOC object>

    Traverses the parent chain until finding an object with ROOMBIT flag.
    Returns the room name, or None if no room found.

    Example: <META-LOC ,LAMP> ; returns ,LIVING-ROOM if lamp is in room
    """

    # Map ZIL flag names to ObjectFlag enum
    FLAG_MAP = {
        "ROOMBIT": ObjectFlag.SURFACE,  # Using SURFACE as ROOMBIT
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "OPENBIT": ObjectFlag.OPEN,
    }

    @property
    def name(self) -> str:
        return "META-LOC"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("META-LOC requires object")
        obj_name = evaluator.evaluate(args[0])

        # Traverse parent chain until we find a room
        current_obj = evaluator.world.get_object(obj_name)
        if not current_obj:
            return None

        visited = set()
        while current_obj and current_obj.name not in visited:
            visited.add(current_obj.name)
            # Check if this is a room (has ROOMBIT/SURFACE flag)
            if current_obj.has_flag(self.FLAG_MAP["ROOMBIT"]):
                return current_obj.name
            # Move to parent
            current_obj = current_obj.parent

        return None


class LitOp(Operation):
    """LIT? - check if location has light.

    Usage: <LIT? room>

    Returns true if the room has the LIGHTBIT flag set.
    Used to determine if player can see in a location.

    Example: <LIT? ,HERE>
    """

    # Map ZIL flag names to ObjectFlag enum
    FLAG_MAP = {
        "ROOMBIT": ObjectFlag.SURFACE,  # Using SURFACE as ROOMBIT
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "OPENBIT": ObjectFlag.OPEN,
    }

    @property
    def name(self) -> str:
        return "LIT?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("LIT? requires room")
        room_name = evaluator.evaluate(args[0])
        try:
            room = evaluator.world.get_object(room_name)
            if not room:
                return False
            return room.has_flag(self.FLAG_MAP["LIGHTBIT"])
        except (KeyError, AttributeError):
            return False


class AccessibleOp(Operation):
    """ACCESSIBLE? - check if object can be reached.

    Usage: <ACCESSIBLE? object>

    An object is accessible if:
    - It's directly in the current room (HERE)
    - It's held by the player (PLAYER)
    - It's in an open container that's in the room or held

    Returns true if object can be interacted with.

    Example: <ACCESSIBLE? ,LAMP>
    """

    # Map ZIL flag names to ObjectFlag enum
    FLAG_MAP = {
        "ROOMBIT": ObjectFlag.SURFACE,  # Using SURFACE as ROOMBIT
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "OPENBIT": ObjectFlag.OPEN,
    }

    @property
    def name(self) -> str:
        return "ACCESSIBLE?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("ACCESSIBLE? requires object")
        obj_name = evaluator.evaluate(args[0])

        try:
            obj = evaluator.world.get_object(obj_name)
            if not obj:
                return False

            # Get HERE and PLAYER names (may be strings or GameObjects)
            here_name = _obj_name(evaluator.world.get_global("HERE"))
            player_name = _obj_name(evaluator.world.get_global("PLAYER"))

            # Directly in room or held by player
            if obj.parent:
                if obj.parent.name == here_name or obj.parent.name == player_name:
                    return True

            # Check if in open container chain leading to room or player
            parent_obj = obj.parent
            visited = set()
            while parent_obj and parent_obj.name not in visited:
                visited.add(parent_obj.name)

                # Reached room or player - object is accessible
                if parent_obj.name == here_name or parent_obj.name == player_name:
                    return True

                # If parent is a closed container, not accessible
                if parent_obj.has_flag(self.FLAG_MAP["CONTAINERBIT"]) and not parent_obj.has_flag(self.FLAG_MAP["OPENBIT"]):
                    return False

                parent_obj = parent_obj.parent

            return False
        except (KeyError, AttributeError):
            return False


class JigsUpOp(Operation):
    """JIGS-UP - game over with death message.

    Usage: <JIGS-UP "message">
    Prints death message, sets DEAD flag, ends game.
    """

    @property
    def name(self) -> str:
        return "JIGS-UP"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        message = evaluator.evaluate(args[0]) if args else "You have died."

        # Print death message
        evaluator.output.write(f"\n{message}\n")

        # Set dead flag
        evaluator.world.set_global("DEAD", True)

        # For now, just return - game engine should check DEAD flag
        return True
