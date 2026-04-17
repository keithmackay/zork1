"""Object resolver for command parsing."""
from typing import List, Optional
from .command_types import NounPhrase
from ..world.world_state import WorldState
from ..world.game_object import GameObject, ObjectFlag


class DisambiguationNeeded(Exception):
    """Raised when multiple objects match and disambiguation is needed."""

    def __init__(self, candidates: List[GameObject], message: str = ""):
        self.candidates = candidates
        self.message = message or f"Which {candidates[0].synonyms[0] if candidates[0].synonyms else 'object'} do you mean?"
        super().__init__(self.message)


class ObjectResolver:
    """Resolve noun phrases to game objects."""

    def __init__(self, world: WorldState):
        """Initialize resolver with world state.

        Args:
            world: WorldState containing objects
        """
        self._world = world

    def resolve(
        self,
        noun_phrase: NounPhrase,
        current_room: GameObject
    ) -> Optional[GameObject]:
        """Resolve noun phrase to a single object.

        Args:
            noun_phrase: NounPhrase to resolve
            current_room: Current room for accessibility check

        Returns:
            Single matching GameObject or None

        Raises:
            DisambiguationNeeded: If multiple objects match
        """
        matches = self.find_matches(noun_phrase, current_room)

        if not matches:
            return None

        if len(matches) == 1:
            return matches[0]

        # Multiple matches - disambiguation needed
        raise DisambiguationNeeded(matches)

    def find_matches(
        self,
        noun_phrase: NounPhrase,
        current_room: GameObject
    ) -> List[GameObject]:
        """Find all objects matching noun phrase within accessible scope.

        Only searches objects that are actually accessible to the player:
        - Directly in the current room
        - Contents of open/transparent containers in the current room
        - Player's inventory
        - Contents of open/transparent containers in inventory
        - LOCAL-GLOBALS (room-scoped ambient objects)

        Args:
            noun_phrase: NounPhrase to match
            current_room: Current room for accessibility check

        Returns:
            List of matching accessible objects
        """
        candidates: List[GameObject] = []

        # 1. Objects directly in the current room (and contents of open containers)
        for obj in current_room.children:
            candidates.append(obj)
            if self._is_open_container(obj):
                candidates.extend(obj.children)

        # 2. Player inventory (and contents of open containers in inventory)
        player = self._world.get_global("WINNER")
        if player and isinstance(player, GameObject):
            for obj in player.children:
                candidates.append(obj)
                if self._is_open_container(obj):
                    candidates.extend(obj.children)

        # 3. LOCAL-GLOBALS (room-scoped ambient objects like "stream", "chasm")
        local_globals = self._world.get_object("LOCAL-GLOBALS")
        if local_globals:
            candidates.extend(local_globals.children)

        # Filter by noun and adjectives
        return [
            obj for obj in candidates
            if self._matches_noun(obj, noun_phrase.noun)
            and (
                not noun_phrase.adjectives
                or self._matches_adjectives(obj, noun_phrase.adjectives)
            )
        ]

    def _is_open_container(self, obj: GameObject) -> bool:
        """Return True if obj is a container that can be seen into."""
        return obj.has_flag(ObjectFlag.CONTAINER) and obj.has_flag(ObjectFlag.OPEN)

    def is_accessible(
        self,
        obj: GameObject,
        current_room: GameObject
    ) -> bool:
        """Check if object is accessible from current room.

        Accessible means:
        - In current room
        - In player's inventory
        - In an open container in the room

        Args:
            obj: Object to check
            current_room: Current room

        Returns:
            True if accessible
        """
        # Get player
        player = self._world.get_global("WINNER")

        # Check if directly in room
        if obj.parent == current_room:
            return True

        # Check if in player inventory
        if player and obj.parent == player:
            return True

        # Check if in open container in room or inventory
        if obj.parent:
            parent = obj.parent

            # Parent must be accessible
            if not self.is_accessible(parent, current_room):
                return False

            # Parent must be open container
            if parent.has_flag(ObjectFlag.CONTAINER):
                if not parent.has_flag(ObjectFlag.OPEN):
                    return False
                return True

        return False

    def _matches_noun(self, obj: GameObject, noun: str) -> bool:
        """Check if object matches noun.

        Args:
            obj: Object to check
            noun: Noun to match

        Returns:
            True if noun matches object synonyms
        """
        noun_upper = noun.upper()
        return obj.matches_word(noun_upper)

    def _matches_adjectives(
        self,
        obj: GameObject,
        adjectives: List[str]
    ) -> bool:
        """Check if object matches all adjectives.

        Args:
            obj: Object to check
            adjectives: Adjectives that must all match

        Returns:
            True if all adjectives match
        """
        obj_adjs = [a.upper() for a in obj.adjectives]

        for adj in adjectives:
            if adj.upper() not in obj_adjs:
                return False

        return True
