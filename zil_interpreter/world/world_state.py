"""World state manager for ZIL interpreter."""

from typing import Dict, Any, Optional, List
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.world.table_data import TableData


class WorldState:
    """Manages the complete game world state."""

    def __init__(self):
        self.objects: Dict[str, GameObject] = {}
        self.globals: Dict[str, Any] = {}
        self.tables: Dict[str, TableData] = {}
        self._current_room: Optional[GameObject] = None

        # Initialize parser state globals
        self.globals["PRSA"] = None  # PRimary Action (verb)
        self.globals["PRSO"] = None  # PRimary object
        self.globals["PRSI"] = None  # Secondary/Indirect object

    def add_object(self, obj: GameObject) -> None:
        """Add an object to the world.

        Args:
            obj: The GameObject to add
        """
        self.objects[obj.name] = obj

    def get_object(self, name) -> Optional[GameObject]:
        """Get an object by name or return the object if already a GameObject.

        Args:
            name: Object name (str) or GameObject

        Returns:
            GameObject if found, None otherwise
        """
        if isinstance(name, GameObject):
            return name
        if name is None:
            return None
        return self.objects.get(str(name).upper())

    def find_object_by_word(self, word: str) -> Optional[GameObject]:
        """Find an object that matches the given word.

        Searches in priority order: inventory, current room contents,
        room globals, then all objects as fallback.

        Args:
            word: Word to match against object synonyms/adjectives

        Returns:
            First matching GameObject, or None
        """
        # Priority 1: Objects in player's inventory
        player = self.get_global("PLAYER") or self.get_global("ADVENTURER")
        if isinstance(player, GameObject):
            for child in player.children:
                if child.matches_word(word):
                    return child

        # Priority 2: Objects in current room (including nested)
        here = self.get_global("HERE")
        if isinstance(here, GameObject):
            for child in here.children:
                if child.matches_word(word):
                    return child
                # Check inside open containers in room
                if child.has_flag("OPENBIT"):
                    for grandchild in child.children:
                        if grandchild.matches_word(word):
                            return grandchild

            # Priority 3: Room's GLOBAL objects (visible from room)
            globals_prop = here.get_property("GLOBAL")
            if isinstance(globals_prop, list):
                for gname in globals_prop:
                    gobj = self.objects.get(str(gname).upper())
                    if gobj and gobj.matches_word(word):
                        return gobj

        # Priority 4: Fallback - search all objects
        for obj in self.objects.values():
            if obj.matches_word(word):
                return obj
        return None

    def set_global(self, name: str, value: Any) -> None:
        """Set a global variable.

        Args:
            name: Variable name
            value: Variable value
        """
        self.globals[name.upper()] = value

    def get_global(self, name: str, default: Any = None) -> Any:
        """Get a global variable.

        Args:
            name: Variable name
            default: Default value if not found

        Returns:
            Variable value or default
        """
        return self.globals.get(name.upper(), default)

    def set_parser_state(
        self,
        verb=None,
        direct_obj=None,
        indirect_obj=None
    ) -> None:
        """Set parser state variables.

        Args:
            verb: Current verb (PRSA)
            direct_obj: Direct object (PRSO) - string or GameObject
            indirect_obj: Indirect object (PRSI) - string or GameObject
        """
        if verb is not None:
            self.globals["PRSA"] = verb.upper() if isinstance(verb, str) else verb
        if direct_obj is not None:
            self.globals["PRSO"] = direct_obj
        if indirect_obj is not None:
            self.globals["PRSI"] = indirect_obj

    def set_current_room(self, room: GameObject) -> None:
        """Set the current room.

        Args:
            room: Room object
        """
        self._current_room = room
        self.globals["HERE"] = room

    def get_current_room(self) -> Optional[GameObject]:
        """Get the current room.

        Returns:
            Current room GameObject
        """
        return self._current_room

    def register_table(self, name: str, table: TableData) -> None:
        """Register a table in the world.

        Args:
            name: Table name
            table: TableData instance
        """
        self.tables[name] = table

    def get_table(self, name: str) -> TableData:
        """Get a table by name.

        Args:
            name: Table name

        Returns:
            TableData instance

        Raises:
            KeyError: If table not found
        """
        if name not in self.tables:
            raise KeyError(f"Unknown table: {name}")
        return self.tables[name]

    def has_table(self, name: str) -> bool:
        """Check if table exists.

        Args:
            name: Table name

        Returns:
            True if table exists, False otherwise
        """
        return name in self.tables

    def serialize(self) -> Dict[str, Any]:
        """Serialize world state for saving.

        Returns:
            Dict containing all world state for JSON serialization
        """
        def _serialize_val(v):
            if isinstance(v, GameObject):
                return v.name
            return v

        return {
            "globals": {k: _serialize_val(v) for k, v in self.globals.items()
                        if not callable(v)},  # Skip function values
            "objects": {
                name: obj.serialize()
                for name, obj in self.objects.items()
            },
            "tables": {
                name: {"name": table.name, "data": table.data}
                for name, table in self.tables.items()
            },
            "current_room": self._current_room.name if self._current_room else None
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore world state from saved data.

        Args:
            data: Dict containing saved world state
        """
        # Restore globals
        self.globals.update(data.get("globals", {}))

        # Restore objects
        for name, obj_data in data.get("objects", {}).items():
            if name in self.objects:
                self.objects[name].deserialize(obj_data)

        # Restore tables
        for name, table_data in data.get("tables", {}).items():
            if name in self.tables:
                self.tables[name].data = table_data.get("data", [])

        # Restore current room
        room_name = data.get("current_room")
        if room_name and room_name in self.objects:
            self._current_room = self.objects[room_name]

    def reset(self) -> None:
        """Reset world to initial state.

        This clears all mutable state while preserving object definitions.
        """
        # Reset parser state
        self.globals["PRSA"] = None
        self.globals["PRSO"] = None
        self.globals["PRSI"] = None

        # Reset score and moves if they exist
        if "SCORE" in self.globals:
            self.globals["SCORE"] = 0
        if "MOVES" in self.globals:
            self.globals["MOVES"] = 0

        # Reset objects to initial state
        for obj in self.objects.values():
            obj.reset()

        # Clear current room (will be set by GO routine)
        self._current_room = None
