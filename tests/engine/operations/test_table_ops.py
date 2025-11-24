"""Tests for table operations."""

import pytest
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState


class TestGetOperation:
    """Tests for GET operation."""

    def test_get_from_list(self):
        """GET retrieves element from list."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_list = [10, 20, 30, 40]
        result = evaluator.evaluate(
            Form(Atom("GET"), [test_list, Number(2)])
        )
        assert result == 30

    def test_get_index_0(self):
        """GET can access first element (0-indexed)."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_list = [100, 200, 300]
        result = evaluator.evaluate(
            Form(Atom("GET"), [test_list, Number(0)])
        )
        assert result == 100

    def test_get_out_of_bounds(self):
        """GET returns None for out-of-bounds index."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_list = [1, 2, 3]
        result = evaluator.evaluate(
            Form(Atom("GET"), [test_list, Number(10)])
        )
        assert result is None

    def test_get_evaluates_args(self):
        """GET evaluates its arguments."""
        world = WorldState()
        world.set_global("MYTABLE", [5, 10, 15])
        world.set_global("INDEX", 1)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("GET"), [Atom("MYTABLE"), Atom("INDEX")])
        )
        assert result == 10


class TestPutOperation:
    """Tests for PUT operation."""

    def test_put_into_list(self):
        """PUT stores element in list."""
        world = WorldState()
        test_list = [10, 20, 30]
        world.set_global("TESTLIST", test_list)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PUT"), [Atom("TESTLIST"), Number(1), Number(99)])
        )

        assert result == 99
        assert test_list[1] == 99

    def test_put_modifies_in_place(self):
        """PUT modifies the table in place."""
        world = WorldState()
        test_list = [1, 2, 3]
        world.set_global("TABLE", test_list)
        evaluator = Evaluator(world)

        evaluator.evaluate(
            Form(Atom("PUT"), [Atom("TABLE"), Number(0), Number(42)])
        )

        assert test_list[0] == 42
        assert world.get_global("TABLE")[0] == 42

    def test_put_returns_value(self):
        """PUT returns the value that was stored."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_list = [0, 0, 0]
        result = evaluator.evaluate(
            Form(Atom("PUT"), [test_list, Number(2), String("hello")])
        )

        assert result == "hello"

    def test_put_out_of_bounds(self):
        """PUT returns None for out-of-bounds index."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_list = [1, 2, 3]
        result = evaluator.evaluate(
            Form(Atom("PUT"), [test_list, Number(10), Number(99)])
        )

        assert result is None


class TestGetbOperation:
    """Tests for GETB operation."""

    def test_getb_from_list(self):
        """GETB retrieves byte from list."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_bytes = [0x41, 0x42, 0x43]  # ABC
        result = evaluator.evaluate(
            Form(Atom("GETB"), [test_bytes, Number(1)])
        )
        assert result == 0x42

    def test_getb_byte_range(self):
        """GETB masks to byte range (0-255)."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_bytes = [0x1FF, 0x200]  # Values > 255
        result = evaluator.evaluate(
            Form(Atom("GETB"), [test_bytes, Number(0)])
        )
        assert result == 0xFF  # Masked to byte

    def test_getb_from_bytes(self):
        """GETB works with bytes/bytearray."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_bytes = bytes([65, 66, 67])
        result = evaluator.evaluate(
            Form(Atom("GETB"), [test_bytes, Number(2)])
        )
        assert result == 67

    def test_getb_out_of_bounds(self):
        """GETB returns None for out-of-bounds offset."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_bytes = [1, 2, 3]
        result = evaluator.evaluate(
            Form(Atom("GETB"), [test_bytes, Number(10)])
        )
        assert result is None


class TestPutbOperation:
    """Tests for PUTB operation."""

    def test_putb_into_list(self):
        """PUTB stores byte in list."""
        world = WorldState()
        test_bytes = [0, 0, 0]
        world.set_global("TESTBYTES", test_bytes)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PUTB"), [Atom("TESTBYTES"), Number(1), Number(0x42)])
        )

        assert result == 0x42
        assert test_bytes[1] == 0x42

    def test_putb_truncates_to_byte(self):
        """PUTB truncates value to byte range."""
        world = WorldState()
        test_bytes = [0, 0]
        world.set_global("TESTBYTES", test_bytes)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PUTB"), [Atom("TESTBYTES"), Number(0), Number(0x1FF)])
        )

        assert result == 0xFF
        assert test_bytes[0] == 0xFF

    def test_putb_modifies_in_place(self):
        """PUTB modifies the table in place."""
        world = WorldState()
        test_bytes = [10, 20, 30]
        world.set_global("BYTES", test_bytes)
        evaluator = Evaluator(world)

        evaluator.evaluate(
            Form(Atom("PUTB"), [Atom("BYTES"), Number(2), Number(99)])
        )

        assert test_bytes[2] == 99

    def test_putb_out_of_bounds(self):
        """PUTB returns None for out-of-bounds offset."""
        world = WorldState()
        evaluator = Evaluator(world)

        test_bytes = [1, 2, 3]
        result = evaluator.evaluate(
            Form(Atom("PUTB"), [test_bytes, Number(10), Number(99)])
        )

        assert result is None


class TestLtableOperation:
    """Tests for LTABLE operation."""

    def test_ltable_creates_prefixed_table(self):
        """LTABLE creates table with length prefix."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("LTABLE"), [Number(10), Number(20), Number(30)])
        )

        assert result == [3, 10, 20, 30]
        assert result[0] == 3  # Length

    def test_ltable_empty(self):
        """LTABLE with no args creates [0]."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("LTABLE"), [])
        )

        assert result == [0]

    def test_ltable_evaluates_elements(self):
        """LTABLE evaluates its elements."""
        world = WorldState()
        world.set_global("A", 100)
        world.set_global("B", 200)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("LTABLE"), [Atom("A"), Atom("B")])
        )

        assert result == [2, 100, 200]

    def test_ltable_single_element(self):
        """LTABLE with single element."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("LTABLE"), [String("ITEM")])
        )

        assert result == [1, "ITEM"]


