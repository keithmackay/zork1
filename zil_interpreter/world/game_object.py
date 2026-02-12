"""Game object representation for ZIL world model."""

from enum import Flag, auto
from typing import Any, Dict, List, Optional, Set


class ObjectFlag(Flag):
    """Standard ZIL object flags (legacy enum for backward compatibility)."""
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


# Map between ZIL flag names and ObjectFlag enum values
ZIL_FLAG_MAP = {
    "OPENBIT": ObjectFlag.OPEN,
    "CONTBIT": ObjectFlag.CONTAINER,
    "CONTAINERBIT": ObjectFlag.CONTAINER,
    "SURFACEBIT": ObjectFlag.SURFACE,
    "TAKEBIT": ObjectFlag.TAKEABLE,
    "TAKEABLEBIT": ObjectFlag.TAKEABLE,
    "LOCKEDBIT": ObjectFlag.LOCKED,
    "NDESCBIT": ObjectFlag.NDESCBIT,
    "TOUCHBIT": ObjectFlag.TOUCHBIT,
    "LIGHTBIT": ObjectFlag.LIGHTBIT,
    "ONBIT": ObjectFlag.ONBIT,
}


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
        self.children: List['GameObject'] = []
        self.properties: Dict[str, Any] = {}
        self.flags: ObjectFlag = ObjectFlag(0)
        self._zil_flags: Set[str] = set()  # String-based flags for full ZIL support
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
            try:
                self._parent.children.remove(self)
            except ValueError:
                pass

        # Add to new parent
        self._parent = new_parent
        if new_parent and self not in new_parent.children:
            new_parent.children.append(self)

    def set_property(self, prop_name: str, value: Any) -> None:
        """Set an object property."""
        self.properties[prop_name] = value

    def get_property(self, prop_name: str, default: Any = None) -> Any:
        """Get an object property."""
        return self.properties.get(prop_name, default)

    def set_flag(self, flag) -> None:
        """Set an object flag (ObjectFlag enum or string)."""
        if isinstance(flag, str):
            self._zil_flags.add(flag.upper())
            # Also set enum flag if it maps
            enum_flag = ZIL_FLAG_MAP.get(flag.upper())
            if enum_flag:
                self.flags |= enum_flag
        elif isinstance(flag, ObjectFlag):
            self.flags |= flag

    def clear_flag(self, flag) -> None:
        """Clear an object flag (ObjectFlag enum or string)."""
        if isinstance(flag, str):
            self._zil_flags.discard(flag.upper())
            enum_flag = ZIL_FLAG_MAP.get(flag.upper())
            if enum_flag:
                self.flags &= ~enum_flag
        elif isinstance(flag, ObjectFlag):
            self.flags &= ~flag

    def has_flag(self, flag) -> bool:
        """Check if object has a flag set (ObjectFlag enum or string)."""
        if isinstance(flag, str):
            flag_upper = flag.upper()
            # Check string flags first
            if flag_upper in self._zil_flags:
                return True
            # Fall back to enum check
            enum_flag = ZIL_FLAG_MAP.get(flag_upper)
            if enum_flag:
                return bool(self.flags & enum_flag)
            return False
        elif isinstance(flag, ObjectFlag):
            return bool(self.flags & flag)
        return False

    def matches_word(self, word: str) -> bool:
        """Check if word or phrase matches this object's synonyms/adjectives.

        Handles single words ("door") and multi-word phrases ("trap door")
        by matching the last word as a noun against synonyms and preceding
        words as adjectives.
        """
        word_upper = word.upper()
        synonym_list = [str(s).upper() for s in self.synonyms]

        # Single word - check synonyms directly
        if ' ' not in word_upper:
            return word_upper in synonym_list

        # Multi-word phrase: last word is noun, preceding words are adjectives
        words = word_upper.split()
        noun = words[-1]
        adj_words = words[:-1]

        if noun not in synonym_list:
            return False

        # Check that all adjective words match object's adjectives
        obj_adjs = [str(a).upper() for a in self.adjectives]
        return all(adj in obj_adjs for adj in adj_words)

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
            "zil_flags": list(self._zil_flags),
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore object state from saved data.

        Note: Parent relationships must be restored after all objects loaded.

        Args:
            data: Dict containing saved object state
        """
        self.properties = data.get("properties", {})
        self.flags = ObjectFlag(data.get("flags", 0))
        self._zil_flags = set(data.get("zil_flags", []))

    def reset(self) -> None:
        """Reset object to initial state.

        Clears mutable state while preserving definition.
        """
        # Clear flags to initial state
        self.flags = ObjectFlag(0)
        self._zil_flags = set()
        # Properties are typically set during world load
        self.properties = {}
