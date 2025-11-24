import pytest
from zil_interpreter.world.game_object import GameObject, ObjectFlag


def test_create_simple_object():
    """Test creating a basic game object."""
    lamp = GameObject(name="LAMP", description="brass lamp")
    assert lamp.name == "LAMP"
    assert lamp.description == "brass lamp"


def test_object_properties():
    """Test setting and getting object properties."""
    obj = GameObject(name="CHEST")
    obj.set_property("SIZE", 20)
    obj.set_property("CAPACITY", 100)

    assert obj.get_property("SIZE") == 20
    assert obj.get_property("CAPACITY") == 100
    assert obj.get_property("NONEXISTENT") is None


def test_object_flags():
    """Test setting and checking object flags."""
    obj = GameObject(name="DOOR")

    assert not obj.has_flag(ObjectFlag.OPEN)
    obj.set_flag(ObjectFlag.OPEN)
    assert obj.has_flag(ObjectFlag.OPEN)

    obj.clear_flag(ObjectFlag.OPEN)
    assert not obj.has_flag(ObjectFlag.OPEN)


def test_object_synonyms():
    """Test object synonyms for parser."""
    lamp = GameObject(
        name="LAMP",
        synonyms=["LAMP", "LANTERN", "LIGHT"]
    )

    assert "LAMP" in lamp.synonyms
    assert "LANTERN" in lamp.synonyms
    assert lamp.matches_word("LANTERN")
    assert not lamp.matches_word("SWORD")


def test_object_location():
    """Test object parent/location tracking."""
    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)

    assert lamp.parent == room
    assert lamp in room.children

    # Move object
    player = GameObject(name="PLAYER")
    lamp.move_to(player)

    assert lamp.parent == player
    assert lamp not in room.children
    assert lamp in player.children
