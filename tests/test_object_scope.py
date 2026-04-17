"""Tests for object scope restriction in ObjectResolver (Task 7)."""
import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject, ObjectFlag
from zil_interpreter.runtime.object_resolver import ObjectResolver
from zil_interpreter.runtime.command_types import NounPhrase


@pytest.fixture
def scoped_world():
    """Create a world with two rooms, player, and objects."""
    world = WorldState()

    room_a = GameObject("ROOM-A", description="Room A")
    room_b = GameObject("ROOM-B", description="Room B")
    world.add_object(room_a)
    world.add_object(room_b)
    world.set_current_room(room_a)

    player = GameObject("WINNER", description="Player")
    player.move_to(room_a)
    world.add_object(player)
    world.set_global("WINNER", player)

    # Object in current room
    lamp = GameObject("LAMP", description="brass lamp", synonyms=["LAMP", "LANTERN"])
    lamp.move_to(room_a)
    world.add_object(lamp)

    # Object in another room (should NOT be findable)
    sword = GameObject("SWORD", description="rusty sword", synonyms=["SWORD"])
    sword.move_to(room_b)
    world.add_object(sword)

    # Object in player inventory
    coin = GameObject("COIN", description="gold coin", synonyms=["COIN"])
    coin.move_to(player)
    world.add_object(coin)

    # Open container in room with contents
    box = GameObject("BOX", description="open box", synonyms=["BOX"])
    box.set_flag(ObjectFlag.CONTAINER)
    box.set_flag(ObjectFlag.OPEN)
    box.move_to(room_a)
    world.add_object(box)

    scroll = GameObject("SCROLL", description="ancient scroll", synonyms=["SCROLL"])
    scroll.move_to(box)
    world.add_object(scroll)

    # LOCAL-GLOBALS object with a child
    local_globals = GameObject("LOCAL-GLOBALS", description="")
    world.add_object(local_globals)

    stream = GameObject("STREAM", description="rushing stream", synonyms=["STREAM", "WATER"])
    stream.move_to(local_globals)
    world.add_object(stream)

    return world


@pytest.fixture
def resolver(scoped_world):
    return ObjectResolver(scoped_world)


class TestObjectScope:
    """Object resolver must restrict search to accessible scope."""

    def test_finds_object_in_current_room(self, resolver, scoped_world):
        """Object directly in current room is found."""
        np = NounPhrase(noun="LAMP")
        matches = resolver.find_matches(np, scoped_world.get_current_room())
        assert len(matches) == 1
        assert matches[0].name == "LAMP"

    def test_does_not_find_object_in_other_room(self, resolver, scoped_world):
        """Object in a different room is NOT found."""
        np = NounPhrase(noun="SWORD")
        matches = resolver.find_matches(np, scoped_world.get_current_room())
        assert matches == [], f"Expected no matches, got: {[m.name for m in matches]}"

    def test_finds_object_in_player_inventory(self, resolver, scoped_world):
        """Object in player inventory is found."""
        np = NounPhrase(noun="COIN")
        matches = resolver.find_matches(np, scoped_world.get_current_room())
        assert len(matches) == 1
        assert matches[0].name == "COIN"

    def test_finds_object_in_open_container_in_room(self, resolver, scoped_world):
        """Object inside an open container in the current room is found."""
        np = NounPhrase(noun="SCROLL")
        matches = resolver.find_matches(np, scoped_world.get_current_room())
        assert len(matches) == 1
        assert matches[0].name == "SCROLL"

    def test_finds_local_globals(self, resolver, scoped_world):
        """Objects in LOCAL-GLOBALS are found regardless of room."""
        np = NounPhrase(noun="STREAM")
        matches = resolver.find_matches(np, scoped_world.get_current_room())
        assert len(matches) == 1
        assert matches[0].name == "STREAM"
