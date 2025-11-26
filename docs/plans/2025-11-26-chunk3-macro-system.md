# Chunk 3: Macro System - TDD Implementation Plan

**Goal:** Implement compile-time macro expansion for ZIL
**Branch:** `feature/zork1-macros`
**Approach:** TDD (Red → Green → Refactor)

---

## Current State

- All 10 Zork I files parse successfully
- FileProcessor loads and merges all files
- **565 tests passing**
- **Missing:** Compile-time macro expansion

## Macro System Overview

From `gmacros.zil`, Zork I defines 15 macros:
- **TELL** - Text output (1,086 uses, most critical)
- **VERB?**, **PRSO?**, **PRSI?**, **ROOM?** - Parser checks
- **BSET**, **BCLEAR**, **BSET?** - Flag operations
- **ENABLE**, **DISABLE** - Interrupt control
- **PROB**, **RFATAL**, **FLAMING?**, **OPENABLE?**, **ABS** - Utilities

### DEFMAC Syntax Patterns

```zil
; Simple macro with quoted param
<DEFMAC ENABLE ('INT) <FORM PUT .INT ,C-ENABLED? 1>>

; ARGS captures all remaining arguments
<DEFMAC TELL ("ARGS" A) <FORM PROG () ...>>

; Optional parameters
<DEFMAC PROB ('BASE? "OPTIONAL" 'LOSER?) ...>
```

### Parameter Types
- `'param` - Quoted (receives unevaluated form)
- `"ARGS"` - Captures all remaining args as list
- `"OPTIONAL"` - Following params are optional
- `"AUX"` - Local variables (not params)

---

## Implementation Tasks

### Task 3.1: Macro Definition AST Node

**Test file:** `tests/compiler/test_macro_definition.py`

```python
"""Tests for DEFMAC parsing and AST representation."""
import pytest
from zil_interpreter.parser.ast_nodes import MacroDef
from zil_interpreter.compiler.file_processor import FileProcessor


class TestMacroDefinition:
    """Tests for parsing DEFMAC forms."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_simple_macro_definition(self, processor, tmp_path):
        """Simple macro creates MacroDef node."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC ENABLE (\'INT) <FORM PUT .INT ,C-ENABLED? 1>>'
        )
        result = processor.load_file("test.zil")
        assert len(result) == 1
        assert isinstance(result[0], MacroDef)
        assert result[0].name == "ENABLE"

    def test_macro_with_args(self, processor, tmp_path):
        """ARGS parameter captures remaining arguments."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC VERB? ("ARGS" ATMS) <MULTIFROB PRSA .ATMS>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert macro.name == "VERB?"
        assert "ARGS" in [p.type for p in macro.params]

    def test_macro_with_optional(self, processor, tmp_path):
        """Optional parameters parsed correctly."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC PROB (\'BASE? "OPTIONAL" \'LOSER?) <FORM G? .BASE? 5>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert len(macro.params) == 2
        assert macro.params[1].optional is True
```

**Implementation:** Add `MacroDef` AST node and update transformer.

```python
# In ast_nodes.py
@dataclass
class MacroParam:
    """Macro parameter definition."""
    name: str
    type: str = "required"  # "required", "optional", "args", "aux"
    quoted: bool = False

@dataclass
class MacroDef(ASTNode):
    """DEFMAC macro definition."""
    name: str
    params: List[MacroParam]
    body: Any  # The macro body (usually a FORM)
```

**Verification:** `pytest tests/compiler/test_macro_definition.py -v`

---

### Task 3.2: Macro Registry

**Test file:** `tests/compiler/test_macro_registry.py`

