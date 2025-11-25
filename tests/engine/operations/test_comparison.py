from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number


# LessThan Operation Tests (< and L?)
def test_less_than_true():
    """< returns true when first value is less than second."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("<"), [Number(3), Number(5)])
    )
    assert result is True


def test_less_than_false():
    """< returns false when first value is not less than second."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("<"), [Number(5), Number(3)])
    )
    assert result is False


def test_less_than_equal_values():
    """< returns false when values are equal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("<"), [Number(5), Number(5)])
    )
    assert result is False


def test_less_than_alias_l():
    """L? is an alias for <."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("L?"), [Number(3), Number(5)])
    )
    assert result is True


def test_less_than_insufficient_args():
    """< with insufficient args returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("<"), [Number(5)]))
    assert result is False


# GreaterThan Operation Tests (> and G?)
def test_greater_than_true():
    """> returns true when first value is greater than second."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom(">"), [Number(5), Number(3)])
    )
    assert result is True


def test_greater_than_false():
    """> returns false when first value is not greater than second."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom(">"), [Number(3), Number(5)])
    )
    assert result is False


def test_greater_than_equal_values():
    """> returns false when values are equal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom(">"), [Number(5), Number(5)])
    )
    assert result is False


def test_greater_than_alias_g():
    """G? is an alias for >."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("G?"), [Number(5), Number(3)])
    )
    assert result is True


def test_greater_than_insufficient_args():
    """> with insufficient args returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom(">"), [Number(5)]))
    assert result is False


# LessEqual Operation Tests (<=)
def test_less_equal_less_than():
    """<= returns true when first value is less than second."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("<="), [Number(3), Number(5)])
    )
    assert result is True


def test_less_equal_equal():
    """<= returns true when values are equal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("<="), [Number(5), Number(5)])
    )
    assert result is True


def test_less_equal_greater():
    """<= returns false when first value is greater."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("<="), [Number(5), Number(3)])
    )
    assert result is False


def test_less_equal_insufficient_args():
    """<= with insufficient args returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("<="), [Number(5)]))
    assert result is False


# GreaterEqual Operation Tests (>=)
def test_greater_equal_greater_than():
    """>= returns true when first value is greater than second."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom(">="), [Number(5), Number(3)])
    )
    assert result is True


def test_greater_equal_equal():
    """>= returns true when values are equal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom(">="), [Number(5), Number(5)])
    )
    assert result is True


def test_greater_equal_less():
    """>= returns false when first value is less."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom(">="), [Number(3), Number(5)])
    )
    assert result is False


def test_greater_equal_insufficient_args():
    """>= with insufficient args returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom(">="), [Number(5)]))
    assert result is False


# ZeroCheck Operation Tests (ZERO?)
def test_zero_check_true():
    """ZERO? returns true for zero."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("ZERO?"), [Number(0)])
    )
    assert result is True


def test_zero_check_false_positive():
    """ZERO? returns false for positive number."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("ZERO?"), [Number(42)])
    )
    assert result is False


def test_zero_check_false_negative():
    """ZERO? returns false for negative number."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("ZERO?"), [Number(-5)])
    )
    assert result is False


def test_zero_check_no_args():
    """ZERO? with no arguments returns true."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("ZERO?"), []))
    assert result is True


# NumericEqual Operation Tests (==)
def test_numeric_equal_true():
    """== returns true when values are numerically equal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("=="), [Number(5), Number(5)])
    )
    assert result is True


def test_numeric_equal_false():
    """== returns false when values are not equal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("=="), [Number(5), Number(3)])
    )
    assert result is False


def test_numeric_equal_multiple_values():
    """== with multiple values checks if all are equal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("=="), [Number(5), Number(5), Number(5)])
    )
    assert result is True


def test_numeric_equal_multiple_values_false():
    """== with multiple values returns false if any differ."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("=="), [Number(5), Number(5), Number(3)])
    )
    assert result is False


def test_numeric_equal_insufficient_args():
    """== with insufficient args returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("=="), [Number(5)]))
    assert result is False


# DlessOperation Tests (DLESS?)
def test_dless_decrements_and_returns_true():
    """DLESS? decrements global and returns true if result < test value."""
    world = WorldState()
    world.set_global("COUNTER", 5)
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("DLESS?"), [Atom("COUNTER"), Number(5)])
    )
    # COUNTER was 5, now 4, and 4 < 5
    assert result is True
    assert world.get_global("COUNTER") == 4


def test_dless_decrements_and_returns_false():
    """DLESS? decrements global and returns false if result >= test value."""
    world = WorldState()
    world.set_global("COUNTER", 5)
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("DLESS?"), [Atom("COUNTER"), Number(3)])
    )
    # COUNTER was 5, now 4, and 4 is NOT < 3
    assert result is False
    assert world.get_global("COUNTER") == 4


def test_dless_equal_after_decrement():
    """DLESS? returns false when decremented value equals test value."""
    world = WorldState()
    world.set_global("COUNTER", 6)
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("DLESS?"), [Atom("COUNTER"), Number(5)])
    )
    # COUNTER was 6, now 5, and 5 is NOT < 5
    assert result is False
    assert world.get_global("COUNTER") == 5


def test_dless_insufficient_args():
    """DLESS? with insufficient args returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("DLESS?"), [Atom("COUNTER")]))
    assert result is False
