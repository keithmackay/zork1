"""Integration test for CLI TELL output."""

import json
from pathlib import Path
from zil_interpreter.cli.game_cli import GameCLI


def test_cli_look_command_shows_output():
    """Test that 'look' command shows TELL output in JSON mode."""
    cli = GameCLI(Path('tests/fixtures/simple_game.zil'), json_mode=True)

    # Load game
    assert cli.load_game() is True

    # Execute command directly through engine (doesn't flush buffer)
    cli.engine.execute_command("look")

    # Get output from buffer
    output = cli.output_buffer.flush()

    # Should contain the TELL text from V-LOOK
    assert "You are in a small room" in output


def test_cli_initial_state_shows_output():
    """Test that initial game state executes look and shows output."""
    cli = GameCLI(Path('tests/fixtures/simple_game.zil'), json_mode=True)

    # Load game (triggers _display_initial_state)
    assert cli.load_game() is True

    # Execute command directly through engine to test buffer sharing
    cli.engine.execute_command("look")
    output = cli.output_buffer.flush()

    # Verify TELL output appears (confirms buffer sharing works)
    assert "You are in a small room" in output
