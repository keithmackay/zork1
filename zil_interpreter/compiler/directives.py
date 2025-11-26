"""Compile-time directive dataclasses for ZIL."""
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ConstantDef:
    """CONSTANT definition.

    Example: <CONSTANT M-ENTER 2>
    """
    name: str
    value: Any


@dataclass
class GlobalDef:
    """GLOBAL variable definition.

    Example: <GLOBAL LUCKY T>
    """
    name: str
    initial_value: Any


@dataclass
class PropDef:
    """PROPDEF property default definition.

    Example: <PROPDEF SIZE 5>
    """
    name: str
    default: Any


@dataclass
class DirectionsDef:
    """DIRECTIONS declaration.

    Example: <DIRECTIONS NORTH EAST WEST SOUTH NE NW SE SW UP DOWN IN OUT LAND>
    """
    directions: List[str]


@dataclass
class SynonymDef:
    """SYNONYM declaration.

    Example: <SYNONYM WITH USING THROUGH THRU>
    First word is primary, rest are aliases.
    """
    primary: str
    aliases: List[str]


@dataclass
class BuzzDef:
    """BUZZ (noise words) declaration.

    Example: <BUZZ A AN THE IS AND OF THEN>
    These words are ignored by the parser.
    """
    words: List[str]


@dataclass
class ObjectConstraint:
    """Object constraint in SYNTAX definition.

    Constraints specify how the parser should find the object:
    - FIND flagbit: Object must have the specified flag
    - HELD: Object must be held by player
    - CARRIED: Object must be carried
    - MANY: Multiple objects allowed
    - HAVE: Object must be in inventory
    - IN-ROOM: Object must be in current room
    - ON-GROUND: Object must be on the ground
    """
    position: int  # 1 = PRSO (direct object), 2 = PRSI (indirect object)
    constraints: List[str] = field(default_factory=list)


@dataclass
class SyntaxDef:
    """SYNTAX verb pattern definition.

    Example: <SYNTAX PUT OBJECT IN OBJECT = V-PUT PRE-PUT>

    Components:
    - verb: The verb word (PUT)
    - objects: Object slots with constraints
    - prepositions: Words between objects (IN)
    - action: The routine to call (V-PUT)
    - preaction: Optional pre-check routine (PRE-PUT)
    """
    verb: str
    action: str
    objects: List[ObjectConstraint] = field(default_factory=list)
    prepositions: List[str] = field(default_factory=list)
    preaction: Optional[str] = None
