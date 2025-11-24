import pytest
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject, ObjectFlag
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_evaluate_atom():
    """Test evaluating an atom (variable lookup)."""
    world = WorldState()
    world.set_global("TEST-VAR", 42)

    evaluator = Evaluator(world)
    result = evaluator.evaluate(Atom("TEST-VAR"))
    assert result == 42


def test_evaluate_string():
    """Test evaluating a string literal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(String("hello"))
    assert result == "hello"


def test_evaluate_number():
    """Test evaluating a number literal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Number(42))
    assert result == 42


def test_evaluate_equal():
    """Test EQUAL? form."""
    world = WorldState()
    evaluator = Evaluator(world)

    form = Form(operator=Atom("EQUAL?"), args=[Number(5), Number(5)])
    assert evaluator.evaluate(form) is True

    form2 = Form(operator=Atom("EQUAL?"), args=[Number(5), Number(3)])
    assert evaluator.evaluate(form2) is False


def test_evaluate_fset_check():
    """Test FSET? form (flag check)."""
    world = WorldState()
    door = GameObject(name="DOOR")
    door.set_flag(ObjectFlag.OPEN)
    world.add_object(door)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("FSET?"), args=[Atom("DOOR"), Atom("OPENBIT")])
    assert evaluator.evaluate(form) is True


def test_evaluate_cond():
    """Test COND form (conditional)."""
    world = WorldState()
    evaluator = Evaluator(world)

    # <COND (<EQUAL? 1 1> 42)>
    form = Form(
        operator=Atom("COND"),
        args=[
            [Form(operator=Atom("EQUAL?"), args=[Number(1), Number(1)]), Number(42)]
        ]
    )
    result = evaluator.evaluate(form)
    assert result == 42


def test_evaluate_verb_check():
    """Test VERB? form."""
    world = WorldState()
    world.set_parser_state(verb="TAKE")

    evaluator = Evaluator(world)

    form = Form(operator=Atom("VERB?"), args=[Atom("TAKE")])
    assert evaluator.evaluate(form) is True

    form2 = Form(operator=Atom("VERB?"), args=[Atom("DROP")])
    assert evaluator.evaluate(form2) is False


def test_evaluate_tell():
    """Test TELL form outputs text to buffer."""
    world = WorldState()
    output = OutputBuffer()
    evaluator = Evaluator(world, output)

    form = Form(operator=Atom("TELL"), args=[String("Hello, world!")])
    evaluator.evaluate(form)

    assert "Hello, world!" in output.get_output()


def test_evaluate_tell_with_crlf():
    """Test TELL with CR (carriage return)."""
    world = WorldState()
    output = OutputBuffer()
    evaluator = Evaluator(world, output)

    form = Form(operator=Atom("TELL"), args=[String("Line 1"), Atom("CR"), String("Line 2")])
    evaluator.evaluate(form)

    result = output.get_output()
    assert "Line 1" in result
    assert "Line 2" in result
