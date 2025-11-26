"""Transformer to convert Lark parse tree to AST."""

from typing import List, Any, Optional
from lark import Transformer, Token
from zil_interpreter.parser.ast_nodes import (
    Form, Atom, String, Number, ASTNode,
    LocalRef, GlobalRef, QuotedAtom, Splice, PercentEval, HashExpr, CharLiteral
)


class ZILTransformer(Transformer):
    """Transforms Lark parse tree into ZIL AST."""

    def atom(self, items: List[Token]) -> Atom:
        """Transform atom token."""
        return Atom(str(items[0]).upper())

    def string(self, items: List[Token]) -> String:
        """Transform string literal."""
        # Remove quotes
        value = str(items[0])[1:-1]
        # Handle escape sequences
        value = value.replace('\\n', '\n').replace('\\t', '\t')
        return String(value)

    def number(self, items: List[Token]) -> Number:
        """Transform number literal."""
        value = str(items[0])
        if '.' in value:
            return Number(float(value))
        return Number(int(value))

    def list(self, items: List[Any]) -> List[Any]:
        """Transform list (parenthesized expressions)."""
        return [item for item in items if item is not None]

    def form(self, items: List[Any]) -> Form:
        """Transform form <operator args...>"""
        operator = items[0]
        args = items[1:] if len(items) > 1 else []
        return Form(operator=operator, args=args)

    def expression(self, items: List[Any]) -> Optional[ASTNode]:
        """Pass through expression."""
        return items[0] if items else None

    def start(self, items: List[Any]) -> List[ASTNode]:
        """Return list of top-level expressions."""
        return [item for item in items if item is not None]

    def local_ref(self, items: List[Token]) -> LocalRef:
        """Transform local variable reference (.VAR)."""
        return LocalRef(str(items[0]).upper())

    def global_ref(self, items: List[Token]) -> GlobalRef:
        """Transform global variable reference (,VAR)."""
        return GlobalRef(str(items[0]).upper())

    def quoted_atom(self, items: List[Token]) -> QuotedAtom:
        """Transform quoted atom ('ATOM)."""
        return QuotedAtom(str(items[0]).upper())

    def splice(self, items: List[Any]) -> Splice:
        """Transform splice expression (!<form>)."""
        return Splice(items[0])

    def percent_eval(self, items: List[Any]) -> PercentEval:
        """Transform compile-time evaluation (%<form>)."""
        return PercentEval(items[0])

    def hash_expr(self, items: List[Any]) -> HashExpr:
        """Transform hash expression (#TYPE values)."""
        hash_type = str(items[0]).upper()
        values = list(items[1:]) if len(items) > 1 else []
        return HashExpr(hash_type, values)

    def char_literal(self, items: List[Token]) -> CharLiteral:
        """Transform character literal (!\\X)."""
        return CharLiteral(str(items[0]))
