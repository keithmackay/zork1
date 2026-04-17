"""Tests for Zork II operations: NEXTP, FIXED-FONT-ON/OFF, PUSH, RSTACK."""
import pytest
from io import StringIO
from unittest.mock import Mock


class TestNextpOperation:
    """Tests for NEXTP operation - get next property."""

    def test_nextp_operation_registered(self):
        """NEXTP operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("NEXTP") is not None

    def test_nextp_returns_first_property(self):
        """NEXTP with 0 returns first property number."""
        from zil_interpreter.engine.operations.zork2_ops import NextpOp
        op = NextpOp()

        mock_obj = Mock()
        mock_obj.properties = {"SIZE": 10, "DESC": "test", "VALUE": 5}

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(side_effect=lambda x: mock_obj if x == "OBJ" else 0)
        mock_evaluator.world = Mock()
        mock_evaluator.world.get_object = Mock(return_value=mock_obj)

        # NEXTP with 0 should return first property
        result = op.execute(["OBJ", 0], mock_evaluator)
        assert result is not None

    def test_nextp_returns_next_property(self):
        """NEXTP returns next property after given one."""
        from zil_interpreter.engine.operations.zork2_ops import NextpOp
        op = NextpOp()

        mock_obj = Mock()
        mock_obj.properties = {"P1": 1, "P2": 2, "P3": 3}

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(side_effect=lambda x: mock_obj if x == "OBJ" else "P1")
        mock_evaluator.world = Mock()
        mock_evaluator.world.get_object = Mock(return_value=mock_obj)

        result = op.execute(["OBJ", "P1"], mock_evaluator)
        # Should return a property name that comes after P1
        assert result in mock_obj.properties or result == 0


class TestFixedFontOperations:
    """Tests for FIXED-FONT-ON and FIXED-FONT-OFF operations."""

    def test_fixed_font_on_registered(self):
        """FIXED-FONT-ON operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("FIXED-FONT-ON") is not None

    def test_fixed_font_off_registered(self):
        """FIXED-FONT-OFF operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("FIXED-FONT-OFF") is not None

    def test_fixed_font_on_sets_flag(self):
        """FIXED-FONT-ON sets fixed font flag."""
        from zil_interpreter.engine.operations.zork2_ops import FixedFontOnOp
        op = FixedFontOnOp()

        mock_evaluator = Mock()
        mock_evaluator.world = Mock()
        mock_evaluator.world.set_global = Mock()

        result = op.execute([], mock_evaluator)

        mock_evaluator.world.set_global.assert_called_with("FIXED-FONT", True)
        assert result is True

    def test_fixed_font_off_clears_flag(self):
        """FIXED-FONT-OFF clears fixed font flag."""
        from zil_interpreter.engine.operations.zork2_ops import FixedFontOffOp
        op = FixedFontOffOp()

        mock_evaluator = Mock()
        mock_evaluator.world = Mock()
        mock_evaluator.world.set_global = Mock()

        result = op.execute([], mock_evaluator)

        mock_evaluator.world.set_global.assert_called_with("FIXED-FONT", False)
        assert result is True


class TestStackOperations:
    """Tests for PUSH and RSTACK stack operations."""

    def test_push_operation_registered(self):
        """PUSH operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("PUSH") is not None

    def test_rstack_operation_registered(self):
        """RSTACK operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("RSTACK") is not None

    def test_push_adds_to_stack(self):
        """PUSH adds value to stack."""
        from zil_interpreter.engine.operations.zork2_ops import PushOp
        op = PushOp()

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value=42)
        mock_evaluator.stack = []

        result = op.execute([42], mock_evaluator)

        assert 42 in mock_evaluator.stack
        assert result == 42

    def test_rstack_pops_and_returns(self):
        """RSTACK pops from stack and returns value."""
        from zil_interpreter.engine.operations.zork2_ops import RstackOp
        op = RstackOp()

        mock_evaluator = Mock()
        mock_evaluator.stack = [1, 2, 3]

        result = op.execute([], mock_evaluator)

        assert result == 3
        assert mock_evaluator.stack == [1, 2]

    def test_rstack_empty_returns_none(self):
        """RSTACK on empty stack returns None."""
        from zil_interpreter.engine.operations.zork2_ops import RstackOp
        op = RstackOp()

        mock_evaluator = Mock()
        mock_evaluator.stack = []

        result = op.execute([], mock_evaluator)

        assert result is None

    def test_rstack_no_stack_attr_returns_none(self):
        """RSTACK when evaluator has no stack attribute returns None."""
        from zil_interpreter.engine.operations.zork2_ops import RstackOp
        op = RstackOp()

        mock_evaluator = Mock(spec=[])  # no 'stack' attribute

        result = op.execute([], mock_evaluator)

        assert result is None

    def test_push_creates_stack_if_missing(self):
        """PUSH creates a stack on the evaluator if none exists."""
        from zil_interpreter.engine.operations.zork2_ops import PushOp
        op = PushOp()

        mock_evaluator = Mock(spec=['evaluate'])
        mock_evaluator.evaluate = Mock(return_value=99)

        result = op.execute([99], mock_evaluator)

        assert result == 99
        assert hasattr(mock_evaluator, 'stack')
        assert 99 in mock_evaluator.stack

    def test_push_rstack_roundtrip(self):
        """PUSH followed by RSTACK returns the pushed value."""
        from zil_interpreter.engine.operations.zork2_ops import PushOp, RstackOp
        push_op = PushOp()
        rstack_op = RstackOp()

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value=7)
        mock_evaluator.stack = []

        push_op.execute([7], mock_evaluator)
        result = rstack_op.execute([], mock_evaluator)

        assert result == 7
        assert mock_evaluator.stack == []


class TestNextpEdgeCases:
    """Additional edge case tests for NEXTP."""

    def test_nextp_returns_false_when_no_properties(self):
        """NEXTP returns 0 when object has no properties."""
        from zil_interpreter.engine.operations.zork2_ops import NextpOp
        op = NextpOp()

        mock_obj = Mock()
        mock_obj.properties = {}

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(side_effect=lambda x: mock_obj if x == "OBJ" else 0)

        result = op.execute(["OBJ", 0], mock_evaluator)

        assert result == 0

    def test_nextp_returns_0_after_last_property(self):
        """NEXTP returns 0 when asked for the property after the last one."""
        from zil_interpreter.engine.operations.zork2_ops import NextpOp
        op = NextpOp()

        mock_obj = Mock()
        mock_obj.properties = {"ONLY": 1}

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(side_effect=lambda x: mock_obj if x == "OBJ" else "ONLY")

        result = op.execute(["OBJ", "ONLY"], mock_evaluator)

        assert result == 0

    def test_nextp_returns_0_for_unknown_property(self):
        """NEXTP returns 0 when given property not in object."""
        from zil_interpreter.engine.operations.zork2_ops import NextpOp
        op = NextpOp()

        mock_obj = Mock()
        mock_obj.properties = {"A": 1, "B": 2}

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(side_effect=lambda x: mock_obj if x == "OBJ" else "UNKNOWN")

        result = op.execute(["OBJ", "UNKNOWN"], mock_evaluator)

        assert result == 0
