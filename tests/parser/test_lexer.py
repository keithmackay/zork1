import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


def test_lexer_recognizes_angle_brackets():
    """Test that lexer can tokenize angle brackets."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    # Should not raise
    parser.parse('<>')


def test_lexer_recognizes_routine_keyword():
    """Test that lexer recognizes ROUTINE keyword."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    result = parser.parse('<ROUTINE FOO ()>')
    assert result is not None


def test_lexer_recognizes_strings():
    """Test that lexer can tokenize quoted strings."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    result = parser.parse('"hello world"')
    assert result is not None


def test_lexer_recognizes_atoms():
    """Test that lexer recognizes atoms (identifiers)."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    result = parser.parse('FOO-BAR')
    assert result is not None
