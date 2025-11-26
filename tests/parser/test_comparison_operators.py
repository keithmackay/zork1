"""Tests for all ZIL comparison operators."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestComparisonOperators:
    """Tests for all comparison operators."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    @pytest.mark.parametrize("op", [
        "=?",      # equal
        "==?",     # identical
        "N==?",    # not identical
        "L?",      # less than
        "L=?",     # less or equal
        "G?",      # greater than
        "G=?",     # greater or equal
        "0?",      # is zero
        "1?",      # is one
    ])
    def test_comparison_operators(self, parser, op):
        """Each comparison operator parses correctly."""
        code = f'<{op} .X .Y>'
        tree = parser.parse(code)
        assert tree is not None

    def test_less_than_question(self, parser):
        """<? less-than operator."""
        code = '<<? .A .B>'
        tree = parser.parse(code)
        assert tree is not None

    def test_greater_than_question(self, parser):
        """>? greater-than operator."""
        code = '<>? .A .B>'
        tree = parser.parse(code)
        assert tree is not None

    def test_equal_in_cond(self, parser):
        """=? in COND clause."""
        code = '<COND (<=? .X 5> <PRINT "equal">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_less_than_in_cond(self, parser):
        """L? in COND clause."""
        code = '<COND (<L? .X 10> <PRINT "less">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_greater_than_in_cond(self, parser):
        """G? in COND clause."""
        code = '<COND (<G? .X 10> <PRINT "greater">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_less_or_equal_in_cond(self, parser):
        """L=? in COND clause."""
        code = '<COND (<L=? .X 10> <PRINT "less or equal">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_greater_or_equal_in_cond(self, parser):
        """G=? in COND clause."""
        code = '<COND (<G=? .X 10> <PRINT "greater or equal">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_zero_check(self, parser):
        """0? checks if value is zero."""
        code = '<COND (<0? .COUNT> <PRINT "empty">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_one_check(self, parser):
        """1? checks if value is one."""
        code = '<COND (<1? .COUNT> <PRINT "single">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_zero_with_local_ref(self, parser):
        """0? with local variable reference."""
        code = '<0? .X>'
        tree = parser.parse(code)
        assert tree is not None

    def test_one_with_global_ref(self, parser):
        """1? with global variable reference."""
        code = '<1? ,FLAG>'
        tree = parser.parse(code)
        assert tree is not None

    def test_nested_comparisons(self, parser):
        """Nested comparison operators."""
        code = '<COND (<G? .A .B> <L? .C .D>)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_comparison_with_numbers(self, parser):
        """Comparison operators with numeric literals."""
        code = '<L? 5 10>'
        tree = parser.parse(code)
        assert tree is not None

    def test_angle_bracket_operators(self, parser):
        """Both angle bracket style operators."""
        code = '''
        <COND (<<? .A .B> <PRINT "less">)
              (<>? .C .D> <PRINT "greater">)>
        '''
        tree = parser.parse(code)
        assert tree is not None

    def test_all_operators_in_routine(self, parser):
        """All operators used in a ROUTINE."""
        code = '''
        <ROUTINE TEST-OPS (.X .Y)
            <COND (<=? .X .Y> <PRINT "equal">)
                  (<L? .X .Y> <PRINT "less">)
                  (<G? .X .Y> <PRINT "greater">)
                  (<L=? .X .Y> <PRINT "less-equal">)
                  (<G=? .X .Y> <PRINT "greater-equal">)
                  (<0? .X> <PRINT "zero">)
                  (<1? .Y> <PRINT "one">)>>
        '''
        tree = parser.parse(code)
        assert tree is not None