class TestItableOperation:
    """Tests for ITABLE operation."""

    def test_itable_creates_initialized_table(self):
        """ITABLE creates table with all elements initialized."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("ITABLE"), [Number(0), Number(5)])
        )

        assert result == [0, 0, 0, 0, 0]
        assert len(result) == 5

    def test_itable_with_string(self):
        """ITABLE can initialize with non-numeric values."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("ITABLE"), [String("NONE"), Number(3)])
        )

        assert result == ["NONE", "NONE", "NONE"]

    def test_itable_zero_size(self):
        """ITABLE with size 0 creates empty table."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("ITABLE"), [Number(42), Number(0)])
        )

        assert result == []

    def test_itable_evaluates_arguments(self):
        """ITABLE evaluates its arguments."""
        world = WorldState()
        world.set_global("INIT", -1)
        world.set_global("SIZE", 4)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("ITABLE"), [Atom("INIT"), Atom("SIZE")])
        )

        assert result == [-1, -1, -1, -1]


class TestTableOperation:
    """Tests for TABLE operation."""

    def test_table_creates_bare_table(self):
        """TABLE creates table without length prefix."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TABLE"), [Number(10), Number(20), Number(30)])
        )

        assert result == [10, 20, 30]
        # No length prefix, unlike LTABLE

    def test_table_empty(self):
        """TABLE with no args creates empty list."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TABLE"), [])
        )

        assert result == []

    def test_table_evaluates_elements(self):
        """TABLE evaluates its elements."""
        world = WorldState()
        world.set_global("X", 5)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TABLE"), [Atom("X"), Number(10)])
        )

        assert result == [5, 10]

    def test_table_mixed_types(self):
        """TABLE can contain mixed types."""
        world = WorldState()
        world.set_global("BOOL_VAL", True)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TABLE"), [Number(42), String("hello"), Atom("BOOL_VAL")])
        )

        assert result == [42, "hello", True]
