import pytest
from zil_interpreter.engine.command_parser import CommandParser
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject


def test_parse_simple_command():
    """Test parsing simple one-word command."""
    world = WorldState()
    parser = CommandParser(world)

    result = parser.parse("look")

    assert result is not None
    assert result['verb'] == 'LOOK'
    assert result['direct_object'] is None
    assert result['indirect_object'] is None


def test_parse_verb_object():
    """Test parsing verb with direct object."""
    world = WorldState()
    lamp = GameObject(name="LAMP", synonyms=["LAMP", "LANTERN"])
    world.add_object(lamp)

    parser = CommandParser(world)
    result = parser.parse("take lamp")

    assert result is not None
    assert result['verb'] == 'TAKE'
    assert result['direct_object'] == 'LAMP'
    assert result['indirect_object'] is None


def test_parse_verb_two_objects():
    """Test parsing verb with direct and indirect objects."""
    world = WorldState()
    lamp = GameObject(name="LAMP", synonyms=["LAMP", "LANTERN"])
    box = GameObject(name="BOX", synonyms=["BOX", "CONTAINER"])
    world.add_object(lamp)
    world.add_object(box)

    parser = CommandParser(world)
    result = parser.parse("put lamp in box")

    assert result is not None
    assert result['verb'] == 'PUT'
    assert result['direct_object'] == 'LAMP'
    assert result['indirect_object'] == 'BOX'
