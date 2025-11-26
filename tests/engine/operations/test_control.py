"""Tests for control flow operations."""

import pytest
from zil_interpreter.engine.evaluator import Evaluator, ReturnValue
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number
from zil_interpreter.engine.operations.control import ProgOperation
from zil_interpreter.runtime.output_buffer import OutputBuffer


# RETURN Operation Tests
def test_return_with_value():
    """RETURN with value raises ReturnValue exception."""
    world = WorldState()
    evaluator = Evaluator(world)

    with pytest.raises(ReturnValue) as exc_info:
        evaluator.evaluate(Form(Atom("RETURN"), [Number(42)]))

    assert exc_info.value.value == 42


def test_return_no_args():
    """RETURN with no args returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    with pytest.raises(ReturnValue) as exc_info:
        evaluator.evaluate(Form(Atom("RETURN"), []))

    assert exc_info.value.value is None


def test_return_evaluates_arg():
    """RETURN evaluates its argument."""
    world = WorldState()
    evaluator = Evaluator(world)

    with pytest.raises(ReturnValue) as exc_info:
        evaluator.evaluate(
            Form(Atom("RETURN"), [Form(Atom("+"), [Number(2), Number(3)])])
        )

    assert exc_info.value.value == 5


# REPEAT Operation Tests
def test_repeat_basic():
    """REPEAT executes body expressions."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Simple repeat with body
    result = evaluator.evaluate(
        Form(Atom("REPEAT"), [
            [],  # Empty loop spec
            Form(Atom("+"), [Number(1), Number(2)])
        ])
    )

    assert result == 3


def test_repeat_empty():
    """REPEAT with no args returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("REPEAT"), []))
    assert result is None


def test_repeat_multiple_body_expressions():
    """REPEAT evaluates multiple body expressions."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("REPEAT"), [
            [],
            Number(1),
            Number(2),
            Number(3)
        ])
    )

    # Returns last evaluated expression
    assert result == 3


# MAPF Operation Tests
def test_mapf_empty_collection():
    """MAPF with empty collection returns empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MAPF"), [Atom("SOME-FUNC"), []])
    )

    assert result == []


def test_mapf_no_args():
    """MAPF with insufficient args returns empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("MAPF"), []))
    assert result == []


def test_mapf_non_list():
    """MAPF with non-list returns empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MAPF"), [Atom("FUNC"), Number(42)])
    )

    assert result == []


# PROG Operation Tests
class TestProgOperation:
    """Tests for PROG operation."""

    def test_prog_name(self):
        """Operation has correct name."""
        op = ProgOperation()
        assert op.name == "PROG"

    def test_prog_executes_body(self):
        """PROG executes body expressions in sequence."""
        world = WorldState()
        output = OutputBuffer()

        op = ProgOperation()

        class MockEvaluator:
            def __init__(self):
                self.world = world
                self.output = output
                self.results = []

            def evaluate(self, arg):
                self.results.append(arg)
                return arg

        evaluator = MockEvaluator()
        # PROG with empty bindings and body of [1, 2, 3]
        result = op.execute([[], 1, 2, 3], evaluator)
        assert evaluator.results == [[], 1, 2, 3]

    def test_prog_returns_last_value(self):
        """PROG returns value of last expression."""
        op = ProgOperation()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg * 2 if isinstance(arg, int) else arg

        evaluator = MockEvaluator()
        result = op.execute([[], 5], evaluator)
        assert result == 10
