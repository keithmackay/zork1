import pytest
from zil_interpreter.engine.game_engine import GameEngine
from zil_interpreter.parser.ast_nodes import Routine, Form, Atom, String
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_game_engine_initialization():
    """Test GameEngine initializes components."""
    world = WorldState()
    output = OutputBuffer()
    engine = GameEngine(world, output)

    assert engine.world is world
    assert engine.output is output
    assert engine.parser is not None
    assert engine.executor is not None


def test_game_engine_execute_command():
    """Test executing a simple command."""
    world = WorldState()
    output = OutputBuffer()
    engine = GameEngine(world, output)

    # Register a LOOK routine
    look_routine = Routine(
        name="V-LOOK",
        args=[],
        body=[Form(operator=Atom("TELL"), args=[String("You look around.")])]
    )
    engine.executor.register_routine(look_routine)

    # Execute "look" command
    engine.execute_command("look")

    assert "You look around." in output.get_output()


def test_game_engine_sets_parser_state():
    """Test engine sets PRSA, PRSO, PRSI."""
    world = WorldState()
    output = OutputBuffer()
    engine = GameEngine(world, output)

    lamp = GameObject(name="LAMP", synonyms=["LAMP"])
    world.add_object(lamp)

    # Register TAKE routine
    take_routine = Routine(
        name="V-TAKE",
        args=[],
        body=[Form(operator=Atom("TELL"), args=[String("Taken.")])]
    )
    engine.executor.register_routine(take_routine)

    # Execute "take lamp"
    engine.execute_command("take lamp")

    assert world.get_global("PRSA") == "V-TAKE"
    assert world.get_global("PRSO") == lamp
