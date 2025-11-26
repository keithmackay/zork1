"""Data types for command parsing."""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, List, Optional


class TokenType(Enum):
    """Types of tokens in a command."""
    VERB = auto()
    NOUN = auto()
    ADJECTIVE = auto()
    PREPOSITION = auto()
    DIRECTION = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """A single token from player input."""
    word: str
    type: TokenType = TokenType.UNKNOWN

    def __repr__(self) -> str:
        return f"Token({self.word!r}, {self.type.name})"


@dataclass
class NounPhrase:
    """A noun phrase with optional adjectives."""
    noun: str
    adjectives: List[str] = field(default_factory=list)


@dataclass
class ParsedCommand:
    """Result of parsing player input."""
    verb: str
    noun_phrases: List[NounPhrase] = field(default_factory=list)
    preposition: Optional[str] = None
    direction: Optional[str] = None

    @property
    def object_count(self) -> int:
        """Number of objects in command."""
        return len(self.noun_phrases)


@dataclass
class CommandResult:
    """Result of processing a command."""
    success: bool
    action: Optional[str] = None
    error: Optional[str] = None
    direct_object: Optional[Any] = None
    indirect_object: Optional[Any] = None
