from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number


# Subtraction Operation Tests
def test_subtract_binary():
    """Subtraction with two numbers."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("-"), [Number(10), Number(3)])
    )
    assert result == 7


def test_subtract_multiple():
    """Subtraction with multiple numbers."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("-"), [Number(100), Number(20), Number(30)])
    )
    assert result == 50


def test_subtract_unary_negation():
    """Unary negation (single argument)."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("-"), [Number(42)])
    )
    assert result == -42


def test_subtract_empty():
    """Subtraction with no arguments returns 0."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("-"), []))
    assert result == 0


# Multiplication Operation Tests
def test_multiply_two_numbers():
    """Multiplication with two numbers."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("*"), [Number(6), Number(7)])
    )
    assert result == 42


def test_multiply_multiple():
    """Multiplication with multiple numbers."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("*"), [Number(2), Number(3), Number(4)])
    )
    assert result == 24


def test_multiply_by_zero():
    """Multiplication by zero returns zero."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("*"), [Number(42), Number(0)])
    )
    assert result == 0


def test_multiply_empty():
    """Multiplication with no arguments returns 1 (identity)."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("*"), []))
    assert result == 1


# Division Operation Tests
def test_divide_basic():
    """Division with two numbers."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("/"), [Number(20), Number(4)])
    )
    assert result == 5


def test_divide_integer_division():
    """Division performs integer division (truncates)."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("/"), [Number(7), Number(2)])
    )
    assert result == 3  # Integer division


def test_divide_multiple():
    """Division with multiple numbers (successive division)."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("/"), [Number(100), Number(5), Number(2)])
    )
    assert result == 10  # 100 / 5 / 2 = 20 / 2 = 10


def test_divide_by_one():
    """Division by one returns original value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("/"), [Number(42), Number(1)])
    )
    assert result == 42


def test_divide_empty():
    """Division with no arguments returns 0."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("/"), []))
    assert result == 0


# Modulo Operation Tests
def test_mod_basic():
    """MOD returns remainder of division."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MOD"), [Number(10), Number(3)])
    )
    assert result == 1


def test_mod_even_division():
    """MOD returns 0 when evenly divisible."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MOD"), [Number(10), Number(5)])
    )
    assert result == 0


def test_mod_larger_divisor():
    """MOD with larger divisor returns dividend."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MOD"), [Number(5), Number(10)])
    )
    assert result == 5


def test_mod_single_argument():
    """MOD with one argument returns the number."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MOD"), [Number(42)])
    )
    assert result == 42


def test_mod_empty():
    """MOD with no arguments returns 0."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("MOD"), []))
    assert result == 0
