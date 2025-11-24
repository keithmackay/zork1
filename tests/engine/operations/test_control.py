"""Tests for control flow operations."""

import pytest
from zil_interpreter.engine.evaluator import Evaluator, ReturnValue
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number


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
