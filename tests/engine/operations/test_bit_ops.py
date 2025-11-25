"""Tests for bit manipulation operations."""

import pytest
from zil_interpreter.parser.ast_nodes import Form, Atom, Number
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState


class TestBandOperation:
    """Tests for BAND bitwise AND operation."""

    def test_band_basic(self):
        """BAND performs bitwise AND."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BAND"), [Number(0b1100), Number(0b1010)])
        )
        assert result == 0b1000

    def test_band_with_mask(self):
        """BAND can extract specific bits."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BAND"), [Number(0xFF), Number(0x0F)])
        )
        assert result == 0x0F

    def test_band_zero(self):
        """BAND with 0 returns 0."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BAND"), [Number(0xFF), Number(0)])
        )
        assert result == 0

    def test_band_evaluates_args(self):
        """BAND evaluates its arguments."""
        world = WorldState()
        world.set_global("FLAGS", 0b1111)
        world.set_global("MASK", 0b0011)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BAND"), [Atom("FLAGS"), Atom("MASK")])
        )
        assert result == 0b0011


class TestBorOperation:
    """Tests for BOR bitwise OR operation."""

    def test_bor_basic(self):
        """BOR performs bitwise OR."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BOR"), [Number(0b1100), Number(0b1010)])
        )
        assert result == 0b1110

    def test_bor_combine_flags(self):
        """BOR can combine bit flags."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BOR"), [Number(0x01), Number(0x02)])
        )
        assert result == 0x03

    def test_bor_zero(self):
        """BOR with 0 returns other value."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BOR"), [Number(0xFF), Number(0)])
        )
        assert result == 0xFF

    def test_bor_evaluates_args(self):
        """BOR evaluates its arguments."""
        world = WorldState()
        world.set_global("FLAG1", 0b0001)
        world.set_global("FLAG2", 0b0010)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BOR"), [Atom("FLAG1"), Atom("FLAG2")])
        )
        assert result == 0b0011


class TestBtstOperation:
    """Tests for BTST bit test operation."""

    def test_btst_bit_set(self):
        """BTST returns TRUE when bit is set."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BTST"), [Number(0b1010), Number(0b0010)])
        )
        assert result is True

    def test_btst_bit_not_set(self):
        """BTST returns FALSE when bit is not set."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BTST"), [Number(0b1010), Number(0b0100)])
        )
        assert result is False

    def test_btst_multiple_bits(self):
        """BTST returns TRUE if any masked bit is set."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BTST"), [Number(0b1010), Number(0b0011)])
        )
        assert result is True  # bit 1 is set

    def test_btst_zero_mask(self):
        """BTST with zero mask returns FALSE."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BTST"), [Number(0xFF), Number(0)])
        )
        assert result is False

    def test_btst_evaluates_args(self):
        """BTST evaluates its arguments."""
        world = WorldState()
        world.set_global("FLAGS", 0b1111)
        world.set_global("MASK", 0b0001)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BTST"), [Atom("FLAGS"), Atom("MASK")])
        )
        assert result is True


class TestBcomOperation:
    """Tests for BCOM bitwise complement operation."""

    def test_bcom_basic(self):
        """BCOM performs bitwise complement."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BCOM"), [Number(0x0000)])
        )
        assert result == 0xFFFF

    def test_bcom_inverts_bits(self):
        """BCOM inverts all bits in 16-bit word."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BCOM"), [Number(0x00FF)])
        )
        assert result == 0xFF00

    def test_bcom_all_ones(self):
        """BCOM of 0xFFFF returns 0x0000."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BCOM"), [Number(0xFFFF)])
        )
        assert result == 0x0000

    def test_bcom_evaluates_arg(self):
        """BCOM evaluates its argument."""
        world = WorldState()
        world.set_global("MASK", 0x00FF)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("BCOM"), [Atom("MASK")])
        )
        assert result == 0xFF00


class TestMapretOperation:
    """Tests for MAPRET return from MAPF iteration operation."""

    def test_mapret_returns_value(self):
        """MAPRET returns evaluated value."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("MAPRET"), [Number(42)])
        )
        assert result == 42

    def test_mapret_evaluates_arg(self):
        """MAPRET evaluates its argument."""
        world = WorldState()
        world.set_global("VALUE", 100)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("MAPRET"), [Atom("VALUE")])
        )
        assert result == 100

    def test_mapret_no_args(self):
        """MAPRET with no args returns None."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("MAPRET"), [])
        )
        assert result is None

    def test_mapret_with_expression(self):
        """MAPRET evaluates complex expressions."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("MAPRET"), [
                Form(Atom("+"), [Number(10), Number(20)])
            ])
        )
        assert result == 30
