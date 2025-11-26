"""ZIL language grammar definition using Lark parser."""

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | percent_eval
              | list
              | splice
              | hash_expr
              | char_literal
              | local_ref
              | global_ref
              | quoted_form
              | quoted_atom
              | atom
              | string
              | number

    form: "<" atom? expression* ">"
    percent_eval: "%" form
    list: "(" expression* ")"
    splice: "!" form
    hash_expr: "#" ATOM expression*
    char_literal: "!\\" /./

    local_ref: "." ATOM
    global_ref: "," ATOM
    quoted_form: "'" form
    quoted_atom: "'" ATOM
    atom: OPERATOR | ATOM
    string: MULTILINE_STRING
    number: SIGNED_NUMBER

    OPERATOR.2: /[=<>+\-*\/]+\?/
    ATOM: /[A-Z][A-Z0-9\-?!+*\/=:]*/i | /[0-9]+[A-Z\-?!=:]+[A-Z0-9\-?!=:]*/i | /[+\-*\/=]/
    MULTILINE_STRING: /"[^"]*"/s
    COMMENT: /;[^\n]*/

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""
