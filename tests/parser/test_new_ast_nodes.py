"""Tests for new AST node types (Tasks 1.12 and 1.13)."""
import pytest
from zil_interpreter.parser.ast_nodes import (
    LocalRef, GlobalRef, QuotedAtom, Splice, PercentEval, HashExpr, CharLiteral,
    Form, Atom
)
from zil_interpreter.parser.transformer import ZILTransformer
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestNewASTNodes:
    """Tests for new AST node types (Task 1.12)."""

    def test_local_ref_node(self):
        """LocalRef node stores variable name."""
        node = LocalRef("X")
        assert node.name == "X"

    def test_global_ref_node(self):
        """GlobalRef node stores variable name."""
        node = GlobalRef("HERE")
        assert node.name == "HERE"

    def test_quoted_atom_node(self):
        """QuotedAtom node stores atom name."""
        node = QuotedAtom("ATOM")
        assert node.name == "ATOM"

    def test_splice_node(self):
        """Splice node contains form."""
        inner = Form(Atom("LIST"), [])
        node = Splice(inner)
        assert node.form == inner

    def test_percent_eval_node(self):
        """PercentEval node contains form."""
        inner = Form(Atom("COND"), [])
        node = PercentEval(inner)
        assert node.form == inner

    def test_hash_expr_node(self):
        """HashExpr node contains type and values."""
        node = HashExpr("DECL", [Atom("X"), Atom("FIX")])
        assert node.hash_type == "DECL"
        assert len(node.values) == 2

    def test_char_literal_node(self):
        """CharLiteral node stores character."""
        node = CharLiteral("A")
        assert node.char == "A"


class TestTransformerNewNodes:
    """Tests for transformer handling new node types (Task 1.13)."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='expression', parser='lalr')

    @pytest.fixture
    def transformer(self):
        return ZILTransformer()

    def test_transform_local_ref(self, parser, transformer):
        """Transformer creates LocalRef from .VAR."""
        tree = parser.parse('.Y')
        result = transformer.transform(tree)
        assert isinstance(result, LocalRef)
        assert result.name == "Y"

    def test_transform_global_ref(self, parser, transformer):
        """Transformer creates GlobalRef from ,VAR."""
        tree = parser.parse(',HERE')
        result = transformer.transform(tree)
        assert isinstance(result, GlobalRef)
        assert result.name == "HERE"

    def test_transform_quoted_atom(self, parser, transformer):
        """Transformer creates QuotedAtom from 'ATOM."""
        tree = parser.parse("'ATOM")
        result = transformer.transform(tree)
        assert isinstance(result, QuotedAtom)
        assert result.name == "ATOM"

    def test_transform_splice(self, parser, transformer):
        """Transformer creates Splice from !<form>."""
        tree = parser.parse('!<LIST 1 2 3>')
        result = transformer.transform(tree)
        assert isinstance(result, Splice)
        assert isinstance(result.form, Form)
        assert result.form.operator.value == "LIST"

    def test_transform_percent_eval(self, parser, transformer):
        """Transformer creates PercentEval from %<form>."""
        tree = parser.parse('%<+ 1 2>')
        result = transformer.transform(tree)
        assert isinstance(result, PercentEval)
        assert isinstance(result.form, Form)
        assert result.form.operator.value == "+"

    def test_transform_hash_expr(self, parser, transformer):
        """Transformer creates HashExpr from #TYPE."""
        tree = parser.parse('#DECL')
        result = transformer.transform(tree)
        assert isinstance(result, HashExpr)
        assert result.hash_type == "DECL"

    def test_transform_hash_expr_with_values(self, parser, transformer):
        """Transformer creates HashExpr with values from #TYPE values."""
        tree = parser.parse('#BYTE 1 2 3')
        result = transformer.transform(tree)
        assert isinstance(result, HashExpr)
        assert result.hash_type == "BYTE"
        assert len(result.values) == 3

    def test_transform_char_literal(self, parser, transformer):
        """Transformer creates CharLiteral from !\\X."""
        tree = parser.parse(r'!\A')
        result = transformer.transform(tree)
        assert isinstance(result, CharLiteral)
        assert result.char == "A"

    def test_transform_complex_expression(self, parser, transformer):
        """Transformer handles complex expression with new nodes."""
        tree = parser.parse('<SET .X ,Y>')
        result = transformer.transform(tree)
        assert isinstance(result, Form)
        assert result.operator.value == "SET"
        assert isinstance(result.args[0], LocalRef)
        assert isinstance(result.args[1], GlobalRef)
