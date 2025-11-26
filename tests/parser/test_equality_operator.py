"""Tests for ==? equality operator."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestEqualityOperator:
    """Tests for ==? operator in ZIL grammar."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_double_equal_question(self, parser):
        """==? operator is recognized."""
        code = '<==? .V ,M-FATAL>'
        tree = parser.parse(code)
        assert tree is not None

    def test_double_equal_question_in_cond(self, parser):
        """==? in COND clause."""
        code = '<COND (<==? .X 5> <PRINT "five">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_not_equal_question(self, parser):
        """N==? operator (not equal)."""
        code = '<N==? .A .B>'
        tree = parser.parse(code)
        assert tree is not None

    def test_equality_with_numbers(self, parser):
        """==? with numeric literals."""
        code = '<==? .X 42>'
        tree = parser.parse(code)
        assert tree is not None

    def test_equality_nested(self, parser):
        """==? in nested expression."""
        code = '<COND (<==? .TYPE ,WEAPON> <DO-ATTACK>)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_not_equality_nested(self, parser):
        """N==? in conditional logic."""
        code = '<COND (<N==? .A .B> <RETURN T>)>'
        tree = parser.parse(code)
        assert tree is not None
