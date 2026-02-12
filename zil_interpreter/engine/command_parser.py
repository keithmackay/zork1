"""Command parser for player input."""

from typing import Optional, Dict, List
from zil_interpreter.world.world_state import WorldState


class CommandParser:
    """Parses player commands into structured actions."""

    # Common verbs and their variations
    VERBS = {
        'LOOK': ['look', 'l'],
        'TAKE': ['take', 'get', 'pick up'],
        'DROP': ['drop', 'put down'],
        'INVENTORY': ['inventory', 'i'],
        'GO': ['go', 'walk', 'run'],
        'NORTH': ['north', 'n'],
        'SOUTH': ['south', 's'],
        'EAST': ['east', 'e'],
        'WEST': ['west', 'w'],
        'UP': ['up', 'u'],
        'DOWN': ['down', 'd'],
        'OPEN': ['open'],
        'CLOSE': ['close'],
        'EXAMINE': ['examine', 'x', 'inspect'],
        'READ': ['read'],
        'PUT': ['put', 'place'],
    }

    # Prepositions to ignore/handle
    PREPOSITIONS = ['in', 'on', 'with', 'to', 'at', 'from']

    def __init__(self, world: WorldState):
        self.world = world

    def parse(self, command: str) -> Optional[Dict]:
        """Parse a player command.

        Args:
            command: Player input string

        Returns:
            Dict with verb, direct_object, indirect_object
            or None if parsing fails
        """
        # Tokenize
        tokens = command.lower().strip().split()
        if not tokens:
            return None

        # Find verb
        verb = self._find_verb(tokens)
        if not verb:
            return None

        # Remove verb from tokens
        verb_token = self._get_verb_token(tokens[0])
        if verb_token:
            tokens = tokens[1:]
        else:
            # Multi-word verb like "pick up"
            for i in range(len(tokens)):
                test_phrase = ' '.join(tokens[:i+1])
                if self._get_verb_token(test_phrase):
                    tokens = tokens[i+1:]
                    break

        # Remove prepositions and find objects
        cleaned_tokens = []
        prep_index = -1

        for i, token in enumerate(tokens):
            if token in self.PREPOSITIONS:
                prep_index = i
                break
            cleaned_tokens.append(token)

        # Direct object (before preposition)
        direct_obj = None
        if cleaned_tokens:
            direct_obj = self._find_object(' '.join(cleaned_tokens))

        # Indirect object (after preposition)
        indirect_obj = None
        if prep_index >= 0 and prep_index + 1 < len(tokens):
            remaining = ' '.join(tokens[prep_index + 1:])
            indirect_obj = self._find_object(remaining)

        return {
            'verb': verb,
            'direct_object': direct_obj,
            'indirect_object': indirect_obj
        }

    def _find_verb(self, tokens: List[str]) -> Optional[str]:
        """Find verb in tokens."""
        # Try first token
        verb = self._get_verb_token(tokens[0])
        if verb:
            return verb

        # Try multi-word verbs
        for i in range(min(3, len(tokens))):
            phrase = ' '.join(tokens[:i+1])
            verb = self._get_verb_token(phrase)
            if verb:
                return verb

        return None

    def _get_verb_token(self, token: str) -> Optional[str]:
        """Get canonical verb for token."""
        for canonical, variations in self.VERBS.items():
            if token in variations:
                return canonical
        return None

    def _find_object(self, text: str):
        """Find object matching text.

        Returns:
            GameObject if found, None otherwise.
        """
        return self.world.find_object_by_word(text)
