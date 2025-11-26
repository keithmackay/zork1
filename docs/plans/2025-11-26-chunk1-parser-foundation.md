# Chunk 1: Parser Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix ZIL grammar to parse all Zork I source files without errors.

**Architecture:** Extend Lark grammar to handle multi-line strings, variable references (`.local`, `,global`), quoted atoms, and special ZIL constructs.

**Tech Stack:** Python 3.11+, Lark parser, pytest

---

## Task 1.1: Multi-line String Support

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Create: `tests/parser/test_multiline_strings.py`

**Step 1: Write the failing test**

```python
# tests/parser/test_multiline_strings.py
"""Tests for multi-line string parsing."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestMultilineStrings:
    """Tests for multi-line string support."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_simple_multiline_string(self, parser):
        """Parser handles string spanning multiple lines."""
        code = '''"Line one
Line two
Line three"'''
        tree = parser.parse(code)
        assert tree is not None

    def test_multiline_string_in_form(self, parser):
        """Parser handles multiline string inside a form."""
        code = '''<TELL "This is
a multi-line
message.">'''
        tree = parser.parse(code)
        assert tree is not None

    def test_zork_header_comment(self, parser):
        """Parser handles Zork I file header format."""
        code = '''"ZORK1 for
	        Zork I: The Great Underground Empire
	(c) Copyright 1983 Infocom, Inc.  All Rights Reserved."

<GLOBAL SCORE 0>'''
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/Keith.MacKay/Projects/zork1/.worktrees/zork1-compiler && pytest tests/parser/test_multiline_strings.py -v`
Expected: FAIL with "No terminal matches" or similar

**Step 3: Write minimal implementation**

```python
# zil_interpreter/parser/grammar.py
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_multiline_strings.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_multiline_strings.py
git commit -m "feat(parser): add multi-line string support"
```

---

## Task 1.2: Local Variable References (.VAR)

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_multiline_strings.py` → rename to `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestLocalVariableReferences:
    """Tests for .VAR local variable syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_local_var_reference(self, parser):
        """Parser handles .VAR local variable reference."""
        code = '<SET X .Y>'
        tree = parser.parse(code)
        assert tree is not None

    def test_local_var_in_expression(self, parser):
        """Parser handles local var in complex expression."""
        code = '<+ .X .Y 1>'
        tree = parser.parse(code)
        assert tree is not None

    def test_local_var_as_argument(self, parser):
        """Parser handles local var as function argument."""
        code = '<TELL .MSG>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestLocalVariableReferences -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Update zil_interpreter/parser/grammar.py

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_grammar_extensions.py::TestLocalVariableReferences -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_grammar_extensions.py
git commit -m "feat(parser): add local variable reference syntax (.VAR)"
```

---

## Task 1.3: Global Variable References (,VAR)

**Files:**
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestGlobalVariableReferences:
    """Tests for ,VAR global variable syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_global_var_reference(self, parser):
        """Parser handles ,VAR global variable reference."""
        code = '<SETG X ,Y>'
        tree = parser.parse(code)
        assert tree is not None

    def test_global_var_comma_syntax(self, parser):
        """Parser handles global var with comma prefix."""
        code = '<TELL ,HERE>'
        tree = parser.parse(code)
        assert tree is not None

    def test_global_constant_reference(self, parser):
        """Parser handles global constant like ,LIST."""
        code = '<MAPF ,LIST <FUNCTION () <RTRUE>>>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestGlobalVariableReferences -v`
Expected: Already PASS (implemented in 1.2)

**Step 3: Verify and commit test**

```bash
git add tests/parser/test_grammar_extensions.py
git commit -m "test(parser): add global variable reference tests"
```

---

