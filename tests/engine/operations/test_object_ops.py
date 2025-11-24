"""Tests for object manipulation operations."""

import pytest
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.parser.ast_nodes import Form, Atom, Number


class TestLocOperation:
    """Tests for LOC operation - get object location/parent."""

    def test_loc_returns_parent(self):
        """LOC returns the parent object of an object."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Create parent and child objects
        room = GameObject("ROOM", "A room")
        box = GameObject("BOX", "A box", parent=room)

        world.add_object(room)
        world.add_object(box)

        # Test LOC returns parent
        result = evaluator.evaluate(Form(Atom("LOC"), [Atom("BOX")]))
        assert result == room

    def test_loc_returns_none_for_no_parent(self):
        """LOC returns None when object has no parent."""
        world = WorldState()
        evaluator = Evaluator(world)

        room = GameObject("ROOM", "A room")
        world.add_object(room)

        result = evaluator.evaluate(Form(Atom("LOC"), [Atom("ROOM")]))
        assert result is None

    def test_loc_returns_none_for_nonexistent_object(self):
        """LOC returns None when object doesn't exist."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(Form(Atom("LOC"), [Atom("NONEXISTENT")]))
        assert result is None

    def test_loc_with_no_args(self):
        """LOC with no arguments returns None."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(Form(Atom("LOC"), []))
        assert result is None

    def test_loc_with_nested_objects(self):
        """LOC works with deeply nested objects."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Create nested structure: ROOM -> BOX -> COIN
        room = GameObject("ROOM", "A room")
        box = GameObject("BOX", "A box", parent=room)
        coin = GameObject("COIN", "A coin", parent=box)

        world.add_object(room)
        world.add_object(box)
        world.add_object(coin)

        # COIN's parent should be BOX
        result = evaluator.evaluate(Form(Atom("LOC"), [Atom("COIN")]))
        assert result == box

        # BOX's parent should be ROOM
        result = evaluator.evaluate(Form(Atom("LOC"), [Atom("BOX")]))
        assert result == room


class TestRemoveOperation:
    """Tests for REMOVE operation - remove object from world."""

    def test_remove_object_from_parent(self):
        """REMOVE removes object from its parent."""
        world = WorldState()
        evaluator = Evaluator(world)

        room = GameObject("ROOM", "A room")
        box = GameObject("BOX", "A box", parent=room)

        world.add_object(room)
        world.add_object(box)

        # Verify box is in room
        assert box.parent == room
        assert box in room.children

        # Remove box
        evaluator.evaluate(Form(Atom("REMOVE"), [Atom("BOX")]))

        # Verify box has no parent and room has no children
        assert box.parent is None
        assert box not in room.children

    def test_remove_object_with_no_parent(self):
        """REMOVE on object with no parent does nothing."""
        world = WorldState()
        evaluator = Evaluator(world)

        room = GameObject("ROOM", "A room")
        world.add_object(room)

        # Should not raise error
        evaluator.evaluate(Form(Atom("REMOVE"), [Atom("ROOM")]))
        assert room.parent is None

    def test_remove_nonexistent_object(self):
        """REMOVE on nonexistent object does nothing."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Should not raise error
        evaluator.evaluate(Form(Atom("REMOVE"), [Atom("NONEXISTENT")]))

    def test_remove_with_no_args(self):
        """REMOVE with no arguments does nothing."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Should not raise error
        evaluator.evaluate(Form(Atom("REMOVE"), []))

    def test_remove_preserves_children(self):
        """REMOVE preserves object's own children."""
        world = WorldState()
        evaluator = Evaluator(world)

        room = GameObject("ROOM", "A room")
        box = GameObject("BOX", "A box", parent=room)
        coin = GameObject("COIN", "A coin", parent=box)

        world.add_object(room)
        world.add_object(box)
        world.add_object(coin)

        # Remove box from room
        evaluator.evaluate(Form(Atom("REMOVE"), [Atom("BOX")]))

        # Box should still have coin as child
        assert coin.parent == box
        assert coin in box.children
        # But box should not be in room
        assert box.parent is None


class TestHeldOperation:
    """Tests for HELD? operation - check if player holds object."""

    def test_held_returns_true_when_player_holds_object(self):
        """HELD? returns true when object is held by player."""
        world = WorldState()
        evaluator = Evaluator(world)

        player = GameObject("ADVENTURER", "You")
        sword = GameObject("SWORD", "A sword", parent=player)

        world.add_object(player)
        world.add_object(sword)

        # Set ADVENTURER as the player
        world.set_global("PLAYER", "ADVENTURER")

        result = evaluator.evaluate(Form(Atom("HELD?"), [Atom("SWORD")]))
        assert result is True

    def test_held_returns_false_when_object_not_held(self):
        """HELD? returns false when object is not held by player."""
        world = WorldState()
        evaluator = Evaluator(world)

        player = GameObject("ADVENTURER", "You")
        room = GameObject("ROOM", "A room")
        sword = GameObject("SWORD", "A sword", parent=room)

        world.add_object(player)
        world.add_object(room)
        world.add_object(sword)

        world.set_global("PLAYER", "ADVENTURER")

        result = evaluator.evaluate(Form(Atom("HELD?"), [Atom("SWORD")]))
        assert result is False

    def test_held_returns_false_for_nonexistent_object(self):
        """HELD? returns false when object doesn't exist."""
        world = WorldState()
        evaluator = Evaluator(world)

        player = GameObject("ADVENTURER", "You")
        world.add_object(player)
        world.set_global("PLAYER", "ADVENTURER")

        result = evaluator.evaluate(Form(Atom("HELD?"), [Atom("NONEXISTENT")]))
        assert result is False

    def test_held_with_no_args(self):
        """HELD? with no arguments returns False."""
        world = WorldState()
        evaluator = Evaluator(world)

        player = GameObject("ADVENTURER", "You")
        world.add_object(player)
        world.set_global("PLAYER", "ADVENTURER")

        result = evaluator.evaluate(Form(Atom("HELD?"), []))
        assert result is False

    def test_held_when_no_player_defined(self):
        """HELD? returns false when no player is defined."""
        world = WorldState()
        evaluator = Evaluator(world)

        sword = GameObject("SWORD", "A sword")
        world.add_object(sword)

        result = evaluator.evaluate(Form(Atom("HELD?"), [Atom("SWORD")]))
        assert result is False

    def test_held_with_multiple_items(self):
        """HELD? works correctly with multiple items."""
        world = WorldState()
        evaluator = Evaluator(world)

        player = GameObject("ADVENTURER", "You")
        room = GameObject("ROOM", "A room")
        sword = GameObject("SWORD", "A sword", parent=player)
        shield = GameObject("SHIELD", "A shield", parent=player)
        helmet = GameObject("HELMET", "A helmet", parent=room)

        world.add_object(player)
        world.add_object(room)
        world.add_object(sword)
        world.add_object(shield)
        world.add_object(helmet)

        world.set_global("PLAYER", "ADVENTURER")

        # Player holds sword and shield
        assert evaluator.evaluate(Form(Atom("HELD?"), [Atom("SWORD")])) is True
        assert evaluator.evaluate(Form(Atom("HELD?"), [Atom("SHIELD")])) is True
        # Player does not hold helmet
        assert evaluator.evaluate(Form(Atom("HELD?"), [Atom("HELMET")])) is False