```python
"""Tests for macro registry."""
import pytest
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import MacroDef, MacroParam, Form, Atom


class TestMacroRegistry:
    """Tests for macro storage and lookup."""

    @pytest.fixture
    def registry(self):
        return MacroRegistry()

    def test_register_macro(self, registry):
        """Can register a macro definition."""
        macro = MacroDef(
            name="ENABLE",
            params=[MacroParam("INT", quoted=True)],
            body=Form(Atom("FORM"), [Atom("PUT")])
        )
        registry.register(macro)
        assert registry.has("ENABLE")

    def test_lookup_macro(self, registry):
        """Can retrieve registered macro."""
        macro = MacroDef(name="TEST", params=[], body=None)
        registry.register(macro)
        result = registry.get("TEST")
        assert result.name == "TEST"

    def test_case_insensitive_lookup(self, registry):
        """Macro lookup is case-insensitive."""
        macro = MacroDef(name="ENABLE", params=[], body=None)
        registry.register(macro)
        assert registry.has("enable")
        assert registry.has("Enable")
        assert registry.get("ENABLE") is registry.get("enable")

    def test_not_found_returns_none(self, registry):
        """Unknown macro returns None."""
        assert registry.get("UNKNOWN") is None
        assert not registry.has("UNKNOWN")

    def test_builtin_macros_available(self, registry):
        """Registry has built-in macros."""
        # TELL should be available as built-in
        assert registry.has("TELL")
```

**Implementation:** `zil_interpreter/compiler/macro_registry.py`

```python
"""Macro registry for ZIL compilation."""
from typing import Dict, Optional
from ..parser.ast_nodes import MacroDef


class MacroRegistry:
    """Registry for macro definitions."""

    def __init__(self):
        self._macros: Dict[str, MacroDef] = {}
        self._register_builtins()

    def _register_builtins(self):
        """Register built-in macros like TELL."""
        # Built-in macros will be added here
        pass

    def register(self, macro: MacroDef) -> None:
        """Register a macro definition."""
        self._macros[macro.name.upper()] = macro

    def get(self, name: str) -> Optional[MacroDef]:
        """Get macro by name (case-insensitive)."""
        return self._macros.get(name.upper())

    def has(self, name: str) -> bool:
        """Check if macro exists."""
        return name.upper() in self._macros
```

**Verification:** `pytest tests/compiler/test_macro_registry.py -v`

---

### Task 3.3: TELL Macro - Basic String Output

**Test file:** `tests/compiler/test_tell_macro.py`

```python
"""Tests for TELL macro expansion."""
import pytest
from zil_interpreter.compiler.tell_macro import expand_tell
from zil_interpreter.parser.ast_nodes import Form, Atom, String


class TestTellMacroBasic:
    """Tests for basic TELL expansion."""

    def test_single_string(self):
        """TELL with single string expands to PRINTI."""
        # <TELL "Hello">
        args = [String("Hello")]
        result = expand_tell(args)
        # Should expand to <PROG () <PRINTI "Hello">>
        assert result.operator.value == "PROG"
        body = result.args[1]  # First arg is (), second is body
        assert body.operator.value == "PRINTI"
        assert body.args[0].value == "Hello"

    def test_multiple_strings(self):
        """TELL with multiple strings creates multiple PRINTI."""
        # <TELL "Hello " "World">
        args = [String("Hello "), String("World")]
        result = expand_tell(args)
        # <PROG () <PRINTI "Hello "> <PRINTI "World">>
        assert result.operator.value == "PROG"
        assert len(result.args) == 3  # () + 2 PRINTI forms

    def test_crlf_indicator(self):
        """CR/CRLF expands to CRLF form."""
        # <TELL "Hi" CR>
        args = [String("Hi"), Atom("CR")]
        result = expand_tell(args)
        # <PROG () <PRINTI "Hi"> <CRLF>>
        last_form = result.args[-1]
        assert last_form.operator.value == "CRLF"

    def test_empty_tell(self):
        """Empty TELL expands to empty PROG."""
        args = []
        result = expand_tell(args)
        assert result.operator.value == "PROG"
        assert len(result.args) == 1  # Just the ()
```

**Implementation:** `zil_interpreter/compiler/tell_macro.py`

