"""Missing ZIL operations needed by Zork I."""

import random
from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


class ProbOperation(Operation):
    """PROB - Random probability check.

    Usage: <PROB n>
    Returns true with probability n/100.
    """

    @property
    def name(self) -> str:
        return "PROB"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False
        chance = evaluator.evaluate(args[0])
        if not isinstance(chance, (int, float)):
            return False
        return random.randint(1, 100) <= chance


class ThisIsItOperation(Operation):
    """THIS-IS-IT - Set the pronoun reference (IT/HIM/HER).

    Usage: <THIS-IS-IT object>
    Sets the object that 'IT' refers to in subsequent commands.
    """

    @property
    def name(self) -> str:
        return "THIS-IS-IT"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return None
        obj = evaluator.evaluate(args[0])
        evaluator.world.set_global("P-IT-OBJECT", obj)
        return obj


class ThisItOperation(Operation):
    """THIS-IT? - Check if object is the current IT reference.

    Usage: <THIS-IT? object>
    Returns true if object is the current pronoun reference.
    """

    @property
    def name(self) -> str:
        return "THIS-IT?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False
        obj = evaluator.evaluate(args[0])
        it_obj = evaluator.world.get_global("P-IT-OBJECT")
        if it_obj is None:
            return False
        from zil_interpreter.world.game_object import GameObject
        if isinstance(obj, GameObject) and isinstance(it_obj, GameObject):
            return obj.name == it_obj.name
        return str(obj) == str(it_obj)


class GlobalInOperation(Operation):
    """GLOBAL-IN? - Check if object is accessible via global scope.

    Usage: <GLOBAL-IN? object room>
    Returns true if object is in the room's GLOBAL property list.
    """

    @property
    def name(self) -> str:
        return "GLOBAL-IN?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        obj = evaluator.evaluate(args[0])
        room = evaluator.evaluate(args[1])

        from zil_interpreter.world.game_object import GameObject
        obj_name = obj.name if isinstance(obj, GameObject) else str(obj).upper()
        room_obj = evaluator.world.get_object(room)
        if not room_obj:
            return False

        # Check room's GLOBAL property (list of global objects)
        global_list = room_obj.get_property("GLOBAL")
        if isinstance(global_list, list):
            for item in global_list:
                item_name = item.name if isinstance(item, GameObject) else str(item).upper()
                if item_name == obj_name:
                    return True

        # Also check GLOBAL-OBJECTS parent
        global_objects = evaluator.world.get_object("GLOBAL-OBJECTS")
        if global_objects:
            for child in global_objects.children:
                if child.name == obj_name:
                    return True

        return False


class WeightOperation(Operation):
    """WEIGHT - Get total weight of object and contents.

    Usage: <WEIGHT object>
    Returns the object's SIZE plus the weight of all contained objects.
    """

    @property
    def name(self) -> str:
        return "WEIGHT"

    def execute(self, args: list, evaluator) -> int:
        if not args:
            return 0
        obj = evaluator.evaluate(args[0])
        obj_ref = evaluator.world.get_object(obj)
        if not obj_ref:
            return 0

        total = obj_ref.get_property("SIZE", 0)
        if not isinstance(total, int):
            total = 0

        # Add weight of contents
        for child in obj_ref.children:
            total += self._weight_of(child)
        return total

    def _weight_of(self, obj) -> int:
        weight = obj.get_property("SIZE", 0)
        if not isinstance(weight, int):
            weight = 0
        for child in obj.children:
            weight += self._weight_of(child)
        return weight


class SeeInsideOperation(Operation):
    """SEE-INSIDE? - Check if player can see inside a container.

    Usage: <SEE-INSIDE? object>
    Returns true if object is open or transparent.
    """

    @property
    def name(self) -> str:
        return "SEE-INSIDE?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False
        obj = evaluator.evaluate(args[0])
        obj_ref = evaluator.world.get_object(obj)
        if not obj_ref:
            return False

        from zil_interpreter.world.game_object import ObjectFlag
        # Can see inside if open or transparent
        if obj_ref.has_flag(ObjectFlag.OPEN):
            return True
        # Check for TRANSBIT (transparent) - stored as property
        if obj_ref.get_property("TRANSBIT"):
            return True
        return False


class AssignedOperation(Operation):
    """ASSIGNED? - Check if local variable has been assigned.

    Usage: <ASSIGNED? var>
    Returns true if variable has a non-None value.
    """

    @property
    def name(self) -> str:
        return "ASSIGNED?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False
        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        var_name = var_name.upper()
        if hasattr(evaluator, 'local_scope') and var_name in evaluator.local_scope:
            return evaluator.local_scope[var_name] is not None
        return False


class GassignedOperation(Operation):
    """GASSIGNED? - Check if global variable has been assigned.

    Usage: <GASSIGNED? var>
    Returns true if global variable exists and is not None.
    """

    @property
    def name(self) -> str:
        return "GASSIGNED?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False
        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        val = evaluator.world.get_global(var_name.upper())
        return val is not None


class NumberCheckOperation(Operation):
    """NUMBER? - Check if value is a number.

    Usage: <NUMBER? value>
    Returns true if value is a number.
    """

    @property
    def name(self) -> str:
        return "NUMBER?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False
        val = evaluator.evaluate(args[0])
        return isinstance(val, (int, float))


class MinOperation(Operation):
    """MIN - Return minimum of two values.

    Usage: <MIN a b>
    """

    @property
    def name(self) -> str:
        return "MIN"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return evaluator.evaluate(args[0]) if args else 0
        a = evaluator.evaluate(args[0])
        b = evaluator.evaluate(args[1])
        return min(a, b)


