"""TELL macro implementation."""
from typing import List, Any
from ..parser.ast_nodes import Form, Atom, String, GlobalRef, LocalRef


def expand_tell(args: List[Any]) -> Form:
    """Expand TELL macro to PROG with print statements.

    Args:
        args: Arguments to TELL macro

    Returns:
        Expanded Form: <PROG () <PRINTI ...> ...>

    Expansion rules:
    - "string" → <PRINTI "string">
    - CR or CRLF → <CRLF>
    - D obj or DESC obj or O obj or OBJ obj → <PRINTD obj>
    - N num or NUM num → <PRINTN num>
    - C char or CHR char or CHAR char → <PRINTC char>
    - A obj or AN obj → <PRINTA obj>
    - <form> → <PRINT <form>>
    - Unknown indicator with obj → <PRINT <GETP obj indicator>>
    """
    body = []
    i = 0

    while i < len(args):
        arg = args[i]

        if isinstance(arg, String):
            # String → <PRINTI "string">
            body.append(Form(Atom("PRINTI"), [arg]))
            i += 1

        elif isinstance(arg, Atom):
            name = arg.value.upper()
            if name in ("CR", "CRLF"):
                # CR/CRLF → <CRLF>
                body.append(Form(Atom("CRLF"), []))
                i += 1
            elif name in ("D", "DESC", "O", "OBJ"):
                # D obj → <PRINTD obj>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTD"), [args[i]]))
                    i += 1
            elif name in ("N", "NUM"):
                # N num → <PRINTN num>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTN"), [args[i]]))
                    i += 1
            elif name in ("C", "CHR", "CHAR"):
                # C char → <PRINTC char>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTC"), [args[i]]))
                    i += 1
            elif name in ("A", "AN"):
                # A obj → <PRINTA obj>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTA"), [args[i]]))
                    i += 1
            else:
                # Unknown indicator - treat as property lookup
                # indicator obj → <PRINT <GETP obj indicator>>
                i += 1
                if i < len(args):
                    obj = args[i]
                    body.append(Form(Atom("PRINT"), [
                        Form(Atom("GETP"), [obj, arg])
                    ]))
                    i += 1
                else:
                    # Standalone atom not recognized as indicator
                    # Just treat it as an expression to print
                    body.append(Form(Atom("PRINT"), [arg]))
        elif isinstance(arg, Form):
            # Form expression → <PRINT expr>
            body.append(Form(Atom("PRINT"), [arg]))
            i += 1
        else:
            # Any other expression (GlobalRef, LocalRef, Number, etc.) → <PRINT expr>
            body.append(Form(Atom("PRINT"), [arg]))
            i += 1

    # Wrap in PROG with empty parameter list
    return Form(Atom("PROG"), [[], *body])
