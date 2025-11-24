from .base import Operation, OperationRegistry
from .comparison import (
    EqualOperation,
    FsetCheckOperation,
    VerbCheckOperation,
    InCheckOperation,
    FirstCheckOperation,
)
from .control import CondOperation
from .arithmetic import AddOperation
from .io import TellOperation


def create_default_registry() -> OperationRegistry:
    """Create registry with all standard operations."""
    registry = OperationRegistry()

    # Comparison
    registry.register(EqualOperation())
    registry.register(FsetCheckOperation())
    registry.register(VerbCheckOperation())
    registry.register(InCheckOperation())
    registry.register(FirstCheckOperation())

    # Control
    registry.register(CondOperation())

    # Arithmetic
    registry.register(AddOperation())

    # I/O
    registry.register(TellOperation())

    return registry


__all__ = ['Operation', 'OperationRegistry', 'create_default_registry']