```python
"""TELL macro implementation."""
from typing import List, Any
from ..parser.ast_nodes import Form, Atom, String, GlobalRef, LocalRef


def expand_tell(args: List[Any]) -> Form:
    """Expand TELL macro to PROG with print statements.

    Args:
        args: Arguments to TELL macro

    Returns:
        Expanded Form: <PROG () <PRINTI ...> ...>
    """
    body = []
    i = 0

    while i < len(args):
        arg = args[i]

        if isinstance(arg, String):
            # String -> <PRINTI "string">
            body.append(Form(Atom("PRINTI"), [arg]))
            i += 1

        elif isinstance(arg, Atom):
            name = arg.value.upper()
            if name in ("CR", "CRLF"):
                # CR/CRLF -> <CRLF>
                body.append(Form(Atom("CRLF"), []))
                i += 1
            elif name in ("D", "DESC", "O", "OBJ"):
                # D obj -> <PRINTD obj>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTD"), [args[i]]))
                    i += 1
            elif name in ("N", "NUM"):
                # N num -> <PRINTN num>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTN"), [args[i]]))
                    i += 1
            elif name in ("C", "CHR", "CHAR"):
                # C char -> <PRINTC char>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTC"), [args[i]]))
                    i += 1
            elif name in ("A", "AN"):
                # A obj -> <PRINTA obj>
                i += 1
                if i < len(args):
                    body.append(Form(Atom("PRINTA"), [args[i]]))
                    i += 1
            else:
                # Unknown indicator - treat as property lookup
                i += 1
                if i < len(args):
                    # <PRINT <GETP obj property>>
                    obj = args[i]
                    body.append(Form(Atom("PRINT"), [
                        Form(Atom("GETP"), [obj, arg])
                    ]))
                    i += 1
        else:
            # Form/expression -> <PRINT expr>
            body.append(Form(Atom("PRINT"), [arg]))
            i += 1

    # Wrap in PROG
    return Form(Atom("PROG"), [[], *body])
```

**Verification:** `pytest tests/compiler/test_tell_macro.py -v`

---

### Task 3.4: TELL Macro - Object Indicators

**Test file:** `tests/compiler/test_tell_indicators.py`

```python
"""Tests for TELL macro indicators (D, N, C, A)."""
import pytest
from zil_interpreter.compiler.tell_macro import expand_tell
from zil_interpreter.parser.ast_nodes import Form, Atom, String, GlobalRef


class TestTellIndicators:
    """Tests for TELL indicator expansion."""

    def test_d_indicator(self):
        """D expands to PRINTD."""
        # <TELL D ,LAMP>
        args = [Atom("D"), GlobalRef("LAMP")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTD"

    def test_desc_indicator(self):
        """DESC is synonym for D."""
        args = [Atom("DESC"), GlobalRef("LAMP")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTD"

    def test_n_indicator(self):
        """N expands to PRINTN."""
        # <TELL N .COUNT>
        args = [Atom("N"), Form(Atom("RANDOM"), [Atom("10")])]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTN"

    def test_c_indicator(self):
        """C expands to PRINTC."""
        args = [Atom("C"), Atom("65")]  # ASCII 'A'
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTC"

    def test_a_indicator(self):
        """A expands to PRINTA (article)."""
        args = [Atom("A"), GlobalRef("LAMP")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINTA"

    def test_property_indicator(self):
        """Unknown indicator treated as property lookup."""
        # <TELL LDESC ,TROLL>  -> <PRINT <GETP ,TROLL LDESC>>
        args = [Atom("LDESC"), GlobalRef("TROLL")]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINT"
        getp = body.args[0]
        assert getp.operator.value == "GETP"
```

**Verification:** `pytest tests/compiler/test_tell_indicators.py -v`

---

### Task 3.5: TELL Macro - Mixed Content

**Test file:** `tests/compiler/test_tell_mixed.py`

