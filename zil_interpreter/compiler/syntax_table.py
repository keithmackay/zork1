"""SYNTAX table for ZIL verb patterns."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .directives import SyntaxDef, ObjectConstraint
from ..parser.ast_nodes import Form, Atom


@dataclass
class SyntaxEntry:
    """A single SYNTAX table entry."""
    verb: str
    action: str
    object_count: int = 0
    prepositions: List[str] = field(default_factory=list)
    preaction: Optional[str] = None
    constraints: List[List[str]] = field(default_factory=list)


class SyntaxTable:
    """Table of SYNTAX verb patterns.

    Used by the parser to match player commands to actions.
    """

    def __init__(self):
        """Initialize empty syntax table."""
        self._entries: Dict[str, List[SyntaxEntry]] = {}
        self._entry_count = 0

    @property
    def entry_count(self) -> int:
        """Get total number of entries."""
        return self._entry_count

    def add_entry(
        self,
        verb: str,
        object_positions: List[int],
        prepositions: List[str],
        action: str,
        preaction: Optional[str]
    ) -> None:
        """Add a syntax entry.

        Args:
            verb: The verb word
            object_positions: List of object positions (1=PRSO, 2=PRSI)
            prepositions: List of prepositions between objects
            action: The action routine name
            preaction: Optional pre-action routine name
        """
        entry = SyntaxEntry(
            verb=verb.upper(),
            action=action,
            object_count=len(object_positions),
            prepositions=[p.upper() for p in prepositions],
            preaction=preaction
        )
        self._add_entry_internal(entry)

    def add_entry_from_def(self, syntax_def: SyntaxDef) -> None:
        """Add entry from a SyntaxDef."""
        entry = SyntaxEntry(
            verb=syntax_def.verb.upper(),
            action=syntax_def.action,
            object_count=len(syntax_def.objects),
            prepositions=[p.upper() for p in syntax_def.prepositions],
            preaction=syntax_def.preaction,
            constraints=[obj.constraints for obj in syntax_def.objects]
        )
        self._add_entry_internal(entry)

    def _add_entry_internal(self, entry: SyntaxEntry) -> None:
        """Internal method to add an entry."""
        verb = entry.verb
        if verb not in self._entries:
            self._entries[verb] = []
        self._entries[verb].append(entry)
        self._entry_count += 1

    def lookup(self, verb: str) -> List[SyntaxEntry]:
        """Look up all syntax entries for a verb.

        Args:
            verb: The verb to look up (case-insensitive)

        Returns:
            List of matching SyntaxEntry objects
        """
        return self._entries.get(verb.upper(), [])

    def match(
        self,
        verb: str,
        object_count: int,
        preposition: Optional[str]
    ) -> Optional[SyntaxEntry]:
        """Find a matching syntax entry.

        Args:
            verb: The verb word
            object_count: Number of objects in command
            preposition: Preposition used (if any)

        Returns:
            Matching SyntaxEntry or None
        """
        entries = self.lookup(verb)

        for entry in entries:
            # Check object count
            if entry.object_count != object_count:
                continue

            # Check preposition
            if object_count >= 2:
                if preposition is None:
                    continue
                if preposition.upper() not in entry.prepositions:
                    continue

            return entry

        return None


def parse_syntax_entry(args: List[Any]) -> Optional[SyntaxDef]:
    """Parse SYNTAX directive arguments into SyntaxDef.

    SYNTAX format:
    <SYNTAX verb [OBJECT [(constraints)]] [prep [OBJECT [(constraints)]]] = action [preaction]>

    Args:
        args: Arguments to SYNTAX directive

    Returns:
        SyntaxDef or None if parsing fails
    """
    if not args:
        return None

    # Find the = separator
    equals_idx = -1
    for i, arg in enumerate(args):
        if isinstance(arg, Atom) and arg.value == "=":
            equals_idx = i
            break

    if equals_idx < 1:
        return None

    # Parse left side (verb pattern)
    pattern_args = args[:equals_idx]
    action_args = args[equals_idx + 1:]

    if not pattern_args or not action_args:
        return None

    # First arg is verb
    verb = _get_atom_value(pattern_args[0])
    if verb is None:
        return None

    # Parse objects and prepositions
    objects = []
    prepositions = []
    position = 1
    i = 1

    while i < len(pattern_args):
        arg = pattern_args[i]

        if isinstance(arg, Atom):
            name = arg.value.upper()

            if name == "OBJECT":
                # Check for constraints
                constraints = []
                if i + 1 < len(pattern_args) and isinstance(pattern_args[i + 1], list):
                    constraints = [_get_atom_value(c) for c in pattern_args[i + 1] if _get_atom_value(c)]
                    i += 1

                objects.append(ObjectConstraint(position=position, constraints=constraints))
                position += 1
            else:
                # Preposition
                prepositions.append(name)

        elif isinstance(arg, list):
            # Standalone constraint list - attach to previous object or skip
            if objects:
                # Merge constraints with last object
                constraints = [_get_atom_value(c) for c in arg if _get_atom_value(c)]
                objects[-1].constraints.extend(constraints)

        i += 1

    # Parse action and preaction
    action = _get_atom_value(action_args[0])
    if action is None:
        return None

    preaction = None
    if len(action_args) > 1:
        preaction = _get_atom_value(action_args[1])

    return SyntaxDef(
        verb=verb,
        action=action,
        objects=objects,
        prepositions=prepositions,
        preaction=preaction
    )


def _get_atom_value(node: Any) -> Optional[str]:
    """Get string value from an Atom node."""
    if isinstance(node, Atom):
        return node.value
    return None