## Task 1.4: Empty List/False Literal (<>)

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestFalseLiteral:
    """Tests for <> false/empty literal."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_empty_form_as_false(self, parser):
        """Parser handles <> as false literal."""
        code = '<GLOBAL FALSE-FLAG <>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_false_in_cond(self, parser):
        """Parser handles <> in conditional."""
        code = '<COND (<> <RTRUE>)>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestFalseLiteral -v`
Expected: PASS (empty form already valid in grammar)

**Step 3: Commit test**

```bash
git add tests/parser/test_grammar_extensions.py
git commit -m "test(parser): add false literal (<>) tests"
```

---

## Task 1.5: Quoted Atoms ('ATOM)

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestQuotedAtoms:
    """Tests for 'ATOM quoted syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_quoted_atom(self, parser):
        """Parser handles 'ATOM quoted syntax."""
        code = "<TYPE? .X 'ATOM>"
        tree = parser.parse(code)
        assert tree is not None

    def test_quoted_atom_in_list(self, parser):
        """Parser handles quoted atom in list."""
        code = "('FOO 'BAR 'BAZ)"
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestQuotedAtoms -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Update zil_interpreter/parser/grammar.py - add quoted_atom rule

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | list
              | local_ref
              | global_ref
              | quoted_atom
              | atom
              | string
              | number

    form: "<" atom? expression* ">"
    list: "(" expression* ")"

    local_ref: "." ATOM
    global_ref: "," ATOM
    quoted_atom: "'" ATOM
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_grammar_extensions.py::TestQuotedAtoms -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_grammar_extensions.py
git commit -m "feat(parser): add quoted atom syntax ('ATOM)"
```

---

## Task 1.6: Splicing Syntax (!<...>)

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestSpliceSyntax:
    """Tests for !<...> splice syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_splice_form(self, parser):
        """Parser handles !<...> splice syntax."""
        code = '<FORM PROG () !<MAPF ,LIST <FUNCTION () <RTRUE>>>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_splice_in_macro(self, parser):
        """Parser handles splice in macro definition."""
        code = '<DEFMAC FOO () <FORM BAR !<LIST 1 2 3>>>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestSpliceSyntax -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Update zil_interpreter/parser/grammar.py - add splice rule

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | list
              | splice
              | local_ref
              | global_ref
              | quoted_atom
              | atom
              | string
              | number

    form: "<" atom? expression* ">"
    list: "(" expression* ")"
    splice: "!" form

    local_ref: "." ATOM
    global_ref: "," ATOM
    quoted_atom: "'" ATOM
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_grammar_extensions.py::TestSpliceSyntax -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_grammar_extensions.py
git commit -m "feat(parser): add splice syntax (!<...>)"
```

---

## Task 1.7: Percent-Bracket Evaluation (%<...>)

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestPercentBracketEval:
    """Tests for %<...> compile-time evaluation."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_percent_eval(self, parser):
        """Parser handles %<...> compile-time eval."""
        code = '<%<+ 1 2>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_percent_cond(self, parser):
        """Parser handles %<COND ...> conditional compilation."""
        code = '%<COND (<GASSIGNED? FOO> <FOO>)>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestPercentBracketEval -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Update zil_interpreter/parser/grammar.py - add percent_eval rule

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | percent_eval
              | list
              | splice
              | local_ref
              | global_ref
              | quoted_atom
              | atom
              | string
              | number

    form: "<" atom? expression* ">"
    percent_eval: "%" form
    list: "(" expression* ")"
    splice: "!" form

    local_ref: "." ATOM
    global_ref: "," ATOM
    quoted_atom: "'" ATOM
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_grammar_extensions.py::TestPercentBracketEval -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_grammar_extensions.py
git commit -m "feat(parser): add percent-bracket compile-time eval (%<...>)"
```

---

## Task 1.8: Hash Syntax (#DECL, #BYTE, etc.)

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestHashSyntax:
    """Tests for # prefix syntax."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_hash_decl(self, parser):
        """Parser handles #DECL type declaration."""
        code = '<ROUTINE FOO (X) #DECL ((X) FIX) .X>'
        tree = parser.parse(code)
        assert tree is not None

    def test_hash_byte(self, parser):
        """Parser handles #BYTE constant."""
        code = '<TABLE #BYTE 1 2 3>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestHashSyntax -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Update zil_interpreter/parser/grammar.py - add hash_expr rule

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | percent_eval
              | list
              | splice
              | hash_expr
              | local_ref
              | global_ref
              | quoted_atom
              | atom
              | string
              | number

    form: "<" atom? expression* ">"
    percent_eval: "%" form
    list: "(" expression* ")"
    splice: "!" form
    hash_expr: "#" ATOM expression*

    local_ref: "." ATOM
    global_ref: "," ATOM
    quoted_atom: "'" ATOM
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_grammar_extensions.py::TestHashSyntax -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_grammar_extensions.py
git commit -m "feat(parser): add hash syntax (#DECL, #BYTE, etc.)"
```

---

## Task 1.9: Backslash Character Literals

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestCharacterLiterals:
    """Tests for backslash character literals."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_char_literal(self, parser):
        """Parser handles !\\X character literal."""
        code = r'<PRINTC !\A>'
        tree = parser.parse(code)
        assert tree is not None

    def test_newline_char(self, parser):
        """Parser handles newline character."""
        code = r'<PRINTC !\n>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestCharacterLiterals -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Update zil_interpreter/parser/grammar.py - add char_literal rule

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
    quoted_atom: "'" ATOM
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_grammar_extensions.py::TestCharacterLiterals -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_grammar_extensions.py
git commit -m "feat(parser): add backslash character literals"
```

