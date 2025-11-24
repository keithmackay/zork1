import pytest
from io import StringIO
from unittest.mock import Mock, patch
from zil_interpreter.cli.repl import REPL
from zil_interpreter.world.world_state import WorldState


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
