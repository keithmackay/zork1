"""Transformer to convert Lark parse tree to AST."""

from typing import List, Any, Optional
from lark import Transformer, Token
from zil_interpreter.parser.ast_nodes import (
    Form, Atom, String, Number, ASTNode, InsertFile,
    LocalRef, GlobalRef, QuotedAtom, Splice, PercentEval, HashExpr, CharLiteral,
    Routine, Object, Global
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

    def form(self, items: List[Any]) -> Form | InsertFile | Routine | Object | Global:
        """Transform form <operator args...>"""
        # Handle empty form <> (represents false/nil in ZIL)
        if not items:
            return Form(operator=Atom("FALSE"), args=[])

        # Check for special forms that have dedicated AST nodes
        if isinstance(items[0], Atom):
            op_name = items[0].value.upper()

            # INSERT-FILE directive
            if op_name == "INSERT-FILE":
                if len(items) > 1 and isinstance(items[1], String):
                    return InsertFile(filename=items[1].value)
                return InsertFile(filename="")

            # ROUTINE definition: <ROUTINE name (args...) body...>
            if op_name == "ROUTINE":
                if len(items) >= 2 and isinstance(items[1], Atom):
                    name = items[1].value
                    # Args are in a list (second element), body is everything after
                    args = []
                    body = []
                    if len(items) >= 3:
                        # Check if second arg is a list (parameters)
                        if isinstance(items[2], list):
                            args = [a.value if isinstance(a, Atom) else str(a) for a in items[2]]
                            body = items[3:] if len(items) > 3 else []
                        else:
                            # No parameters, all remaining items are body
                            body = items[2:]
                    return Routine(name=name, args=args, body=body)

            # OBJECT definition: <OBJECT name (properties...)>
            if op_name == "OBJECT":
                if len(items) >= 2 and isinstance(items[1], Atom):
                    name = items[1].value
                    # Properties are in remaining elements
                    properties = {}
                    # Parse property lists - typically (PROPERTY-NAME value...)
                    for i in range(2, len(items)):
                        if isinstance(items[i], list) and len(items[i]) > 0:
                            prop_name = items[i][0].value if isinstance(items[i][0], Atom) else str(items[i][0])
                            prop_values = items[i][1:]
                            properties[prop_name] = prop_values
                    return Object(name=name, properties=properties)

            # GLOBAL definition: <GLOBAL name value>
            if op_name == "GLOBAL":
                if len(items) >= 2 and isinstance(items[1], Atom):
                    name = items[1].value
                    value = items[2] if len(items) > 2 else None
                    return Global(name=name, value=value)

        # Default: generic form
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

    def quoted_expr(self, items: List[Any]) -> Any:
        """Transform quoted expression ('expr)."""
        # If the quoted thing is an atom, wrap in QuotedAtom
        # Otherwise, just return the quoted expression
        if isinstance(items[0], Atom):
            return QuotedAtom(items[0].value)
        # For forms and other expressions, return as-is (will handle in later chunks)
        return items[0]

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
        """Transform character literal (\\X or !\\X)."""
        # Extract the character after the backslash
        # Handles both \X and !\X forms
        literal = str(items[0])
        char = literal[-1]  # Last character after backslash
        return CharLiteral(char)
