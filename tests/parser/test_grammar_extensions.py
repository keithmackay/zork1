"""Tests for grammar extensions including multi-line strings and variable references."""
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


class TestLocalVariableReferences:
    """Tests for .VAR local variable syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_local_var_reference(self, parser):
        """Parser handles .VAR local variable reference."""
        code = '<SET X .Y>'
        tree = parser.parse(code)
        assert tree is not None

    def test_local_var_in_expression(self, parser):
        """Parser handles local var in complex expression."""
        code = '<ADD .X .Y 1>'
        tree = parser.parse(code)
        assert tree is not None

    def test_local_var_as_argument(self, parser):
        """Parser handles local var as function argument."""
        code = '<TELL .MSG>'
        tree = parser.parse(code)
        assert tree is not None


class TestGlobalVariableReferences:
    """Tests for ,VAR global variable syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_global_var_reference(self, parser):
        """Parser handles ,VAR global variable reference."""
        code = '<SETG X ,Y>'
        tree = parser.parse(code)
        assert tree is not None

    def test_global_var_comma_syntax(self, parser):
        """Parser handles global var with comma prefix."""
        code = '<TELL ,HERE>'
        tree = parser.parse(code)
        assert tree is not None

    def test_global_constant_reference(self, parser):
        """Parser handles global constant like ,LIST."""
        code = '<MAPF ,LIST <FUNCTION () <RTRUE>>>'
        tree = parser.parse(code)
        assert tree is not None
