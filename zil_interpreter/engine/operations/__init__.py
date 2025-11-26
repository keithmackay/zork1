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
    DlessOperation,
)
from .control import (
    CondOperation,
    RtrueOperation,
    RfalseOperation,
    ReturnOperation,
    RepeatOperation,
    MapfOperation,
    ProgOperation,
    DoOperation,
    QuitOperation,
)
from .arithmetic import (
    AddOperation,
    SubtractOperation,
    MultiplyOperation,
    DivideOperation,
    ModOperation,
)
from .io import TellOperation, PrintnOperation, PrintOperation, PrintiOperation, YesQuestionOp, ReadOp, LexOp
from .object_ops import (
    MoveOperation,
    FsetOperation,
    FclearOperation,
    GetpOperation,
    PutpOperation,
    LocOperation,
    RemoveOperation,
    HeldOperation,
    MapContentsOperation,
)
from .variables import SetOperation, SetgOperation
from .logic import AndOperation, OrOperation, NotOperation
from .string_ops import ConcatOperation, SubstringOperation, PrintcOperation
from .list_ops import (
    LengthOperation,
    NthOperation,
    RestOperation,
    FirstListOperation,
    NextOperation,
    BackOperation,
    EmptyCheckOperation,
    MemqOperation,
)
from .table_ops import (
    LtableOperation,
    ItableOperation,
    TableOperation,
)
from .table_access import GetOp, PutOp, GetBOp, PutBOp
from .control_io import (
    PerformOperation,
    ApplyOperation,
    GotoOperation,
    RandomOperation,
    PrintdOperation,
    CrlfOperation,
)
from .comparison_objects import (
    NextQuestionOperation,
    GetptOperation,
    PtsizeOperation,
)
from .bit_ops import (
    BandOperation,
    BorOperation,
    BtstOperation,
    BcomOperation,
    MapretOperation,
)
from .advanced import (
    PrimtypeOperation,
    PrintbOperation,
    IgrtrQuestionOperation,
    AgainOperation,
    TypeQuestionOperation,
    ValueOperation,
    AgainException,
)
from .game_logic import (
    MetaLocOp,
    LitOp,
    AccessibleOp,
    JigsUpOp,
)


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
    registry.register(DlessOperation())

    # Control
    registry.register(CondOperation())
    registry.register(RtrueOperation())
    registry.register(RfalseOperation())
    registry.register(ReturnOperation())
    registry.register(RepeatOperation())
    registry.register(MapfOperation())
    registry.register(ProgOperation())
    registry.register(DoOperation())
    registry.register(QuitOperation())

    # Arithmetic
    registry.register(AddOperation())
    registry.register(SubtractOperation())
    registry.register(MultiplyOperation())
    registry.register(DivideOperation())
    registry.register(ModOperation())

    # I/O
    registry.register(TellOperation())
    registry.register(PrintnOperation())
    registry.register(PrintOperation())
    registry.register(PrintiOperation())
    registry.register(YesQuestionOp())
    registry.register(ReadOp())
    registry.register(LexOp())

    # Object Operations
    registry.register(MoveOperation())
    registry.register(FsetOperation())
    registry.register(FclearOperation())
    registry.register(GetpOperation())
    registry.register(PutpOperation())
    registry.register(LocOperation())
    registry.register(RemoveOperation())
    registry.register(HeldOperation())
    registry.register(MapContentsOperation())

    # Variables
    registry.register(SetOperation())
    registry.register(SetgOperation())

    # String Operations
    registry.register(ConcatOperation())
    registry.register(SubstringOperation())
    registry.register(PrintcOperation())

    # List Operations
    registry.register(LengthOperation())
    registry.register(NthOperation())
    registry.register(RestOperation())
    registry.register(FirstListOperation())
    registry.register(NextOperation())
    registry.register(BackOperation())
    registry.register(EmptyCheckOperation())
    registry.register(MemqOperation())

    # Table Operations (NEW: using TableData)
    registry.register(GetOp())
    registry.register(PutOp())
    registry.register(GetBOp())
    registry.register(PutBOp())
    # Table creation operations (still use old implementation)
    registry.register(LtableOperation())
    registry.register(ItableOperation())
    registry.register(TableOperation())

    # Control Flow + I/O Operations
    registry.register(PerformOperation())
    registry.register(ApplyOperation())
    registry.register(GotoOperation())
    registry.register(RandomOperation())
    registry.register(PrintdOperation())
    registry.register(CrlfOperation())

    # Comparison + Object Operations
    registry.register(NextQuestionOperation())
    registry.register(GetptOperation())
    registry.register(PtsizeOperation())

    # Bit Operations
    registry.register(BandOperation())
    registry.register(BorOperation())
    registry.register(BtstOperation())
    registry.register(BcomOperation())
    registry.register(MapretOperation())

    # Advanced Operations
    registry.register(PrimtypeOperation())
    registry.register(PrintbOperation())
    registry.register(IgrtrQuestionOperation())
    registry.register(AgainOperation())
    registry.register(TypeQuestionOperation())
    registry.register(ValueOperation())

    # Game Logic Operations
    registry.register(MetaLocOp())
    registry.register(LitOp())
    registry.register(AccessibleOp())
    registry.register(JigsUpOp())

    return registry


__all__ = ['Operation', 'OperationRegistry', 'create_default_registry']