```python
"""Tests for TELL with mixed content types."""
import pytest
from zil_interpreter.compiler.tell_macro import expand_tell
from zil_interpreter.parser.ast_nodes import Form, Atom, String, GlobalRef


class TestTellMixed:
    """Tests for complex TELL expansions."""

    def test_string_and_object(self):
        """String followed by D indicator."""
        # <TELL "The " D ,LAMP " is here.">
        args = [
            String("The "),
            Atom("D"), GlobalRef("LAMP"),
            String(" is here.")
        ]
        result = expand_tell(args)
        # <PROG () <PRINTI "The "> <PRINTD ,LAMP> <PRINTI " is here.">>
        assert len(result.args) == 4  # () + 3 prints
        assert result.args[1].operator.value == "PRINTI"
        assert result.args[2].operator.value == "PRINTD"
        assert result.args[3].operator.value == "PRINTI"

    def test_full_sentence_with_cr(self):
        """Complete sentence with CR."""
        # <TELL "You see a " D ,PRSO " here." CR>
        args = [
            String("You see a "),
            Atom("D"), GlobalRef("PRSO"),
            String(" here."),
            Atom("CR")
        ]
        result = expand_tell(args)
        assert len(result.args) == 5  # () + 4 forms
        assert result.args[-1].operator.value == "CRLF"

    def test_expression_argument(self):
        """Form expression wrapped in PRINT."""
        # <TELL <GET-DESC ,LAMP>>
        args = [Form(Atom("GET-DESC"), [GlobalRef("LAMP")])]
        result = expand_tell(args)
        body = result.args[1]
        assert body.operator.value == "PRINT"
        assert body.args[0].operator.value == "GET-DESC"

    def test_multiple_numbers(self):
        """Multiple N indicators."""
        # <TELL "Score: " N ,SCORE " Moves: " N ,MOVES CR>
        args = [
            String("Score: "),
            Atom("N"), GlobalRef("SCORE"),
            String(" Moves: "),
            Atom("N"), GlobalRef("MOVES"),
            Atom("CR")
        ]
        result = expand_tell(args)
        assert len(result.args) == 6  # () + 5 forms
```

**Verification:** `pytest tests/compiler/test_tell_mixed.py -v`

---

### Task 3.6: Macro Expander

**Test file:** `tests/compiler/test_macro_expander.py`

```python
"""Tests for macro expansion engine."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, String, GlobalRef


class TestMacroExpander:
    """Tests for AST-to-AST macro expansion."""

    @pytest.fixture
    def expander(self):
        registry = MacroRegistry()
        return MacroExpander(registry)

    def test_expand_tell(self, expander):
        """TELL macro is expanded."""
        # <TELL "Hello" CR>
        form = Form(Atom("TELL"), [String("Hello"), Atom("CR")])
        result = expander.expand(form)
        assert result.operator.value == "PROG"

    def test_non_macro_unchanged(self, expander):
        """Non-macro forms pass through unchanged."""
        form = Form(Atom("PRINT"), [String("Hello")])
        result = expander.expand(form)
        assert result.operator.value == "PRINT"

    def test_nested_expansion(self, expander):
        """Macros in nested forms are expanded."""
        # <COND (T <TELL "Yes" CR>)>
        inner = Form(Atom("TELL"), [String("Yes"), Atom("CR")])
        form = Form(Atom("COND"), [[Atom("T"), inner]])
        result = expander.expand(form)
        # Inner TELL should be expanded
        expanded_inner = result.args[0][1]
        assert expanded_inner.operator.value == "PROG"

    def test_expand_routine_body(self, expander):
        """Routine bodies have macros expanded."""
        from zil_interpreter.parser.ast_nodes import Routine
        routine = Routine(
            name="TEST",
            args=[],
            body=[Form(Atom("TELL"), [String("Test"), Atom("CR")])]
        )
        result = expander.expand_routine(routine)
        assert result.body[0].operator.value == "PROG"
```

**Implementation:** `zil_interpreter/compiler/macro_expander.py`

