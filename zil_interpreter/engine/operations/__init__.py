from .base import Operation, OperationRegistry
from .comparison import (
    EqualOperation,
    FsetCheckOperation,
    VerbCheckOperation,
    InCheckOperation,
    FirstCheckOperation,
)
from .control import CondOperation, RtrueOperation, RfalseOperation
from .arithmetic import AddOperation
from .io import TellOperation
from .object_ops import (
    MoveOperation,
    FsetOperation,
    FclearOperation,
    GetpOperation,
    PutpOperation,
)
from .variables import SetOperation, SetgOperation


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
    registry.register(RtrueOperation())
    registry.register(RfalseOperation())

    # Arithmetic
    registry.register(AddOperation())

    # I/O
    registry.register(TellOperation())

    # Object Operations
    registry.register(MoveOperation())
    registry.register(FsetOperation())
    registry.register(FclearOperation())
    registry.register(GetpOperation())
    registry.register(PutpOperation())

    # Variables
    registry.register(SetOperation())
    registry.register(SetgOperation())

    return registry


__all__ = ['Operation', 'OperationRegistry', 'create_default_registry']