---

## Task 1.10: Extended ATOM Pattern

**Files:**
- Modify: `zil_interpreter/parser/grammar.py`
- Modify: `tests/parser/test_grammar_extensions.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_grammar_extensions.py

class TestExtendedAtoms:
    """Tests for extended atom patterns."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_atom_with_equals(self, parser):
        """Parser handles atoms with = like V-TAKE."""
        code = '<SYNTAX TAKE = V-TAKE>'
        tree = parser.parse(code)
        assert tree is not None

    def test_atom_with_colon(self, parser):
        """Parser handles atoms with : like AUX:."""
        code = '<ROUTINE FOO ("AUX" X)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_verb_question_mark(self, parser):
        """Parser handles VERB? atom."""
        code = '<VERB? TAKE>'
        tree = parser.parse(code)
        assert tree is not None

    def test_negative_number(self, parser):
        """Parser handles negative numbers."""
        code = '<SET X -1>'
        tree = parser.parse(code)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_grammar_extensions.py::TestExtendedAtoms -v`
Expected: Some may FAIL

**Step 3: Write minimal implementation**

```python
# Update ATOM pattern in zil_interpreter/parser/grammar.py

    ATOM: /[A-Z][A-Z0-9\-?!=:]*/i | /[0-9]+[A-Z\-?!=:]+[A-Z0-9\-?!=:]*/i
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_grammar_extensions.py::TestExtendedAtoms -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_grammar_extensions.py
git commit -m "feat(parser): extend ATOM pattern for ZIL identifiers"
```

---

## Task 1.11: Integration Test - Parse gmacros.zil

**Files:**
- Create: `tests/parser/test_zork_files.py`

**Step 1: Write the failing test**

```python
# tests/parser/test_zork_files.py
"""Integration tests for parsing Zork I ZIL files."""
import pytest
from pathlib import Path
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestZorkFileParsing:
    """Integration tests parsing actual Zork I files."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    @pytest.fixture
    def zork_dir(self):
        # Find zork1 directory relative to project root
        return Path(__file__).parent.parent.parent / "zork1"

    def test_parse_gmacros_header(self, parser, zork_dir):
        """Parser handles gmacros.zil header."""
        gmacros = zork_dir / "gmacros.zil"
        if not gmacros.exists():
            pytest.skip("zork1/gmacros.zil not found")

        content = gmacros.read_text()
        # Try parsing first 500 chars (header + initial forms)
        header = content[:500]
        tree = parser.parse(header)
        assert tree is not None

    def test_parse_gglobals(self, parser, zork_dir):
        """Parser handles gglobals.zil."""
        gglobals = zork_dir / "gglobals.zil"
        if not gglobals.exists():
            pytest.skip("zork1/gglobals.zil not found")

        content = gglobals.read_text()
        tree = parser.parse(content)
        assert tree is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_zork_files.py -v`
Expected: May FAIL on complex syntax

**Step 3: Iterate on grammar fixes**

