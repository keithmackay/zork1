import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR
from zil_interpreter.parser.transformer import ZILTransformer
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number


def test_transform_simple_atom():
    """Test transforming a simple atom."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('FOO')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result, Atom)
    assert result.value == "FOO"


def test_transform_string():
    """Test transforming a string literal."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('"hello"')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result, String)
    assert result.value == "hello"


def test_transform_number():
    """Test transforming a number."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('42')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result, Number)
    assert result.value == 42


def test_transform_simple_form():
    """Test transforming a simple form."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('<TELL "hello">')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result, Form)
    assert result.operator.value == "TELL"
    assert len(result.args) == 1
    assert isinstance(result.args[0], String)


def test_transform_nested_form():
    """Test transforming nested forms."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('<COND (<EQUAL? X 1> <TELL "one">)>')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result, Form)
    assert result.operator.value == "COND"
    # Verify the first arg is a list (not a Lark Tree)
    assert isinstance(result.args[0], list)
    assert len(result.args[0]) == 2
    # Verify nested forms are properly transformed
    assert isinstance(result.args[0][0], Form)
    assert result.args[0][0].operator.value == "EQUAL?"
    assert isinstance(result.args[0][1], Form)
    assert result.args[0][1].operator.value == "TELL"


def test_transform_list():
    """Test transforming a list (parenthesized expressions)."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('(1 2 3)')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    # Result should be a list, not a Lark Tree
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(item, Number) for item in result)
    assert result[0].value == 1
    assert result[1].value == 2
    assert result[2].value == 3
