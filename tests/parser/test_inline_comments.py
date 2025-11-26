"""Tests for inline comment handling in ZIL grammar."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestInlineComments:
    """Tests for semicolon comments within expressions."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_inline_comment_in_list(self, parser):
        """Inline comment within parenthesized list."""
        code = '(ADJECTIVE LARGE STORM ;"-TOSSED"\n)'
        tree = parser.parse(code)
        assert tree is not None

    def test_inline_comment_in_property(self, parser):
        """Inline comment after string in property."""
        code = '(DESC "such thing" ;"[not here]"\n)'
        tree = parser.parse(code)
        assert tree is not None

    def test_inline_comment_before_close_paren(self, parser):
        """Comment immediately before closing paren."""
        code = '(A B ;comment\n)'
        tree = parser.parse(code)
        assert tree is not None

    def test_inline_comment_before_close_angle(self, parser):
        """Comment immediately before closing angle bracket."""
        code = '<FOO BAR ;comment\n>'
        tree = parser.parse(code)
        assert tree is not None

    def test_commented_out_form(self, parser):
        """Entire form commented out within expression."""
        code = '<COND (T ;<OLD-CODE>\n <NEW-CODE>)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_multiple_inline_comments(self, parser):
        """Multiple inline comments in one expression."""
        code = '(A ;first\n B ;second\n C)'
        tree = parser.parse(code)
        assert tree is not None
