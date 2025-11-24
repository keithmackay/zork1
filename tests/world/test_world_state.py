import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject


def test_create_empty_world():
    """Test creating an empty world state."""
    world = WorldState()
    assert len(world.objects) == 0
    # World initializes with parser state globals (PRSA, PRSO, PRSI)
    assert "PRSA" in world.globals
    assert "PRSO" in world.globals
    assert "PRSI" in world.globals


def test_add_object_to_world():
    """Test adding objects to world state."""
    world = WorldState()
    lamp = GameObject(name="LAMP")

    world.add_object(lamp)
    assert "LAMP" in world.objects
    assert world.get_object("LAMP") == lamp


def test_find_object_by_synonym():
    """Test finding object by synonym."""
    world = WorldState()
    lamp = GameObject(name="LAMP", synonyms=["LAMP", "LANTERN"])
    world.add_object(lamp)

    result = world.find_object_by_word("LANTERN")
    assert result == lamp


def test_global_variables():
    """Test getting and setting global variables."""
    world = WorldState()

    world.set_global("SCORE", 0)
    world.set_global("MOVES", 1)

    assert world.get_global("SCORE") == 0
    assert world.get_global("MOVES") == 1
    assert world.get_global("NONEXISTENT") is None


def test_parser_state():
    """Test parser state variables (PRSA, PRSO, PRSI)."""
    world = WorldState()

    world.set_parser_state(verb="TAKE", direct_obj="LAMP", indirect_obj=None)

    assert world.get_global("PRSA") == "TAKE"
    assert world.get_global("PRSO") == "LAMP"
    assert world.get_global("PRSI") is None


def test_current_room():
    """Test getting and setting current room."""
    world = WorldState()
    room = GameObject(name="WEST-OF-HOUSE")
    world.add_object(room)

    world.set_current_room(room)
    assert world.get_current_room() == room
