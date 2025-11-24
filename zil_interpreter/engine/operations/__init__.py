from .base import Operation, OperationRegistry
from .comparison import (
    EqualOperation,
    FsetCheckOperation,
    VerbCheckOperation,
    InCheckOperation,
    FirstCheckOperation,
    LessThanOperation,
    GreaterThanOperation,
    LessEqualOperation,
    GreaterEqualOperation,
    ZeroCheckOperation,
    NumericEqualOperation,
)
from .control import CondOperation, RtrueOperation, RfalseOperation
from .arithmetic import (
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
    ModOperation,
)
from .io import TellOperation
from .object_ops import (
    MoveOperation,
    FsetOperation,
    FclearOperation,
    GetpOperation,
    PutpOperation,
)
from .variables import SetOperation, SetgOperation
from .logic import AndOperation, OrOperation, NotOperation
from .string_ops import ConcatOperation, SubstringOperation, PrintcOperation


def create_default_registry() -> OperationRegistry:
    """Create registry with all standard operations."""
    registry = OperationRegistry()

    # Logic
    registry.register(AndOperation())
    registry.register(OrOperation())
    registry.register(NotOperation())

    # Comparison
    registry.register(EqualOperation())
    registry.register(FsetCheckOperation())
    registry.register(VerbCheckOperation())
    registry.register(InCheckOperation())
    registry.register(FirstCheckOperation())

    # Numeric comparison operations
    less_than = LessThanOperation()
    registry.register(less_than)
    registry._operations["L?"] = less_than  # Alias L? for <

    greater_than = GreaterThanOperation()
    registry.register(greater_than)
    registry._operations["G?"] = greater_than  # Alias G? for >

    registry.register(LessEqualOperation())
    registry.register(GreaterEqualOperation())
    registry.register(ZeroCheckOperation())
    registry.register(NumericEqualOperation())

    # Control
    registry.register(CondOperation())
    registry.register(RtrueOperation())
    registry.register(RfalseOperation())

    # Arithmetic
    registry.register(AddOperation())
    registry.register(SubtractOperation())
    registry.register(MultiplyOperation())
    registry.register(DivideOperation())
    registry.register(ModOperation())

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

    # String Operations
    registry.register(ConcatOperation())
    registry.register(SubstringOperation())
    registry.register(PrintcOperation())

    return registry


__all__ = ['Operation', 'OperationRegistry', 'create_default_registry']
