"""ZIL language grammar definition using Lark parser."""

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | list
              | local_ref
              | global_ref
              | atom
              | string
              | number

    form: "<" atom? expression* ">"
    list: "(" expression* ")"

    local_ref: "." ATOM
    global_ref: "," ATOM
    atom: ATOM
    string: MULTILINE_STRING
    number: SIGNED_NUMBER

    ATOM: /[A-Z0-9][A-Z0-9\-?!]*/i
    MULTILINE_STRING: /"[^"]*"/s
    COMMENT: /;[^\n]*/

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""