```python
"""Macro expansion engine."""
from typing import Any, List
from .macro_registry import MacroRegistry
from .tell_macro import expand_tell
from ..parser.ast_nodes import Form, Atom, Routine, Object, Global


class MacroExpander:
    """Expands macros in ZIL AST."""

    def __init__(self, registry: MacroRegistry):
        self.registry = registry
        self._builtin_expanders = {
            "TELL": expand_tell,
        }

    def expand(self, node: Any) -> Any:
        """Recursively expand macros in AST node."""
        if isinstance(node, Form):
            return self._expand_form(node)
        elif isinstance(node, list):
            return [self.expand(item) for item in node]
        elif isinstance(node, Routine):
            return self.expand_routine(node)
        else:
            return node

    def _expand_form(self, form: Form) -> Any:
        """Expand macros in a form."""
        if not isinstance(form.operator, Atom):
            return form

        name = form.operator.value.upper()

        # Check for built-in macro
        if name in self._builtin_expanders:
            expanded = self._builtin_expanders[name](form.args)
            return self.expand(expanded)  # Recursively expand result

        # Check for user-defined macro
        macro = self.registry.get(name)
        if macro:
            expanded = self._expand_user_macro(macro, form.args)
            return self.expand(expanded)

        # Not a macro - expand children
        expanded_args = [self.expand(arg) for arg in form.args]
        return Form(form.operator, expanded_args)

    def expand_routine(self, routine: Routine) -> Routine:
        """Expand macros in routine body."""
        expanded_body = [self.expand(form) for form in routine.body]
        return Routine(routine.name, routine.args, expanded_body)
```

**Verification:** `pytest tests/compiler/test_macro_expander.py -v`

---

### Task 3.7: Simple Macro Expansion (ENABLE, DISABLE)

**Test file:** `tests/compiler/test_simple_macros.py`

```python
"""Tests for simple macro expansions."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, GlobalRef


class TestSimpleMacros:
    """Tests for simple single-form macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_enable_macro(self, expander):
        """ENABLE expands to PUT form."""
        # <ENABLE ,LAMP-INT>
        form = Form(Atom("ENABLE"), [GlobalRef("LAMP-INT")])
        result = expander.expand(form)
        # <PUT ,LAMP-INT ,C-ENABLED? 1>
        assert result.operator.value == "PUT"

    def test_disable_macro(self, expander):
        """DISABLE expands to PUT form."""
        # <DISABLE ,LAMP-INT>
        form = Form(Atom("DISABLE"), [GlobalRef("LAMP-INT")])
        result = expander.expand(form)
        # <PUT ,LAMP-INT ,C-ENABLED? 0>
        assert result.operator.value == "PUT"
        assert result.args[2].value == 0

    def test_rfatal_macro(self, expander):
        """RFATAL expands to PROG with PUSH/RSTACK."""
        form = Form(Atom("RFATAL"), [])
        result = expander.expand(form)
        assert result.operator.value == "PROG"
```

**Verification:** `pytest tests/compiler/test_simple_macros.py -v`

---

### Task 3.8: VERB? PRSO? PRSI? Macros

**Test file:** `tests/compiler/test_parser_macros.py`

```python
"""Tests for parser-related macros."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestParserMacros:
    """Tests for VERB?, PRSO?, PRSI?, ROOM? macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_verb_single(self, expander):
        """VERB? with single verb."""
        # <VERB? TAKE>
        form = Form(Atom("VERB?"), [Atom("TAKE")])
        result = expander.expand(form)
        # <EQUAL? ,PRSA ,V?TAKE>
        assert result.operator.value == "EQUAL?"

    def test_verb_multiple(self, expander):
        """VERB? with multiple verbs creates OR."""
        # <VERB? TAKE DROP>
        form = Form(Atom("VERB?"), [Atom("TAKE"), Atom("DROP")])
        result = expander.expand(form)
        # <OR <EQUAL? ,PRSA ,V?TAKE> <EQUAL? ,PRSA ,V?DROP>>
        assert result.operator.value == "OR"

    def test_prso_check(self, expander):
        """PRSO? checks direct object."""
        # <PRSO? LAMP>
        form = Form(Atom("PRSO?"), [Atom("LAMP")])
        result = expander.expand(form)
        # <EQUAL? ,PRSO ,LAMP>
        assert result.operator.value == "EQUAL?"

    def test_room_check(self, expander):
        """ROOM? checks current room."""
        # <ROOM? LIVING-ROOM>
        form = Form(Atom("ROOM?"), [Atom("LIVING-ROOM")])
        result = expander.expand(form)
        # <EQUAL? ,HERE ,LIVING-ROOM>
        assert result.operator.value == "EQUAL?"
```

