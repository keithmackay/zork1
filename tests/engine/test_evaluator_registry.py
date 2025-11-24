# tests/engine/test_evaluator_registry.py
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number

class TestOperation(Operation):
    @property
    def name(self) -> str:
        return "TEST-OP"

    def execute(self, args: list, evaluator) -> int:
        return 999

def test_evaluator_uses_registry():
    """Evaluator should check registry for operations."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Register test operation
    evaluator.registry.register(TestOperation())

    # Evaluate form using test operation
    result = evaluator.evaluate(Form(Atom("TEST-OP"), []))
    assert result == 999
