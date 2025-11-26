"""Tests for multi-line string parsing."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestMultilineStrings:
    """Tests for multi-line string support."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_simple_multiline_string(self, parser):
        """Parser handles string spanning multiple lines."""
        code = '''"Line one
Line two
Line three"'''
        tree = parser.parse(code)
        assert tree is not None

    def test_multiline_string_in_form(self, parser):
        """Parser handles multiline string inside a form."""
        code = '''<TELL "This is
a multi-line
message.">'''
        tree = parser.parse(code)
        assert tree is not None

    def test_zork_header_comment(self, parser):
        """Parser handles Zork I file header format."""
        code = '''"ZORK1 for
	        Zork I: The Great Underground Empire
	(c) Copyright 1983 Infocom, Inc.  All Rights Reserved."

<GLOBAL SCORE 0>'''
        tree = parser.parse(code)
        assert tree is not None
