from zil_interpreter.engine.operations.base import Operation, OperationRegistry

class MockOperation(Operation):
    @property
    def name(self) -> str:
        return "MOCK"

    def execute(self, args: list, evaluator) -> int:
        return 42

def test_registry_register():
    registry = OperationRegistry()
    op = MockOperation()
    registry.register(op)
    assert registry.has("MOCK")

def test_registry_get():
    registry = OperationRegistry()
    op = MockOperation()
    registry.register(op)
    retrieved = registry.get("MOCK")
    assert retrieved == op

def test_registry_case_insensitive():
    registry = OperationRegistry()
    op = MockOperation()
    registry.register(op)
    assert registry.get("mock") == op
    assert registry.get("Mock") == op
    assert registry.get("MOCK") == op

def test_table_operations_registered():
    """Table operations are registered."""
    from zil_interpreter.engine.operations import create_default_registry
    registry = create_default_registry()
    assert registry.get("GET") is not None
    assert registry.get("PUT") is not None
    assert registry.get("GETB") is not None
    assert registry.get("PUTB") is not None

def test_game_logic_operations_registered():
    """Game logic operations are registered."""
    from zil_interpreter.engine.operations import create_default_registry
    registry = create_default_registry()
    assert registry.get("META-LOC") is not None
    assert registry.get("LIT?") is not None
    assert registry.get("ACCESSIBLE?") is not None

def test_batch5_operations_registered():
    """Batch 5 operations are registered."""
    from zil_interpreter.engine.operations import create_default_registry
    registry = create_default_registry()
    assert registry.get("PROG") is not None
    assert registry.get("DO") is not None
    assert registry.get("MAP-CONTENTS") is not None
    assert registry.get("JIGS-UP") is not None
    assert registry.get("YES?") is not None
    assert registry.get("QUIT") is not None

def test_batch6_operations_registered():
    """Batch 6 operations are registered."""
    from zil_interpreter.engine.operations import create_default_registry
    registry = create_default_registry()
    assert registry.get("QUEUE") is not None
    assert registry.get("ENABLE") is not None
    assert registry.get("DISABLE") is not None
    assert registry.get("INT") is not None
    assert registry.get("DEQUEUE") is not None
    assert registry.get("READ") is not None
    assert registry.get("LEX") is not None
    assert registry.get("WORD?") is not None
