"""Test that TELL routine output appears correctly."""

from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_tell_routine_produces_output():
    """Test that V-LOOK routine using TELL writes to output buffer."""
    # Create single output buffer
    output = OutputBuffer()

    # Load world with shared buffer
    loader = WorldLoader()
    world, executor = loader.load_world(
        Path('tests/fixtures/simple_game.zil'),
        output
    )

    # Call V-LOOK routine which uses <TELL "You are in a small room." CR>
    executor.call_routine('V-LOOK', [])

    # Get output from the shared buffer
    result = output.flush()

    # Verify output contains the TELL text
    assert "You are in a small room" in result
    assert result == "You are in a small room.\n"


def test_multiple_tell_calls_accumulate():
    """Test that multiple TELL calls accumulate in buffer."""
    output = OutputBuffer()

    loader = WorldLoader()
    world, executor = loader.load_world(
        Path('tests/fixtures/simple_game.zil'),
        output
    )

    # Call multiple routines
    executor.call_routine('V-LOOK', [])
    executor.call_routine('V-INVENTORY', [])

    result = output.flush()

    # Both outputs should be present
    assert "You are in a small room" in result
    assert "You are carrying nothing" in result
