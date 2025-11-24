"""ZIL language grammar definition using Lark parser."""

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | list
              | atom
              | string
              | number

    form: "<" atom? expression* ">"
    list: "(" expression* ")"

    atom: ATOM
    string: ESCAPED_STRING
    number: SIGNED_NUMBER

    ATOM: /[A-Z0-9][A-Z0-9\-?!]*/i
    COMMENT: /;[^\n]*/

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""
