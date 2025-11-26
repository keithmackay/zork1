"""Tests for empty form handling in ZIL grammar."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestEmptyForms:
    """Tests for empty form <> and empty lists ()."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_empty_form(self, parser):
        """Empty form <> parses."""
        code = '<>'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_form_as_value(self, parser):
        """Empty form as false value."""
        code = '<SETG FLAG <>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_list(self, parser):
        """Empty list () parses."""
        code = '()'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_list_in_routine(self, parser):
        """Empty arg list in ROUTINE."""
        code = '<ROUTINE FOO () <PRINT "hi">>'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_form_in_cond(self, parser):
        """Empty form in COND clause."""
        code = '<COND (<> <PRINT "false">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_multiple_empty_forms(self, parser):
        """Multiple empty forms in expression."""
        code = '<ROUTINE TEST () <> <> <>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_nested_empty_forms(self, parser):
        """Nested structure with empty forms and lists."""
        code = '<<> () <ROUTINE X () <>>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_form_vs_empty_list(self, parser):
        """Both empty form and empty list in same expression."""
        code = '<SETG A <>> <SETG B ()>'
        tree = parser.parse(code)
        assert tree is not None
