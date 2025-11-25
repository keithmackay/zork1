"""Integration tests for loading and playing a simple game."""

from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_simple_game_integration():
    """Test loading and playing a simple game."""
    loader = WorldLoader()
    output = OutputBuffer()
    test_file = Path(__file__).parent.parent / "fixtures" / "simple_game.zil"

    world, executor = loader.load_world(test_file, output)

    # Verify world loaded
    assert world.get_global("SCORE") == 0
    assert "ROOM" in world.objects
    assert "LAMP" in world.objects

    # Verify routines loaded
    assert "V-LOOK" in executor.routines
    assert "V-TAKE" in executor.routines
    assert "V-INVENTORY" in executor.routines

    # Verify LAMP object properties
    lamp = world.get_object("LAMP")
    assert lamp is not None
    assert lamp.description == "brass lamp"
    assert "LAMP" in lamp.synonyms
    assert "LANTERN" in lamp.synonyms
