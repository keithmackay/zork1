"""AST node definitions for ZIL parse tree."""

from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    pass


@dataclass
class Atom(ASTNode):
    """Represents a ZIL atom (identifier)."""
    value: str


@dataclass
class String(ASTNode):
    """Represents a string literal."""
    value: str


@dataclass
class Number(ASTNode):
    """Represents a numeric literal."""
    value: int | float


@dataclass
class Form(ASTNode):
    """Represents a ZIL form: <operator args...>"""
    operator: Atom
    args: List[Any] = field(default_factory=list)


@dataclass
class Routine(ASTNode):
    """Represents a ROUTINE definition."""
    name: str
    args: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class Object(ASTNode):
    """Represents an OBJECT definition."""
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Global(ASTNode):
    """Represents a GLOBAL variable definition."""
    name: str
    value: Any = None


@dataclass
class InsertFile(ASTNode):
    """Represents an INSERT-FILE directive."""
    filename: str