Based on failures, add additional grammar rules as needed.

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_zork_files.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/parser/test_zork_files.py
git commit -m "test(parser): add Zork I file parsing integration tests"
```

---

## Task 1.12: Update AST Nodes for New Syntax

**Files:**
- Modify: `zil_interpreter/parser/ast_nodes.py`
- Create: `tests/parser/test_ast_nodes.py`

**Step 1: Write the failing test**

```python
# tests/parser/test_ast_nodes.py
"""Tests for AST node types."""
import pytest
from zil_interpreter.parser.ast_nodes import (
    LocalRef, GlobalRef, QuotedAtom, Splice, PercentEval, HashExpr, CharLiteral
)


class TestNewASTNodes:
    """Tests for new AST node types."""

    def test_local_ref_node(self):
        """LocalRef node stores variable name."""
        node = LocalRef("X")
        assert node.name == "X"
        assert node.node_type == "local_ref"

    def test_global_ref_node(self):
        """GlobalRef node stores variable name."""
        node = GlobalRef("HERE")
        assert node.name == "HERE"
        assert node.node_type == "global_ref"

    def test_quoted_atom_node(self):
        """QuotedAtom node stores atom name."""
        node = QuotedAtom("ATOM")
        assert node.name == "ATOM"
        assert node.node_type == "quoted_atom"

    def test_splice_node(self):
        """Splice node contains form."""
        from zil_interpreter.parser.ast_nodes import Form, Atom
        inner = Form(Atom("LIST"), [])
        node = Splice(inner)
        assert node.form == inner
        assert node.node_type == "splice"

    def test_percent_eval_node(self):
        """PercentEval node contains form."""
        from zil_interpreter.parser.ast_nodes import Form, Atom
        inner = Form(Atom("COND"), [])
        node = PercentEval(inner)
        assert node.form == inner
        assert node.node_type == "percent_eval"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_ast_nodes.py -v`
Expected: FAIL with ImportError

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/parser/ast_nodes.py

@dataclass
class LocalRef:
    """Reference to local variable (.VAR)."""
    name: str
    node_type: str = "local_ref"


@dataclass
class GlobalRef:
    """Reference to global variable (,VAR)."""
    name: str
    node_type: str = "global_ref"


@dataclass
class QuotedAtom:
    """Quoted atom ('ATOM)."""
    name: str
    node_type: str = "quoted_atom"


@dataclass
class Splice:
    """Splice expression (!<form>)."""
    form: Any
    node_type: str = "splice"


@dataclass
class PercentEval:
    """Compile-time evaluation (%<form>)."""
    form: Any
    node_type: str = "percent_eval"


@dataclass
class HashExpr:
    """Hash expression (#TYPE value)."""
    hash_type: str
    values: List[Any]
    node_type: str = "hash_expr"


@dataclass
class CharLiteral:
    """Character literal (!\\X)."""
    char: str
    node_type: str = "char_literal"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_ast_nodes.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/ast_nodes.py tests/parser/test_ast_nodes.py
git commit -m "feat(parser): add AST nodes for new syntax types"
```

---

## Task 1.13: Update Transformer for New Nodes

