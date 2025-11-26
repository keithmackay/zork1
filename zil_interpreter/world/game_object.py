"""Game object representation for ZIL world model."""

from enum import Flag, auto
from typing import Any, Dict, List, Optional, Set


class ObjectFlag(Flag):
    """Standard ZIL object flags."""
    OPEN = auto()
    CONTAINER = auto()
    SURFACE = auto()
    TAKEABLE = auto()
    LOCKED = auto()
    NDESCBIT = auto()  # No automatic description
    TOUCHBIT = auto()
    LIGHTBIT = auto()
    ONBIT = auto()  # Light is on
    INVISIBLE = auto()


class GameObject:
    """Represents a game object in the ZIL world."""

    def __init__(
        self,
        name: str,
        description: str = "",
        synonyms: Optional[List[str]] = None,
        adjectives: Optional[List[str]] = None,
        parent: Optional['GameObject'] = None
    ):
        self.name = name
        self.description = description
        self.synonyms = synonyms or []
        self.adjectives = adjectives or []
        self._parent: Optional['GameObject'] = None
        self.children: Set['GameObject'] = set()
        self.properties: Dict[str, Any] = {}
        self.flags: ObjectFlag = ObjectFlag(0)
        self.action_routine: Optional[str] = None

        if parent:
            self.move_to(parent)

    @property
    def parent(self) -> Optional['GameObject']:
        """Get object's parent/location."""
        return self._parent

    def move_to(self, new_parent: Optional['GameObject']) -> None:
        """Move object to a new parent/location."""
        # Remove from old parent
        if self._parent:
            self._parent.children.discard(self)

        # Add to new parent
        self._parent = new_parent
        if new_parent:
            new_parent.children.add(self)

    def set_property(self, prop_name: str, value: Any) -> None:
        """Set an object property."""
        self.properties[prop_name] = value

    def get_property(self, prop_name: str, default: Any = None) -> Any:
        """Get an object property."""
        return self.properties.get(prop_name, default)

    def set_flag(self, flag: ObjectFlag) -> None:
        """Set an object flag."""
        self.flags |= flag

    def clear_flag(self, flag: ObjectFlag) -> None:
        """Clear an object flag."""
        self.flags &= ~flag

    def has_flag(self, flag: ObjectFlag) -> bool:
        """Check if object has a flag set."""
        return bool(self.flags & flag)

    def matches_word(self, word: str) -> bool:
        """Check if word matches this object's synonyms."""
        word_upper = word.upper()
        return word_upper in [s.upper() for s in self.synonyms]

    def __repr__(self) -> str:
        return f"GameObject({self.name})"

    def serialize(self) -> Dict[str, Any]:
        """Serialize object state for saving.

        Returns:
            Dict containing object's mutable state
        """
        return {
            "parent": self._parent.name if self._parent else None,
            "properties": self.properties.copy(),
            "flags": self.flags.value,
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore object state from saved data.

        Note: Parent relationships must be restored after all objects loaded.

        Args:
            data: Dict containing saved object state
        """
        self.properties = data.get("properties", {})
        self.flags = ObjectFlag(data.get("flags", 0))

    def reset(self) -> None:
        """Reset object to initial state.

        Clears mutable state while preserving definition.
        """
        # Clear flags to initial state
        self.flags = ObjectFlag(0)
        # Properties are typically set during world load
        self.properties = {}
