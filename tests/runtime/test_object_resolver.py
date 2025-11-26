"""Tests for ObjectResolver (Tasks 5.9-5.11)."""
import pytest
from zil_interpreter.runtime.object_resolver import ObjectResolver, DisambiguationNeeded
from zil_interpreter.runtime.command_types import NounPhrase
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject, ObjectFlag


@pytest.fixture
def world():
    """Create world state with test objects."""
    world = WorldState()

    # Create rooms
    room = GameObject("LIVING-ROOM", description="Living Room")
    other_room = GameObject("KITCHEN", description="Kitchen")
    world.add_object(room)
    world.add_object(other_room)
    world.set_current_room(room)

    # Create player
    player = GameObject("PLAYER", description="Player")
    player.move_to(room)
    world.add_object(player)
    world.set_global("WINNER", player)

    # Create objects
    lamp = GameObject(
        "LAMP",
        description="brass lamp",
        synonyms=["LAMP", "LANTERN", "LIGHT"]
    )
    lamp.adjectives = ["BRASS"]
    lamp.move_to(room)
    world.add_object(lamp)

    case = GameObject(
        "CASE",
        description="wooden case",
        synonyms=["CASE", "BOX"]
    )
    case.adjectives = ["WOODEN"]
    case.set_flag(ObjectFlag.CONTAINER)
    case.set_flag(ObjectFlag.OPEN)
    case.move_to(room)
    world.add_object(case)

    # Closed container
    chest = GameObject(
        "CHEST",
        description="treasure chest",
        synonyms=["CHEST"]
    )
    chest.set_flag(ObjectFlag.CONTAINER)
    # Not open
    chest.move_to(room)
    world.add_object(chest)

    # Hidden item in chest
    gem = GameObject(
        "GEM",
        description="sparkly gem",
        synonyms=["GEM", "JEWEL"]
    )
    gem.move_to(chest)
    world.add_object(gem)

    return world


@pytest.fixture
def resolver(world):
    """Create resolver with world."""
    return ObjectResolver(world)


class TestBasicResolution:
    """Tests for basic object resolution (Task 5.9)."""

    def test_finds_object_by_synonym(self, resolver, world):
        """Resolver finds object by synonym."""
        np = NounPhrase(noun="LAMP")
        obj = resolver.resolve(np, world.get_current_room())
        assert obj is not None
        assert obj.name == "LAMP"

    def test_finds_object_by_alternate_synonym(self, resolver, world):
        """Resolver finds object by alternate synonym."""
        np = NounPhrase(noun="LANTERN")
        obj = resolver.resolve(np, world.get_current_room())
        assert obj is not None
        assert obj.name == "LAMP"

    def test_not_found_returns_none(self, resolver, world):
        """Non-existent object returns None."""
        np = NounPhrase(noun="DINOSAUR")
        obj = resolver.resolve(np, world.get_current_room())
        assert obj is None

    def test_uses_adjective_to_match(self, resolver, world):
        """Adjective helps identify object."""
        np = NounPhrase(adjectives=["BRASS"], noun="LAMP")
        obj = resolver.resolve(np, world.get_current_room())
        assert obj is not None
        assert obj.name == "LAMP"


class TestAccessibility:
    """Tests for accessibility checking (Task 5.10)."""

    def test_accessible_in_room(self, resolver, world):
        """Objects in current room are accessible."""
        lamp = world.get_object("LAMP")
        assert resolver.is_accessible(lamp, world.get_current_room())

    def test_accessible_in_inventory(self, resolver, world):
        """Objects in inventory are accessible."""
        lamp = world.get_object("LAMP")
        player = world.get_object("PLAYER")
        lamp.move_to(player)
        assert resolver.is_accessible(lamp, world.get_current_room())

    def test_accessible_in_open_container(self, resolver, world):
        """Objects in open containers are accessible."""
        lamp = world.get_object("LAMP")
        case = world.get_object("CASE")
        lamp.move_to(case)
        assert resolver.is_accessible(lamp, world.get_current_room())

    def test_not_accessible_in_closed_container(self, resolver, world):
        """Objects in closed containers not accessible."""
        gem = world.get_object("GEM")
        # GEM is in closed CHEST
        assert not resolver.is_accessible(gem, world.get_current_room())

    def test_not_accessible_in_other_room(self, resolver, world):
        """Objects in other rooms not accessible."""
        lamp = world.get_object("LAMP")
        other_room = world.get_object("KITCHEN")
        lamp.move_to(other_room)
        assert not resolver.is_accessible(lamp, world.get_current_room())


class TestDisambiguation:
    """Tests for disambiguation (Task 5.11)."""

    def test_find_multiple_matches(self, resolver, world):
        """find_matches returns all matching objects."""
        # Add another lamp
        other_lamp = GameObject(
            "BROKEN-LAMP",
            synonyms=["LAMP", "LIGHT"]
        )
        other_lamp.adjectives = ["BROKEN"]
        other_lamp.move_to(world.get_current_room())
        world.add_object(other_lamp)

        np = NounPhrase(noun="LAMP")
        matches = resolver.find_matches(np, world.get_current_room())
        assert len(matches) == 2

    def test_adjective_narrows_matches(self, resolver, world):
        """Adjective narrows down matches."""
        # Add another lamp
        other_lamp = GameObject(
            "BROKEN-LAMP",
            synonyms=["LAMP", "LIGHT"]
        )
        other_lamp.adjectives = ["BROKEN"]
        other_lamp.move_to(world.get_current_room())
        world.add_object(other_lamp)

        np = NounPhrase(adjectives=["BRASS"], noun="LAMP")
        matches = resolver.find_matches(np, world.get_current_room())
        assert len(matches) == 1
        assert matches[0].name == "LAMP"

    def test_single_match_resolves(self, resolver, world):
        """Single match resolves without ambiguity."""
        np = NounPhrase(noun="CASE")
        obj = resolver.resolve(np, world.get_current_room())
        assert obj is not None
        assert obj.name == "CASE"

    def test_multiple_matches_raises(self, resolver, world):
        """Multiple matches raise DisambiguationNeeded."""
        # Add another lamp
        other_lamp = GameObject(
            "BROKEN-LAMP",
            synonyms=["LAMP", "LIGHT"]
        )
        other_lamp.adjectives = ["BROKEN"]
        other_lamp.move_to(world.get_current_room())
        world.add_object(other_lamp)

        np = NounPhrase(noun="LAMP")
        with pytest.raises(DisambiguationNeeded) as exc_info:
            resolver.resolve(np, world.get_current_room())
        assert len(exc_info.value.candidates) == 2