**Verification:** `pytest tests/compiler/test_parser_macros.py -v`

---

### Task 3.9: BSET BCLEAR BSET? Macros

**Test file:** `tests/compiler/test_flag_macros.py`

```python
"""Tests for flag manipulation macros."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, GlobalRef


class TestFlagMacros:
    """Tests for BSET, BCLEAR, BSET? macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_bset_single(self, expander):
        """BSET with single flag."""
        # <BSET ,LAMP ONBIT>
        form = Form(Atom("BSET"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        # <FSET ,LAMP ,ONBIT>
        assert result.operator.value == "FSET"

    def test_bset_multiple(self, expander):
        """BSET with multiple flags creates PROG."""
        # <BSET ,LAMP ONBIT LIGHTBIT>
        form = Form(Atom("BSET"), [
            GlobalRef("LAMP"), Atom("ONBIT"), Atom("LIGHTBIT")
        ])
        result = expander.expand(form)
        # <PROG () <FSET...> <FSET...>>
        assert result.operator.value == "PROG"

    def test_bclear_single(self, expander):
        """BCLEAR clears flags."""
        form = Form(Atom("BCLEAR"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        assert result.operator.value == "FCLEAR"

    def test_bset_question(self, expander):
        """BSET? checks flags with OR."""
        form = Form(Atom("BSET?"), [
            GlobalRef("LAMP"), Atom("ONBIT"), Atom("LIGHTBIT")
        ])
        result = expander.expand(form)
        # <OR <FSET? ...> <FSET? ...>>
        assert result.operator.value == "OR"
```

**Verification:** `pytest tests/compiler/test_flag_macros.py -v`

---

### Task 3.10: Conditional Macros (FLAMING?, OPENABLE?, ABS, PROB)

**Test file:** `tests/compiler/test_conditional_macros.py`

```python
"""Tests for conditional/utility macros."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, GlobalRef, Number


class TestConditionalMacros:
    """Tests for FLAMING?, OPENABLE?, ABS, PROB macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_flaming(self, expander):
        """FLAMING? checks FLAMEBIT and ONBIT."""
        form = Form(Atom("FLAMING?"), [GlobalRef("LAMP")])
        result = expander.expand(form)
        # <AND <FSET? ,LAMP ,FLAMEBIT> <FSET? ,LAMP ,ONBIT>>
        assert result.operator.value == "AND"

    def test_openable(self, expander):
        """OPENABLE? checks DOORBIT or CONTBIT."""
        form = Form(Atom("OPENABLE?"), [GlobalRef("BOX")])
        result = expander.expand(form)
        # <OR <FSET? ,BOX ,DOORBIT> <FSET? ,BOX ,CONTBIT>>
        assert result.operator.value == "OR"

    def test_abs_positive(self, expander):
        """ABS creates conditional for absolute value."""
        form = Form(Atom("ABS"), [GlobalRef("NUM")])
        result = expander.expand(form)
        # <COND (<L? ,NUM 0> <-> 0 ,NUM>) (T ,NUM)>
        assert result.operator.value == "COND"

    def test_prob(self, expander):
        """PROB creates probability check."""
        form = Form(Atom("PROB"), [Number(50)])
        result = expander.expand(form)
        # <G? 50 <RANDOM 100>>
        assert result.operator.value == "G?"
```

**Verification:** `pytest tests/compiler/test_conditional_macros.py -v`

---

### Task 3.11: Compile-Time Evaluation (%<...>)

**Test file:** `tests/compiler/test_percent_eval.py`

