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


def test_evaluate_move():
    """Test MOVE form changes object location."""
    world = WorldState()

    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)
    player = GameObject(name="PLAYER")

    world.add_object(room)
    world.add_object(lamp)
    world.add_object(player)

    evaluator = Evaluator(world)

    # Move lamp to player
    form = Form(operator=Atom("MOVE"), args=[Atom("LAMP"), Atom("PLAYER")])
    evaluator.evaluate(form)

    assert lamp.parent == player
    assert lamp in player.children


def test_evaluate_fset():
    """Test FSET form sets object flags."""
    world = WorldState()
    door = GameObject(name="DOOR")
    world.add_object(door)

    evaluator = Evaluator(world)

    assert not door.has_flag(ObjectFlag.OPEN)

    form = Form(operator=Atom("FSET"), args=[Atom("DOOR"), Atom("OPENBIT")])
    evaluator.evaluate(form)

    assert door.has_flag(ObjectFlag.OPEN)


def test_evaluate_fclear():
    """Test FCLEAR form clears object flags."""
    world = WorldState()
    door = GameObject(name="DOOR")
    door.set_flag(ObjectFlag.OPEN)
    world.add_object(door)

    evaluator = Evaluator(world)

    assert door.has_flag(ObjectFlag.OPEN)

    form = Form(operator=Atom("FCLEAR"), args=[Atom("DOOR"), Atom("OPENBIT")])
    evaluator.evaluate(form)

    assert not door.has_flag(ObjectFlag.OPEN)


def test_evaluate_getp():
    """Test GETP form reads object properties."""
    world = WorldState()
    chest = GameObject(name="CHEST")
    chest.set_property("SIZE", 20)
    chest.set_property("CAPACITY", 100)
    world.add_object(chest)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("GETP"), args=[Atom("CHEST"), Atom("SIZE")])
    result = evaluator.evaluate(form)

    assert result == 20


def test_evaluate_putp():
    """Test PUTP form sets object properties."""
    world = WorldState()
    chest = GameObject(name="CHEST")
    world.add_object(chest)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("PUTP"), args=[Atom("CHEST"), Atom("SIZE"), Number(30)])
    evaluator.evaluate(form)

    assert chest.get_property("SIZE") == 30


def test_evaluate_in_predicate():
    """Test IN? form checks object containment."""
    world = WorldState()

    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)
    player = GameObject(name="PLAYER")

    world.add_object(room)
    world.add_object(lamp)
    world.add_object(player)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("IN?"), args=[Atom("LAMP"), Atom("ROOM")])
    assert evaluator.evaluate(form) is True

    form2 = Form(operator=Atom("IN?"), args=[Atom("LAMP"), Atom("PLAYER")])
    assert evaluator.evaluate(form2) is False


def test_evaluate_first_predicate():
    """Test FIRST? form returns first child object."""
    world = WorldState()

    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)
    sword = GameObject(name="SWORD", parent=room)

    world.add_object(room)
    world.add_object(lamp)
    world.add_object(sword)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("FIRST?"), args=[Atom("ROOM")])
    result = evaluator.evaluate(form)

    # Should return one of the children (as GameObject)
    assert result in [lamp, sword]
