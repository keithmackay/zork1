"""World state manager for ZIL interpreter."""

from typing import Dict, Any, Optional, List
from zil_interpreter.world.game_object import GameObject


class WorldState:
    """Manages the complete game world state."""

    def __init__(self):
        self.objects: Dict[str, GameObject] = {}
        self.globals: Dict[str, Any] = {}
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

    def get_object(self, name: str) -> Optional[GameObject]:
        """Get an object by name.

        Args:
            name: Object name

        Returns:
            GameObject if found, None otherwise
        """
        return self.objects.get(name.upper())

    def find_object_by_word(self, word: str) -> Optional[GameObject]:
        """Find an object that matches the given word.

        Args:
            word: Word to match against object synonyms

        Returns:
            First matching GameObject, or None
        """
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
        verb: Optional[str] = None,
        direct_obj: Optional[str] = None,
        indirect_obj: Optional[str] = None
    ) -> None:
        """Set parser state variables.

        Args:
            verb: Current verb (PRSA)
            direct_obj: Direct object (PRSO)
            indirect_obj: Indirect object (PRSI)
        """
        if verb is not None:
            self.globals["PRSA"] = verb.upper()
        if direct_obj is not None:
            self.globals["PRSO"] = direct_obj.upper()
        if indirect_obj is not None:
            self.globals["PRSI"] = indirect_obj.upper() if indirect_obj else None

    def set_current_room(self, room: GameObject) -> None:
        """Set the current room.

        Args:
            room: Room object
        """
        self._current_room = room
        self.globals["HERE"] = room.name

    def get_current_room(self) -> Optional[GameObject]:
        """Get the current room.

        Returns:
            Current room GameObject
        """
        return self._current_room
