"""Tests for game logic operations."""
import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.engine.operations.game_logic import MetaLocOp, LitOp, AccessibleOp


class TestMetaLocOp:
    """Tests for META-LOC operation."""

    def test_meta_loc_name(self):
        """Operation has correct name."""
        op = MetaLocOp()
        assert op.name == "META-LOC"

    def test_meta_loc_finds_room(self):
        """META-LOC returns ultimate container (room)."""
        from zil_interpreter.world.game_object import ObjectFlag
        world = WorldState()

        # Create hierarchy: ROOM -> PLAYER -> BAG -> LAMP
        room = GameObject(name="LIVING-ROOM")
        room.set_flag(ObjectFlag.SURFACE)  # ROOMBIT
        world.add_object(room)

        player = GameObject(name="PLAYER")
        player.move_to(room)
        world.add_object(player)

        bag = GameObject(name="BAG")
        bag.move_to(player)
        world.add_object(bag)

        lamp = GameObject(name="LAMP")
        lamp.move_to(bag)
        world.add_object(lamp)

        op = MetaLocOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        result = op.execute([Atom("LAMP")], evaluator)
        assert result == "LIVING-ROOM"

    def test_meta_loc_returns_none_for_orphan(self):
        """META-LOC returns None if no room found."""
        world = WorldState()

        lamp = GameObject(name="LAMP")
        world.add_object(lamp)

        op = MetaLocOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        result = op.execute([Atom("LAMP")], evaluator)
        assert result is None


class TestLitOp:
    """Tests for LIT? operation."""

    def test_lit_name(self):
        """Operation has correct name."""
        op = LitOp()
        assert op.name == "LIT?"

    def test_lit_true_for_room_with_light(self):
        """LIT? returns true if room has LIGHTBIT."""
        from zil_interpreter.world.game_object import ObjectFlag
        world = WorldState()
        room = GameObject(name="KITCHEN")
        room.set_flag(ObjectFlag.LIGHTBIT)
        world.add_object(room)

        op = LitOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("KITCHEN")], evaluator) is True

    def test_lit_false_for_dark_room(self):
        """LIT? returns false if room has no light."""
        world = WorldState()
        room = GameObject(name="CELLAR")
        world.add_object(room)

        op = LitOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("CELLAR")], evaluator) is False


class TestAccessibleOp:
    """Tests for ACCESSIBLE? operation."""

    def test_accessible_name(self):
        """Operation has correct name."""
        op = AccessibleOp()
        assert op.name == "ACCESSIBLE?"

    def test_accessible_true_in_room(self):
        """ACCESSIBLE? true for objects in current room."""
        world = WorldState()
        room = GameObject(name="KITCHEN")
        world.add_object(room)
        lamp = GameObject(name="LAMP")
        lamp.move_to(room)
        world.add_object(lamp)
        world.set_global("HERE", "KITCHEN")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("LAMP")], evaluator) is True

    def test_accessible_true_if_held(self):
        """ACCESSIBLE? true for objects held by player."""
        world = WorldState()
        player = GameObject(name="PLAYER")
        world.add_object(player)
        sword = GameObject(name="SWORD")
        sword.move_to(player)
        world.add_object(sword)
        world.set_global("PLAYER", "PLAYER")
        world.set_global("HERE", "KITCHEN")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("SWORD")], evaluator) is True

    def test_accessible_false_in_other_room(self):
        """ACCESSIBLE? false for objects in other rooms."""
        world = WorldState()
        room1 = GameObject(name="KITCHEN")
        world.add_object(room1)
        room2 = GameObject(name="CELLAR")
        world.add_object(room2)
        lamp = GameObject(name="LAMP")
        lamp.move_to(room2)
        world.add_object(lamp)
        world.set_global("HERE", "KITCHEN")
        world.set_global("PLAYER", "PLAYER")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("LAMP")], evaluator) is False

    def test_accessible_true_in_open_container(self):
        """ACCESSIBLE? true for objects in open container in room."""
        from zil_interpreter.world.game_object import ObjectFlag
        world = WorldState()
        room = GameObject(name="KITCHEN")
        world.add_object(room)

        box = GameObject(name="BOX")
        box.move_to(room)
        box.set_flag(ObjectFlag.CONTAINER)
        box.set_flag(ObjectFlag.OPEN)
        world.add_object(box)

        coin = GameObject(name="COIN")
        coin.move_to(box)
        world.add_object(coin)

        world.set_global("HERE", "KITCHEN")
        world.set_global("PLAYER", "PLAYER")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("COIN")], evaluator) is True

    def test_accessible_false_in_closed_container(self):
        """ACCESSIBLE? false for objects in closed container."""
        from zil_interpreter.world.game_object import ObjectFlag
        world = WorldState()
        room = GameObject(name="KITCHEN")
        world.add_object(room)

        box = GameObject(name="BOX")
        box.move_to(room)
        box.set_flag(ObjectFlag.CONTAINER)
        # Note: OPENBIT is NOT set, so container is closed
        world.add_object(box)

        coin = GameObject(name="COIN")
        coin.move_to(box)
        world.add_object(coin)

        world.set_global("HERE", "KITCHEN")
        world.set_global("PLAYER", "PLAYER")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("COIN")], evaluator) is False
