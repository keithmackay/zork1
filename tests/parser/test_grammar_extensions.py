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


class TestFalseLiteral:
    """Tests for <> false/empty literal."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_empty_form_as_false(self, parser):
        """Parser handles <> as false literal."""
        code = '<GLOBAL FALSE-FLAG <>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_false_in_cond(self, parser):
        """Parser handles <> in conditional."""
        code = '<IF <> <RTRUE> <RFALSE>>'
        tree = parser.parse(code)
        assert tree is not None


class TestQuotedAtoms:
    """Tests for 'ATOM quoted syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_quoted_atom(self, parser):
        """Parser handles 'ATOM quoted syntax."""
        code = "<EQUAL? .X 'ATOM>"
        tree = parser.parse(code)
        assert tree is not None

    def test_quoted_atom_in_list(self, parser):
        """Parser handles quoted atom in list."""
        code = "('FOO 'BAR 'BAZ)"
        tree = parser.parse(code)
        assert tree is not None


class TestSpliceSyntax:
    """Tests for !<...> splice syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_splice_form(self, parser):
        """Parser handles !<...> splice syntax."""
        code = '<FORM PROG () !<MAPF>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_splice_in_macro(self, parser):
        """Parser handles splice in macro definition."""
        code = '<DEFMAC FOO () <FORM BAR !<LIST 1 2 3>>>'
        tree = parser.parse(code)
        assert tree is not None


class TestPercentBracketEval:
    """Tests for %<...> compile-time evaluation."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_percent_eval(self, parser):
        """Parser handles %<...> compile-time eval."""
        code = '<%<+ 1 2>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_percent_cond(self, parser):
        """Parser handles %<COND ...> conditional compilation."""
        code = '%<IF <GASSIGNED? FOO> <FOO> T>'
        tree = parser.parse(code)
        assert tree is not None


class TestHashSyntax:
    """Tests for # prefix syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_hash_decl(self, parser):
        """Parser handles #DECL type declaration."""
        code = '<ROUTINE FOO (X) #DECL ((X) FIX) .X>'
        tree = parser.parse(code)
        assert tree is not None

    def test_hash_byte(self, parser):
        """Parser handles #BYTE constant."""
        code = '<TABLE #BYTE 1 2 3>'
        tree = parser.parse(code)
        assert tree is not None


class TestCharacterLiterals:
    """Tests for backslash character literals."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_char_literal(self, parser):
        """Parser handles !\\X character literal."""
        code = r'<PRINTC !\A>'
        tree = parser.parse(code)
        assert tree is not None

    def test_newline_char(self, parser):
        """Parser handles newline character."""
        code = r'<PRINTC !\n>'
        tree = parser.parse(code)
        assert tree is not None


class TestExtendedAtoms:
    """Tests for extended atom patterns."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_atom_with_equals(self, parser):
        """Parser handles atoms with = like V-TAKE."""
        code = '<SYNTAX TAKE = V-TAKE>'
        tree = parser.parse(code)
        assert tree is not None

    def test_atom_with_colon(self, parser):
        """Parser handles atoms with : like AUX:."""
        code = '<ROUTINE FOO ("AUX" X)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_verb_question_mark(self, parser):
        """Parser handles VERB? atom."""
        code = '<VERB? TAKE>'
        tree = parser.parse(code)
        assert tree is not None

    def test_negative_number(self, parser):
        """Parser handles negative numbers."""
        code = '<SET X -1>'
        tree = parser.parse(code)
        assert tree is not None
