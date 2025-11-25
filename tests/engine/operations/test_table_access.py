"""Tests for table access operations."""
import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.table_data import TableData
from zil_interpreter.engine.operations.table_access import GetOp, PutOp, GetBOp, PutBOp


class TestGetOp:
    """Tests for GET operation."""

    def test_get_name(self):
        """Operation has correct name."""
        op = GetOp()
        assert op.name == "GET"

    def test_get_retrieves_word_from_table(self):
        """GET retrieves word at index from table."""
        world = WorldState()
        table = TableData(name="SCORES", data=[100, 200, 300])
        world.register_table("SCORES", table)

        op = GetOp()

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
        result = op.execute([Atom("SCORES"), Atom(1)], evaluator)
        assert result == 200


class TestPutOp:
    """Tests for PUT operation."""

    def test_put_name(self):
        """Operation has correct name."""
        op = PutOp()
        assert op.name == "PUT"

    def test_put_sets_word_in_table(self):
        """PUT sets word at index in table."""
        world = WorldState()
        table = TableData(name="DATA", data=[0, 0, 0])
        world.register_table("DATA", table)

        op = PutOp()

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
        result = op.execute([Atom("DATA"), Atom(1), Atom(999)], evaluator)

        # PUT returns the value set
        assert result == 999
        # Table is modified
        assert table.get_word(1) == 999


class TestGetBOp:
    """Tests for GETB operation."""

    def test_getb_name(self):
        """Operation has correct name."""
        op = GetBOp()
        assert op.name == "GETB"

    def test_getb_retrieves_byte_from_table(self):
        """GETB retrieves byte at byte index."""
        world = WorldState()
        table = TableData(name="BYTES", data=[0x1234, 0x5678])
        world.register_table("BYTES", table)

        op = GetBOp()

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
        assert op.execute([Atom("BYTES"), Atom(0)], evaluator) == 0x12
        assert op.execute([Atom("BYTES"), Atom(1)], evaluator) == 0x34
        assert op.execute([Atom("BYTES"), Atom(2)], evaluator) == 0x56
        assert op.execute([Atom("BYTES"), Atom(3)], evaluator) == 0x78


class TestPutBOp:
    """Tests for PUTB operation."""

    def test_putb_name(self):
        """Operation has correct name."""
        op = PutBOp()
        assert op.name == "PUTB"

    def test_putb_sets_byte_in_table(self):
        """PUTB sets byte at byte index."""
        world = WorldState()
        table = TableData(name="DATA", data=[0x0000])
        world.register_table("DATA", table)

        op = PutBOp()

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
        op.execute([Atom("DATA"), Atom(0), Atom(0xAB)], evaluator)
        assert table.get_word(0) == 0xAB00

        op.execute([Atom("DATA"), Atom(1), Atom(0xCD)], evaluator)
        assert table.get_word(0) == 0xABCD
