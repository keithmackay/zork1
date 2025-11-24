"""Transformer to convert Lark parse tree to AST."""

from lark import Transformer, Token
from zil_interpreter.parser.ast_nodes import (
    Form, Atom, String, Number, ASTNode
)


class ZILTransformer(Transformer):
    """Transforms Lark parse tree into ZIL AST."""

    def atom(self, items):
        """Transform atom token."""
        return Atom(str(items[0]).upper())

    def string(self, items):
        """Transform string literal."""
        # Remove quotes
        value = str(items[0])[1:-1]
        # Handle escape sequences
        value = value.replace('\\n', '\n').replace('\\t', '\t')
        return String(value)

    def number(self, items):
        """Transform number literal."""
        value = str(items[0])
        if '.' in value:
            return Number(float(value))
        return Number(int(value))

    def form(self, items):
        """Transform form <operator args...>"""
        operator = items[0]
        args = items[1:] if len(items) > 1 else []
        return Form(operator=operator, args=args)

    def expression(self, items):
        """Pass through expression."""
        return items[0] if items else None

    def start(self, items):
        """Return list of top-level expressions."""
        return [item for item in items if item is not None]
