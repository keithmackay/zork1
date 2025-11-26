"""ZIL language grammar definition using Lark parser."""

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | percent_eval
              | list
              | splice
              | hash_expr
              | char_literal
              | quoted_expr
              | local_ref
              | global_ref
              | atom
              | string
              | number
              | comment_expr

    form: "<" atom? expression* ">"
    percent_eval: "%" form
    list: "(" expression* ")"
    splice: "!" form
          | "!" local_ref
          | "!" global_ref
    hash_expr: "#" ATOM expression*
    char_literal: /[!]?\\./

    comment_expr: SEMICOLON expression

    local_ref: "." ATOM
    global_ref: "," ATOM
    quoted_expr: "'" expression
    atom: OPERATOR | ATOM
    string: ESCAPED_STRING
    number: SIGNED_NUMBER

    SEMICOLON: ";"
    OPERATOR.2: /N?==\?|[LG]=\?|[LG01]\?|<=\?|>=\?|=\?|>\?|<\?/
    ATOM: /\$?[A-Z][A-Z0-9\-?!+*\/=:]*/i | /[0-9]+[A-Z\-?!=:]+[A-Z0-9\-?!=:]*/i | /[+\-*\/=](?!\?)/
    ESCAPED_STRING: /"([^"\\]|\\.)*"/s
    STRING_COMMENT: /;"([^"\\]|\\.)*"/s
    LINE_COMMENT: /;[^\n<\(\.,'][^\n]*/
    FORMFEED: /\^L/

    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    %ignore STRING_COMMENT
    %ignore LINE_COMMENT
    %ignore FORMFEED
"""
