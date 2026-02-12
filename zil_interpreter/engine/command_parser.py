"""Command parser for player input."""

from typing import Optional, Dict, List
from zil_interpreter.world.world_state import WorldState


class CommandParser:
    """Parses player commands into structured actions."""

    # Common verbs and their variations
    VERBS = {
        # Navigation
        'LOOK': ['look', 'l'],
        'GO': ['go', 'walk', 'run'],
        'NORTH': ['north', 'n'],
        'SOUTH': ['south', 's'],
        'EAST': ['east', 'e'],
        'WEST': ['west', 'w'],
        'UP': ['up', 'u'],
        'DOWN': ['down', 'd'],
        'NE': ['ne', 'northeast'],
        'NW': ['nw', 'northwest'],
        'SE': ['se', 'southeast'],
        'SW': ['sw', 'southwest'],
        'ENTER': ['enter', 'go in'],
        'EXIT': ['exit', 'leave', 'go out', 'out'],
        'LAUNCH': ['launch'],
        'LAND': ['land'],
        # Object manipulation
        'TAKE': ['take', 'get', 'pick up', 'grab'],
        'DROP': ['drop', 'put down', 'discard'],
        'PUT': ['put', 'place', 'insert'],
        'OPEN': ['open'],
        'CLOSE': ['close', 'shut'],
        'GIVE': ['give', 'hand', 'offer'],
        'THROW': ['throw', 'toss', 'hurl'],
        'MOVE': ['move', 'push', 'pull', 'drag'],
        'TURN': ['turn', 'rotate', 'twist', 'spin'],
        'LAMP-ON': ['turn on', 'switch on', 'activate'],
        'LAMP-OFF': ['turn off', 'switch off', 'deactivate'],
        'TIE': ['tie', 'fasten', 'attach'],
        'UNTIE': ['untie', 'unfasten', 'detach'],
        'FILL': ['fill'],
        'EMPTY': ['empty'],
        'POUR': ['pour'],
        'DIG': ['dig'],
        'SWIM': ['swim'],
        # Interaction
        'EXAMINE': ['examine', 'x', 'inspect', 'look at'],
        'READ': ['read'],
        'EAT': ['eat', 'consume', 'taste'],
        'DRINK': ['drink', 'sip', 'quaff'],
        'ATTACK': ['attack', 'kill', 'hit', 'fight', 'stab', 'slash'],
        'BREAK': ['break', 'smash', 'destroy', 'shatter'],
        'BURN': ['burn', 'ignite', 'light'],
        'BLOW': ['blow', 'extinguish'],
        'WAVE': ['wave', 'shake'],
        'RUB': ['rub', 'touch', 'feel', 'pet'],
        'LOCK': ['lock'],
        'UNLOCK': ['unlock'],
        'KICK': ['kick'],
        'KNOCK': ['knock'],
        'LISTEN': ['listen'],
        'SMELL': ['smell', 'sniff'],
        'PRAY': ['pray'],
        'CURSE': ['curse', 'damn', 'swear'],
        'SAY': ['say', 'speak', 'talk', 'tell', 'shout', 'yell'],
        'RING': ['ring'],
        'WIND': ['wind'],
        'CLIMB': ['climb'],
        'JUMP': ['jump', 'leap'],
        'WAIT': ['wait', 'z'],
        # Status
        'INVENTORY': ['inventory', 'i'],
        'SCORE': ['score'],
        'DIAGNOSE': ['diagnose', 'health'],
        'VERBOSE': ['verbose'],
        'BRIEF': ['brief'],
        'SUPERBRIEF': ['superbrief'],
        # System
        'SAVE': ['save'],
        'RESTORE': ['restore', 'load'],
        'RESTART': ['restart'],
        'AGAIN': ['again', 'g'],
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

        # Remove verb tokens (longest match first)
        for i in range(min(3, len(tokens)), 0, -1):
            test_phrase = ' '.join(tokens[:i])
            if self._get_verb_token(test_phrase):
                tokens = tokens[i:]
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
        """Find verb in tokens (longest match first)."""
        # Try multi-word verbs first (longest to shortest)
        for i in range(min(3, len(tokens)), 0, -1):
            phrase = ' '.join(tokens[:i])
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