class MaxOperation(Operation):
    """MAX - Return maximum of two values.

    Usage: <MAX a b>
    """

    @property
    def name(self) -> str:
        return "MAX"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return evaluator.evaluate(args[0]) if args else 0
        a = evaluator.evaluate(args[0])
        b = evaluator.evaluate(args[1])
        return max(a, b)


class AbsOperation(Operation):
    """ABS - Return absolute value.

    Usage: <ABS n>
    """

    @property
    def name(self) -> str:
        return "ABS"

    def execute(self, args: list, evaluator) -> int:
        if not args:
            return 0
        val = evaluator.evaluate(args[0])
        return abs(val) if isinstance(val, (int, float)) else 0


class SearchListOperation(Operation):
    """SEARCH-LIST - Search through object children list.

    Usage: <SEARCH-LIST object property value>
    Searches children of object for one whose property matches value.
    """

    @property
    def name(self) -> str:
        return "SEARCH-LIST"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 3:
            return False
        container = evaluator.evaluate(args[0])
        prop_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))
        target = evaluator.evaluate(args[2])

        container_obj = evaluator.world.get_object(container)
        if not container_obj:
            return False

        for child in container_obj.children:
            val = child.get_property(prop_name.upper())
            if val == target:
                return child

        return False


class FindInOperation(Operation):
    """FIND-IN - Find object in container by synonym.

    Usage: <FIND-IN container word>
    Returns first child of container that matches word.
    """

    @property
    def name(self) -> str:
        return "FIND-IN"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return False
        container = evaluator.evaluate(args[0])
        word = evaluator.evaluate(args[1])

        container_obj = evaluator.world.get_object(container)
        if not container_obj:
            return False

        word_str = str(word).upper()
        for child in container_obj.children:
            if child.matches_word(word_str):
                return child

        return False


class ZmemqOperation(Operation):
    """ZMEMQ - Search table for value.

    Usage: <ZMEMQ value table [length]>
    Returns offset if found, FALSE otherwise.
    """

    @property
    def name(self) -> str:
        return "ZMEMQ"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return False
        target = evaluator.evaluate(args[0])
        table = evaluator.evaluate(args[1])

        if isinstance(table, list):
            for i, val in enumerate(table):
                if val == target:
                    return i * 2  # Word offset
            return False
        return False


class ZmemqbOperation(Operation):
    """ZMEMQB - Search table for byte value.

    Usage: <ZMEMQB value table [length]>
    Returns offset if found, FALSE otherwise.
    """

    @property
    def name(self) -> str:
        return "ZMEMQB"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return False
        target = evaluator.evaluate(args[0])
        table = evaluator.evaluate(args[1])

        if isinstance(table, list):
            for i, val in enumerate(table):
                if val == target:
                    return i  # Byte offset
            return False
        return False


class LengthCheckOperation(Operation):
    """LENGTH? - Check length of table/list.

    Usage: <LENGTH? table min-length>
    Returns true if table has at least min-length elements.
    """

    @property
    def name(self) -> str:
        return "LENGTH?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        table = evaluator.evaluate(args[0])
        min_len = evaluator.evaluate(args[1])
        if isinstance(table, (list, str)):
            return len(table) >= min_len
        return False


class PutrestOperation(Operation):
    """PUTREST - Set the REST of a list.

    Usage: <PUTREST list new-rest>
    Sets the tail of list to new-rest.
    """

    @property
    def name(self) -> str:
        return "PUTREST"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None
        lst = evaluator.evaluate(args[0])
        new_rest = evaluator.evaluate(args[1])
        if isinstance(lst, list) and len(lst) > 0:
            first = lst[0]
            lst.clear()
            lst.append(first)
            if isinstance(new_rest, list):
                lst.extend(new_rest)
            return lst
        return lst


class MapstopOperation(Operation):
    """MAPSTOP - Stop MAPF iteration and return value.

    Usage: <MAPSTOP value>
    Stops current MAPF and returns value.
    """

    @property
    def name(self) -> str:
        return "MAPSTOP"

    def execute(self, args: list, evaluator) -> Any:
        val = evaluator.evaluate(args[0]) if args else None
        from zil_interpreter.engine.evaluator import ReturnValue
        raise ReturnValue(val)


class ChtypeOperation(Operation):
    """CHTYPE - Change type of a value.

    Usage: <CHTYPE value type>
    In the interpreter, this is mostly a no-op since we don't have
    strict type tags. Returns the value as-is for most cases.
    """

    @property
    def name(self) -> str:
        return "CHTYPE"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return None
        val = evaluator.evaluate(args[0])
        # In our interpreter, type coercion is mostly implicit
        return val


class SpnameOperation(Operation):
    """SPNAME - Get the print name (string) of an atom.

    Usage: <SPNAME atom>
    Returns the string representation of the atom name.
    """

    @property
    def name(self) -> str:
        return "SPNAME"

    def execute(self, args: list, evaluator) -> str:
        if not args:
            return ""
        val = args[0]
        if isinstance(val, Atom):
            return val.value
        val = evaluator.evaluate(val)
        from zil_interpreter.world.game_object import GameObject
        if isinstance(val, GameObject):
            return val.name
        return str(val)


class StuffOperation(Operation):
    """STUFF - Copy data between buffers.

    Usage: <STUFF src dest>
    Copies lexical data between input buffers.
    In the interpreter, this is a simplified implementation.
    """

    @property
    def name(self) -> str:
        return "STUFF"

    def execute(self, args: list, evaluator) -> Any:
        # In our interpreter, buffer management is simplified
        if len(args) < 2:
            return None
        src = evaluator.evaluate(args[0])
        dest = evaluator.evaluate(args[1])
        # Just return the source value
        return src
