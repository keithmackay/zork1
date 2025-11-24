"""Tests for comparison and object operations."""

import pytest
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState


class TestGQuestionOperation:
    """Tests for G? (greater than) operation."""

    def test_g_question_true(self):
        """G? returns true when first > second."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("G?"), [Number(5), Number(3)])
        )
        assert result is True

    def test_g_question_false(self):
        """G? returns false when first <= second."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("G?"), [Number(3), Number(5)])
        )
        assert result is False

    def test_g_question_equal(self):
        """G? returns false for equal values."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("G?"), [Number(5), Number(5)])
        )
        assert result is False

    def test_g_question_evaluates_args(self):
        """G? evaluates its arguments."""
        world = WorldState()
        world.set_global("A", 10)
        world.set_global("B", 5)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("G?"), [Atom("A"), Atom("B")])
        )
        assert result is True


class TestLQuestionOperation:
    """Tests for L? (less than) operation."""

    def test_l_question_true(self):
        """L? returns true when first < second."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("L?"), [Number(3), Number(5)])
        )
        assert result is True

    def test_l_question_false(self):
        """L? returns false when first >= second."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("L?"), [Number(5), Number(3)])
        )
        assert result is False

    def test_l_question_equal(self):
        """L? returns false for equal values."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("L?"), [Number(5), Number(5)])
        )
        assert result is False

    def test_l_question_evaluates_args(self):
        """L? evaluates its arguments."""
        world = WorldState()
        world.set_global("A", 3)
        world.set_global("B", 10)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("L?"), [Atom("A"), Atom("B")])
        )
        assert result is True


class TestNextQuestionOperation:
    """Tests for NEXT? (get next sibling object) operation."""

    def test_next_question_returns_sibling(self):
        """NEXT? returns next sibling object."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        room = GameObject("ROOM")
        obj1 = GameObject("OBJ1")
        obj2 = GameObject("OBJ2")
        obj3 = GameObject("OBJ3")

        world.add_object(room)
        world.add_object(obj1)
        world.add_object(obj2)
        world.add_object(obj3)

        obj1.move_to(room)
        obj2.move_to(room)
        obj3.move_to(room)

        evaluator = Evaluator(world)

        # Get next sibling of obj1
        result = evaluator.evaluate(
            Form(Atom("NEXT?"), [Atom("OBJ1")])
        )

        assert result == obj2

    def test_next_question_last_child(self):
        """NEXT? returns FALSE for last child."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        room = GameObject("ROOM")
        obj1 = GameObject("OBJ1")
        obj2 = GameObject("OBJ2")

        world.add_object(room)
        world.add_object(obj1)
        world.add_object(obj2)

        obj1.move_to(room)
        obj2.move_to(room)

        evaluator = Evaluator(world)

        # Since children is a set, order is not guaranteed
        # Find which object is actually last
        children = list(room.children)
        last_child = children[-1]

        # Get next sibling of last child
        result = evaluator.evaluate(
            Form(Atom("NEXT?"), [Atom(last_child.name)])
        )

        assert result is False

    def test_next_question_no_parent(self):
        """NEXT? returns FALSE for object with no parent."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        obj = GameObject("OBJ")
        world.add_object(obj)

        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("NEXT?"), [Atom("OBJ")])
        )

        assert result is False

    def test_next_question_invalid_object(self):
        """NEXT? returns FALSE for invalid object."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("NEXT?"), [Atom("NONEXISTENT")])
        )

        assert result is False


class TestGetptOperation:
    """Tests for GETPT (get property table entry) operation."""

    def test_getpt_existing_property(self):
        """GETPT returns property reference for existing property."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        lamp = GameObject("LAMP")
        lamp.set_property("SIZE", 10)
        world.add_object(lamp)

        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("LAMP"), Atom("SIZE")])
        )

        # Should return property reference (not FALSE)
        assert result is not False
        assert result != 0

    def test_getpt_missing_property(self):
        """GETPT returns FALSE for missing property."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        lamp = GameObject("LAMP")
        world.add_object(lamp)

        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("LAMP"), Atom("MISSING")])
        )

        assert result is False

    def test_getpt_invalid_object(self):
        """GETPT returns FALSE for invalid object."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("NONEXISTENT"), Atom("PROP")])
        )

        assert result is False

    def test_getpt_property_check(self):
        """GETPT can be used for property existence check."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        obj = GameObject("OBJ")
        obj.set_property("DESC", "test")
        world.add_object(obj)

        evaluator = Evaluator(world)

        # Property exists
        result1 = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("OBJ"), Atom("DESC")])
        )
        assert result1 is not False

        # Property doesn't exist
        result2 = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("OBJ"), Atom("MISSING")])
        )
        assert result2 is False


class TestPtsizeOperation:
    """Tests for PTSIZE (get property table size) operation."""

    def test_ptsize_integer_property(self):
        """PTSIZE returns 2 for integer property."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        obj = GameObject("OBJ")
        obj.set_property("SIZE", 10)
        world.add_object(obj)

        evaluator = Evaluator(world)

        # Get property reference
        prop_ref = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("OBJ"), Atom("SIZE")])
        )

        # Get size
        size = evaluator.evaluate(
            Form(Atom("PTSIZE"), [prop_ref])
        )

        assert size == 2

    def test_ptsize_table_property(self):
        """PTSIZE returns correct size for table property."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        obj = GameObject("OBJ")
        obj.set_property("TABLE", [1, 2, 3, 4])
        world.add_object(obj)

        evaluator = Evaluator(world)

        # Get property reference
        prop_ref = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("OBJ"), Atom("TABLE")])
        )

        # Get size (4 elements * 2 bytes = 8)
        size = evaluator.evaluate(
            Form(Atom("PTSIZE"), [prop_ref])
        )

        assert size == 8

    def test_ptsize_false(self):
        """PTSIZE returns 0 for FALSE property ref."""
        world = WorldState()
        evaluator = Evaluator(world)

        size = evaluator.evaluate(
            Form(Atom("PTSIZE"), [False])
        )

        assert size == 0

    def test_ptsize_string_property(self):
        """PTSIZE returns string length for string property."""
        from zil_interpreter.world.game_object import GameObject

        world = WorldState()
        obj = GameObject("OBJ")
        obj.set_property("DESC", "hello")
        world.add_object(obj)

        evaluator = Evaluator(world)

        prop_ref = evaluator.evaluate(
            Form(Atom("GETPT"), [Atom("OBJ"), Atom("DESC")])
        )

        size = evaluator.evaluate(
            Form(Atom("PTSIZE"), [prop_ref])
        )

        assert size == 5
