from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number


# AND Operation Tests
def test_and_all_true():
    """AND with all true values returns last value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("AND"), [Number(1), Number(2), Number(3)])
    )
    assert result == 3


def test_and_with_false():
    """AND with false value returns first false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("AND"), [Number(1), Number(0), Number(3)])
    )
    assert result == 0


def test_and_empty():
    """AND with no arguments returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("AND"), []))
    assert result is False


def test_and_short_circuit():
    """AND should short-circuit on first false value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("AND"), [Number(5), Number(0), Number(10)])
    )
    # Should return 0 (first false), not evaluate beyond
    assert result == 0


# OR Operation Tests
def test_or_with_true():
    """OR returns first true value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("OR"), [Number(0), Number(2), Number(3)])
    )
    assert result == 2


def test_or_all_false():
    """OR with all false returns last value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("OR"), [Number(0), Number(0), Number(0)])
    )
    assert result == 0


def test_or_empty():
    """OR with no arguments returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("OR"), []))
    assert result is False


def test_or_short_circuit():
    """OR should short-circuit on first true value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("OR"), [Number(0), Number(5), Number(10)])
    )
    # Should return 5 (first true), not evaluate beyond
    assert result == 5


# NOT Operation Tests
def test_not_true():
    """NOT true returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("NOT"), [Number(1)]))
    assert result is False


def test_not_false():
    """NOT false returns true."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("NOT"), [Number(0)]))
    assert result is True


def test_not_empty():
    """NOT with no arguments returns true."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("NOT"), []))
    assert result is True


def test_not_nonzero():
    """NOT with nonzero value returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("NOT"), [Number(42)]))
    assert result is False