**Files:**
- Modify: `zil_interpreter/parser/transformer.py`
- Modify: `tests/parser/test_ast_nodes.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_ast_nodes.py

from zil_interpreter.parser.transformer import ZILTransformer
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestTransformerNewNodes:
    """Tests for transformer handling new node types."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    @pytest.fixture
    def transformer(self):
        return ZILTransformer()

    def test_transform_local_ref(self, parser, transformer):
        """Transformer creates LocalRef from .VAR."""
        tree = parser.parse('<SET X .Y>')
        result = transformer.transform(tree)
        # Find the LocalRef in the result
        assert any(isinstance(getattr(n, 'node_type', None), str)
                   and getattr(n, 'node_type', None) == 'local_ref'
                   for n in self._flatten(result))

    def test_transform_global_ref(self, parser, transformer):
        """Transformer creates GlobalRef from ,VAR."""
        tree = parser.parse('<TELL ,HERE>')
        result = transformer.transform(tree)
        assert result is not None

    def _flatten(self, obj):
        """Flatten nested structure for testing."""
        if hasattr(obj, '__iter__') and not isinstance(obj, str):
            for item in obj:
                yield from self._flatten(item)
        yield obj
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_ast_nodes.py::TestTransformerNewNodes -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/parser/transformer.py

from zil_interpreter.parser.ast_nodes import (
    LocalRef, GlobalRef, QuotedAtom, Splice, PercentEval, HashExpr, CharLiteral
)

class ZILTransformer(Transformer):
    # ... existing methods ...

    def local_ref(self, items):
        return LocalRef(str(items[0]))

    def global_ref(self, items):
        return GlobalRef(str(items[0]))

    def quoted_atom(self, items):
        return QuotedAtom(str(items[0]))

    def splice(self, items):
        return Splice(items[0])

    def percent_eval(self, items):
        return PercentEval(items[0])

    def hash_expr(self, items):
        return HashExpr(str(items[0]), list(items[1:]))

    def char_literal(self, items):
        return CharLiteral(str(items[0]))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_ast_nodes.py::TestTransformerNewNodes -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/transformer.py tests/parser/test_ast_nodes.py
git commit -m "feat(parser): add transformer methods for new node types"
```

---

## Task 1.14: Final Integration - Parse All Zork Files

**Files:**
- Modify: `tests/parser/test_zork_files.py`

**Step 1: Write the failing test**

```python
# Add to tests/parser/test_zork_files.py

    def test_parse_all_zork_files(self, parser, zork_dir):
        """Parser handles all Zork I ZIL files."""
        if not zork_dir.exists():
            pytest.skip("zork1 directory not found")

        zil_files = [
            "zork1.zil",
            "gmacros.zil",
            "gsyntax.zil",
            "gparser.zil",
            "gverbs.zil",
            "gglobals.zil",
            "gmain.zil",
            "gclock.zil",
            "1dungeon.zil",
            "1actions.zil",
        ]

        errors = []
        for filename in zil_files:
            filepath = zork_dir / filename
            if not filepath.exists():
                continue
            try:
                content = filepath.read_text()
                parser.parse(content)
            except Exception as e:
                errors.append(f"{filename}: {e}")

        if errors:
            pytest.fail(f"Failed to parse files:\n" + "\n".join(errors))
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_zork_files.py::TestZorkFileParsing::test_parse_all_zork_files -v`
Expected: FAIL (likely needs more grammar fixes)

**Step 3: Iterate until passing**

Add any missing grammar rules based on parse errors.

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_zork_files.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_zork_files.py
git commit -m "feat(parser): complete grammar for all Zork I files"
```

---

## Task 1.15: Register Chunk 1 Complete

**Step 1: Run full test suite**

```bash
cd /Users/Keith.MacKay/Projects/zork1/.worktrees/zork1-compiler
pytest tests/ -v
```

**Step 2: Verify no regressions**

All existing tests should still pass.

**Step 3: Final commit**

```bash
git add -A
git commit -m "feat(parser): complete Chunk 1 - Parser Foundation

- Multi-line string support
- Local/global variable references (.VAR, ,VAR)
- Quoted atoms ('ATOM)
- Splice syntax (!<...>)
- Percent-bracket eval (%<...>)
- Hash syntax (#DECL, etc.)
- Character literals
- Extended ATOM pattern
- New AST nodes and transformer methods
- Integration tests for all Zork I files"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1.1 | Multi-line strings | 3 |
| 1.2 | Local variable refs | 3 |
| 1.3 | Global variable refs | 3 |
| 1.4 | False literal | 2 |
| 1.5 | Quoted atoms | 2 |
| 1.6 | Splice syntax | 2 |
| 1.7 | Percent-bracket | 2 |
| 1.8 | Hash syntax | 2 |
| 1.9 | Character literals | 2 |
| 1.10 | Extended ATOMs | 4 |
| 1.11 | Parse gmacros | 2 |
| 1.12 | New AST nodes | 5 |
| 1.13 | Transformer | 2 |
| 1.14 | Parse all files | 1 |
| 1.15 | Final verification | - |

**Total: 15 tasks, ~35 new tests**