```python
"""Tests for compile-time evaluation."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import PercentEval, Form, Atom, Number


class TestPercentEval:
    """Tests for %<...> compile-time evaluation."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_simple_arithmetic(self, expander):
        """Simple arithmetic is evaluated at compile time."""
        # %<+ 1 2> -> 3
        inner = Form(Atom("+"), [Number(1), Number(2)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 3

    def test_nested_arithmetic(self, expander):
        """Nested arithmetic evaluated."""
        # %<* 2 <+ 3 4>> -> 14
        inner = Form(Atom("*"), [
            Number(2),
            Form(Atom("+"), [Number(3), Number(4)])
        ])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert result.value == 14

    def test_percent_in_form(self, expander):
        """Percent eval within larger form."""
        # <SETG X %<+ 1 1>> -> <SETG X 2>
        percent = PercentEval(Form(Atom("+"), [Number(1), Number(1)]))
        form = Form(Atom("SETG"), [Atom("X"), percent])
        result = expander.expand(form)
        assert result.args[1].value == 2
```

**Verification:** `pytest tests/compiler/test_percent_eval.py -v`

---

### Task 3.12: Full File Macro Expansion

**Test file:** `tests/compiler/test_file_expansion.py`

```python
"""Tests for expanding macros in complete files."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Routine


class TestFileExpansion:
    """Tests for macro expansion across files."""

    @pytest.fixture
    def zork_dir(self):
        current = Path(__file__).parent
        while current != current.parent:
            candidate = current / "zork1"
            if candidate.exists():
                return candidate
            current = current.parent
        pytest.skip("zork1 directory not found")

    def test_expand_routine_with_tell(self, zork_dir):
        """Routine containing TELL is expanded."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        # Load and expand a file with TELL usage
        ast = processor.load_file("gclock.zil")
        expanded = [expander.expand(node) for node in ast]

        # Find routines and verify TELL is expanded
        routines = [n for n in expanded if isinstance(n, Routine)]
        assert len(routines) > 0
        # TELL forms should now be PROG forms
        for routine in routines:
            for form in routine.body:
                if isinstance(form, Form):
                    assert form.operator.value != "TELL"

    def test_no_unexpanded_macros(self, zork_dir):
        """After expansion, no macro calls remain."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        ast = processor.load_file("gmain.zil")
        expanded = [expander.expand(node) for node in ast]

        macro_names = {"TELL", "VERB?", "PRSO?", "PRSI?", "ROOM?",
                       "BSET", "BCLEAR", "BSET?", "ENABLE", "DISABLE"}

        def check_no_macros(node):
            if isinstance(node, Form):
                if isinstance(node.operator, Atom):
                    assert node.operator.value.upper() not in macro_names
                for arg in node.args:
                    check_no_macros(arg)
            elif isinstance(node, list):
                for item in node:
                    check_no_macros(item)
            elif isinstance(node, Routine):
                for form in node.body:
                    check_no_macros(form)

        for node in expanded:
            check_no_macros(node)
```

**Verification:** `pytest tests/compiler/test_file_expansion.py -v`

---

### Task 3.13: Zork I Macro Expansion Integration

**Test file:** `tests/integration/test_zork_macros.py`

```python
"""Integration tests for Zork I macro expansion."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Routine, Form


class TestZorkMacroExpansion:
    """Integration tests for complete Zork I macro expansion."""

    @pytest.fixture
    def zork_dir(self):
        current = Path(__file__).parent
        while current != current.parent:
            candidate = current / "zork1"
            if candidate.exists():
                return candidate
            current = current.parent
        pytest.skip("zork1 directory not found")

    @pytest.fixture
    def expanded_ast(self, zork_dir):
        """Load and expand all Zork I files."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        ast = processor.load_all("zork1.zil")
        return [expander.expand(node) for node in ast]

    def test_all_files_expand(self, expanded_ast):
        """All Zork I files expand without error."""
        assert len(expanded_ast) > 100

    def test_tell_count(self, expanded_ast):
        """All TELL macros are expanded (1000+ originally)."""
        tell_count = 0
        prog_count = 0

        def count_forms(node):
            nonlocal tell_count, prog_count
            if isinstance(node, Form):
                if node.operator.value == "TELL":
                    tell_count += 1
                elif node.operator.value == "PROG":
                    prog_count += 1
                for arg in node.args:
                    count_forms(arg)
            elif isinstance(node, Routine):
                for form in node.body:
                    count_forms(form)
            elif isinstance(node, list):
                for item in node:
                    count_forms(item)

        for node in expanded_ast:
            count_forms(node)

        assert tell_count == 0, "All TELL macros should be expanded"
        assert prog_count > 500, "Many PROG forms from TELL expansion"

    def test_routine_bodies_expanded(self, expanded_ast):
        """Routine bodies have macros expanded."""
        routines = [n for n in expanded_ast if isinstance(n, Routine)]
        assert len(routines) > 50

        for routine in routines:
            for form in routine.body:
                if isinstance(form, Form):
                    # No unexpanded macros in routine bodies
                    assert form.operator.value not in ["TELL", "VERB?", "BSET"]
```

