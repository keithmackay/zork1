from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String


# CONCAT Operation Tests
def test_concat_two_strings():
    """CONCAT concatenates two strings."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("CONCAT"), [String("Hello"), String(" World")])
    )
    assert result == "Hello World"


def test_concat_multiple_strings():
    """CONCAT concatenates multiple strings."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("CONCAT"), [String("Hello"), String(" "), String("World"), String("!")])
    )
    assert result == "Hello World!"


def test_concat_with_numbers():
    """CONCAT converts numbers to strings."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("CONCAT"), [String("Count: "), Number(42)])
    )
    assert result == "Count: 42"


def test_concat_empty():
    """CONCAT with no arguments returns empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("CONCAT"), []))
    assert result == ""


def test_concat_single_string():
    """CONCAT with single string returns that string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("CONCAT"), [String("Hello")])
    )
    assert result == "Hello"


# SUBSTRING Operation Tests
def test_substring_basic():
    """SUBSTRING extracts substring from start to end."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("SUBSTRING"), [String("Hello World"), Number(0), Number(5)])
    )
    assert result == "Hello"


def test_substring_middle():
    """SUBSTRING extracts from middle of string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("SUBSTRING"), [String("Hello World"), Number(6), Number(11)])
    )
    assert result == "World"


def test_substring_single_char():
    """SUBSTRING can extract single character."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("SUBSTRING"), [String("Hello"), Number(1), Number(2)])
    )
    assert result == "e"


def test_substring_to_end():
    """SUBSTRING with end beyond length goes to end."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("SUBSTRING"), [String("Hello"), Number(2), Number(100)])
    )
    assert result == "llo"


def test_substring_negative_start():
    """SUBSTRING with negative start returns empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("SUBSTRING"), [String("Hello"), Number(-1), Number(5)])
    )
    assert result == ""


def test_substring_start_after_end():
    """SUBSTRING with start after end returns empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("SUBSTRING"), [String("Hello"), Number(3), Number(1)])
    )
    assert result == ""


def test_substring_insufficient_args():
    """SUBSTRING with insufficient args returns empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("SUBSTRING"), [String("Hello")])
    )
    assert result == ""


# PRINTC Operation Tests
def test_printc_ascii_char():
    """PRINTC prints ASCII character and returns it."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("PRINTC"), [Number(65)])  # ASCII 'A'
    )

    # Check output buffer
    output = evaluator.output.get_output()
    assert "A" in output

    # PRINTC returns the character
    assert result == "A"


def test_printc_lowercase():
    """PRINTC prints lowercase character."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("PRINTC"), [Number(97)])  # ASCII 'a'
    )

    output = evaluator.output.get_output()
    assert "a" in output
    assert result == "a"


def test_printc_space():
    """PRINTC prints space character."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("PRINTC"), [Number(32)])  # ASCII space
    )

    output = evaluator.output.get_output()
    assert " " in output
    assert result == " "


def test_printc_newline():
    """PRINTC prints newline character."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("PRINTC"), [Number(10)])  # ASCII newline
    )

    output = evaluator.output.get_output()
    assert "\n" in output
    assert result == "\n"


def test_printc_no_args():
    """PRINTC with no arguments returns empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("PRINTC"), []))
    assert result == ""


def test_printc_invalid_char_code():
    """PRINTC with invalid character code returns empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Test with a very large number
    result = evaluator.evaluate(
        Form(Atom("PRINTC"), [Number(999999)])
    )
    assert result == ""
