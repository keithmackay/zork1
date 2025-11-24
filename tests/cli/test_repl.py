import pytest
from io import StringIO
from unittest.mock import Mock, patch
from zil_interpreter.cli.repl import REPL
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Routine, Form, Atom, String


def test_create_repl():
    """Test creating a REPL instance."""
    world = WorldState()
    repl = REPL(world)
    assert repl.world == world


def test_repl_welcome_message():
    """Test REPL displays welcome message."""
    world = WorldState()
    repl = REPL(world)

    output = StringIO()
    with patch('sys.stdout', output):
        repl.display_welcome()

    result = output.getvalue()
    assert "ZIL Interpreter" in result


def test_repl_prompt():
    """Test REPL prompt."""
    world = WorldState()
    repl = REPL(world)

    assert repl.get_prompt() == "> "


def test_process_quit_command():
    """Test processing quit command."""
    world = WorldState()
    repl = REPL(world)

    assert repl.should_quit("quit") is True
    assert repl.should_quit("exit") is True
    assert repl.should_quit("q") is True
    assert repl.should_quit("take lamp") is False


def test_repl_executes_commands():
    """Test REPL executes commands through game engine."""
    world = WorldState()
    repl = REPL(world)

    # Register a test routine
    routine = Routine(
        name="V-LOOK",
        args=[],
        body=[Form(operator=Atom("TELL"), args=[String("Test output")])]
    )
    repl.engine.executor.register_routine(routine)

    # Capture output
    output = StringIO()
    with patch('sys.stdout', output):
        repl.process_command("look")

    result = output.getvalue()
    assert "Test output" in result
