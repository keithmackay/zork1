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
