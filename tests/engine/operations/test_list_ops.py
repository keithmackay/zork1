"""Tests for list operations."""

from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String


# LENGTH Operation Tests
def test_length_of_string():
    """LENGTH returns length of string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("LENGTH"), [String("Hello")])
    )
    assert result == 5


def test_length_of_empty_string():
    """LENGTH of empty string returns 0."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("LENGTH"), [String("")])
    )
    assert result == 0


def test_length_no_args():
    """LENGTH with no arguments returns 0."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("LENGTH"), []))
    assert result == 0


# NTH Operation Tests
def test_nth_first_element():
    """NTH gets first element (1-indexed)."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Create a list by setting a global
    world.set_global("TEST-LIST", [10, 20, 30])

    result = evaluator.evaluate(
        Form(Atom("NTH"), [Atom("TEST-LIST"), Number(1)])
    )
    assert result == 10


def test_nth_middle_element():
    """NTH gets middle element."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", ["a", "b", "c"])

    result = evaluator.evaluate(
        Form(Atom("NTH"), [Atom("TEST-LIST"), Number(2)])
    )
    assert result == "b"


def test_nth_last_element():
    """NTH gets last element."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [1, 2, 3, 4, 5])

    result = evaluator.evaluate(
        Form(Atom("NTH"), [Atom("TEST-LIST"), Number(5)])
    )
    assert result == 5


def test_nth_out_of_bounds():
    """NTH with out of bounds index returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [1, 2, 3])

    result = evaluator.evaluate(
        Form(Atom("NTH"), [Atom("TEST-LIST"), Number(10)])
    )
    assert result is None


def test_nth_zero_index():
    """NTH with index 0 returns None (1-indexed)."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [1, 2, 3])

    result = evaluator.evaluate(
        Form(Atom("NTH"), [Atom("TEST-LIST"), Number(0)])
    )
    assert result is None


def test_nth_string():
    """NTH gets character from string (1-indexed)."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("NTH"), [String("Hello"), Number(2)])
    )
    assert result == "e"


# REST Operation Tests
def test_rest_basic():
    """REST returns all but first element."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [1, 2, 3, 4])

    result = evaluator.evaluate(
        Form(Atom("REST"), [Atom("TEST-LIST")])
    )
    assert result == [2, 3, 4]


def test_rest_single_element():
    """REST of single element list returns empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [42])

    result = evaluator.evaluate(
        Form(Atom("REST"), [Atom("TEST-LIST")])
    )
    assert result == []


def test_rest_empty_list():
    """REST of empty list returns empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [])

    result = evaluator.evaluate(
        Form(Atom("REST"), [Atom("TEST-LIST")])
    )
    assert result == []


def test_rest_string():
    """REST of string returns all but first character."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("REST"), [String("Hello")])
    )
    assert result == "ello"


# FIRST (list) Operation Tests
def test_first_list():
    """FIRST returns first element of list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [10, 20, 30])

    result = evaluator.evaluate(
        Form(Atom("FIRST"), [Atom("TEST-LIST")])
    )
    assert result == 10


def test_first_empty_list():
    """FIRST of empty list returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [])

    result = evaluator.evaluate(
        Form(Atom("FIRST"), [Atom("TEST-LIST")])
    )
    assert result is None


def test_first_string():
    """FIRST of string returns first character."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("FIRST"), [String("Hello")])
    )
    assert result == "H"


def test_first_no_args():
    """FIRST with no arguments returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("FIRST"), []))
    assert result is None


# NEXT Operation Tests
def test_next_sibling():
    """NEXT returns next sibling object."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Create parent with multiple children
    parent = GameObject("ROOM")
    child1 = GameObject("ITEM1")
    child2 = GameObject("ITEM2")

    child1.move_to(parent)
    child2.move_to(parent)

    world.add_object(parent)
    world.add_object(child1)
    world.add_object(child2)

    # Get all siblings as a list
    siblings = list(parent.children)

    # Find which child is first
    if siblings[0] == child1:
        # If child1 is first, next should be child2
        result = evaluator.evaluate(
            Form(Atom("NEXT"), [Atom("ITEM1")])
        )
        assert result == child2
    else:
        # If child2 is first, next should be child1
        result = evaluator.evaluate(
            Form(Atom("NEXT"), [Atom("ITEM2")])
        )
        assert result == child1