**Verification:** `pytest tests/integration/test_zork_macros.py -v`

---

## File Structure

```
zil_interpreter/
├── compiler/
│   ├── __init__.py           # UPDATE
│   ├── macro_registry.py     # NEW (Task 3.2)
│   ├── macro_expander.py     # NEW (Task 3.6)
│   ├── tell_macro.py         # NEW (Task 3.3-3.5)
│   └── builtin_macros.py     # NEW (Tasks 3.7-3.10)
├── parser/
│   ├── ast_nodes.py          # UPDATE (Task 3.1)
│   └── transformer.py        # UPDATE (Task 3.1)
└── ...

tests/
├── compiler/
│   ├── test_macro_definition.py   # NEW (Task 3.1)
│   ├── test_macro_registry.py     # NEW (Task 3.2)
│   ├── test_tell_macro.py         # NEW (Task 3.3)
│   ├── test_tell_indicators.py    # NEW (Task 3.4)
│   ├── test_tell_mixed.py         # NEW (Task 3.5)
│   ├── test_macro_expander.py     # NEW (Task 3.6)
│   ├── test_simple_macros.py      # NEW (Task 3.7)
│   ├── test_parser_macros.py      # NEW (Task 3.8)
│   ├── test_flag_macros.py        # NEW (Task 3.9)
│   ├── test_conditional_macros.py # NEW (Task 3.10)
│   ├── test_percent_eval.py       # NEW (Task 3.11)
│   └── test_file_expansion.py     # NEW (Task 3.12)
└── integration/
    └── test_zork_macros.py        # NEW (Task 3.13)
```

---

## Task Summary

| Task | Description | Test File | Impl File |
|------|-------------|-----------|-----------|
| 3.1 | MacroDef AST node | test_macro_definition.py | ast_nodes.py, transformer.py |
| 3.2 | Macro registry | test_macro_registry.py | macro_registry.py |
| 3.3 | TELL - basic strings | test_tell_macro.py | tell_macro.py |
| 3.4 | TELL - indicators | test_tell_indicators.py | tell_macro.py |
| 3.5 | TELL - mixed content | test_tell_mixed.py | tell_macro.py |
| 3.6 | Macro expander | test_macro_expander.py | macro_expander.py |
| 3.7 | ENABLE/DISABLE/RFATAL | test_simple_macros.py | builtin_macros.py |
| 3.8 | VERB?/PRSO?/PRSI?/ROOM? | test_parser_macros.py | builtin_macros.py |
| 3.9 | BSET/BCLEAR/BSET? | test_flag_macros.py | builtin_macros.py |
| 3.10 | FLAMING?/OPENABLE?/ABS/PROB | test_conditional_macros.py | builtin_macros.py |
| 3.11 | Percent eval (%<...>) | test_percent_eval.py | macro_expander.py |
| 3.12 | File expansion | test_file_expansion.py | integration |
| 3.13 | Zork integration | test_zork_macros.py | integration |

---

## Success Criteria

- [ ] All DEFMAC definitions create MacroDef AST nodes
- [ ] MacroRegistry stores and retrieves macros
- [ ] TELL macro expands all 1,086 uses correctly
- [ ] All 15 Zork I macros implemented
- [ ] No unexpanded macro calls after expansion
- [ ] All 13 tasks have passing tests
- [ ] Code committed with descriptive messages

---

## Dependencies

```
Chunk 2 (File Processing) ─────► Chunk 3 (Macro System)
                                          │
                                          ▼
                                   Chunk 4 (Directives)
```