def test_next_last_sibling():
    """NEXT of last sibling returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Create parent with single child
    parent = GameObject("ROOM")
    child = GameObject("ITEM")

    child.move_to(parent)

    world.add_object(parent)
    world.add_object(child)

    # Get all siblings
    result = evaluator.evaluate(
        Form(Atom("NEXT"), [Atom("ITEM")])
    )

    # If it's the only child, next should be None
    assert result is None


def test_next_no_parent():
    """NEXT of object with no parent returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    obj = GameObject("ITEM")
    world.add_object(obj)

    result = evaluator.evaluate(
        Form(Atom("NEXT"), [Atom("ITEM")])
    )
    assert result is None


# BACK Operation Tests
def test_back_second_element():
    """BACK returns previous sibling."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Create parent with multiple children
    parent = GameObject("ROOM")
    child1 = GameObject("ITEM1")
    child2 = GameObject("ITEM2")

    child1.move_to(parent)
    child2.move_to(parent)

    world.add_object(parent)
    world.add_object(child1)
    world.add_object(child2)

    # Get all siblings as a list
    siblings = list(parent.children)

    # Find which child is second
    if siblings[0] == child1 and len(siblings) > 1:
        # If child1 is first, BACK on child2 should return child1
        result = evaluator.evaluate(
            Form(Atom("BACK"), [Atom("ITEM2")])
        )
        assert result == child1
    elif siblings[0] == child2 and len(siblings) > 1:
        # If child2 is first, BACK on child1 should return child2
        result = evaluator.evaluate(
            Form(Atom("BACK"), [Atom("ITEM1")])
        )
        assert result == child2


def test_back_first_element():
    """BACK of first element returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    parent = GameObject("ROOM")
    child = GameObject("ITEM")

    child.move_to(parent)

    world.add_object(parent)
    world.add_object(child)

    result = evaluator.evaluate(
        Form(Atom("BACK"), [Atom("ITEM")])
    )
    assert result is None


def test_back_no_parent():
    """BACK of object with no parent returns None."""
    world = WorldState()
    evaluator = Evaluator(world)

    obj = GameObject("ITEM")
    world.add_object(obj)

    result = evaluator.evaluate(
        Form(Atom("BACK"), [Atom("ITEM")])
    )
    assert result is None


# EMPTY? Operation Tests
def test_empty_check_empty_list():
    """EMPTY? returns True for empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [])

    result = evaluator.evaluate(
        Form(Atom("EMPTY?"), [Atom("TEST-LIST")])
    )
    assert result is True


def test_empty_check_non_empty_list():
    """EMPTY? returns False for non-empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [1, 2, 3])

    result = evaluator.evaluate(
        Form(Atom("EMPTY?"), [Atom("TEST-LIST")])
    )
    assert result is False


def test_empty_check_empty_string():
    """EMPTY? returns True for empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("EMPTY?"), [String("")])
    )
    assert result is True


def test_empty_check_non_empty_string():
    """EMPTY? returns False for non-empty string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("EMPTY?"), [String("Hello")])
    )
    assert result is False


def test_empty_check_zero():
    """EMPTY? returns True for zero."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("EMPTY?"), [Number(0)])
    )
    assert result is True


def test_empty_check_non_zero():
    """EMPTY? returns False for non-zero number."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("EMPTY?"), [Number(42)])
    )
    assert result is False


# MEMQ Operation Tests
def test_memq_element_found():
    """MEMQ returns True if element is in list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [1, 2, 3, 4, 5])

    result = evaluator.evaluate(
        Form(Atom("MEMQ"), [Number(3), Atom("TEST-LIST")])
    )
    assert result is True


def test_memq_element_not_found():
    """MEMQ returns False if element not in list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [1, 2, 3])

    result = evaluator.evaluate(
        Form(Atom("MEMQ"), [Number(10), Atom("TEST-LIST")])
    )
    assert result is False


def test_memq_string_in_list():
    """MEMQ finds string in list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", ["hello", "world", "test"])

    result = evaluator.evaluate(
        Form(Atom("MEMQ"), [String("world"), Atom("TEST-LIST")])
    )
    assert result is True


def test_memq_empty_list():
    """MEMQ returns False for empty list."""
    world = WorldState()
    evaluator = Evaluator(world)

    world.set_global("TEST-LIST", [])

    result = evaluator.evaluate(
        Form(Atom("MEMQ"), [Number(1), Atom("TEST-LIST")])
    )
    assert result is False


def test_memq_char_in_string():
    """MEMQ can check if character is in string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MEMQ"), [String("e"), String("Hello")])
    )
    assert result is True


def test_memq_char_not_in_string():
    """MEMQ returns False if character not in string."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("MEMQ"), [String("x"), String("Hello")])
    )
    assert result is False
