# Chunk 4: Compile-Time Directive System - TDD Implementation Plan

**Goal:** Process ZIL compile-time directives to build game tables
**Branch:** `feature/zork1-directives`
**Approach:** TDD (Red → Green → Refactor)

---

## Current State

- All 10 Zork I files parse successfully
- Macro system expands all 15 macros (0 unexpanded)
- **685 tests passing**
- **Missing:** Compile-time directive processing (SYNTAX, CONSTANT, GLOBAL, etc.)

## Directive Overview

From Zork I files:
- **269 SYNTAX** entries in gsyntax.zil (verb patterns)
- **101 CONSTANT** definitions across files
- **167 GLOBAL** variable declarations
- **4 PROPDEF** property defaults
- **1 DIRECTIONS** declaration (12 directions)
- Multiple **BUZZ/SYNONYM** vocabulary entries

---

## Implementation Tasks

### Task 4.1: Directive AST Dataclasses

**Test file:** `tests/compiler/test_directive_ast.py`

```python
"""Tests for directive AST dataclasses."""
import pytest
from zil_interpreter.compiler.directives import (
    ConstantDef, GlobalDef, PropDef, DirectionsDef,
    SynonymDef, BuzzDef, SyntaxDef, ObjectConstraint
)


class TestDirectiveDataclasses:
    """Tests for directive AST representation."""

    def test_constant_def(self):
        """CONSTANT creates ConstantDef."""
        const = ConstantDef(name="M-ENTER", value=2)
        assert const.name == "M-ENTER"
        assert const.value == 2

    def test_global_def(self):
        """GLOBAL creates GlobalDef."""
        glob = GlobalDef(name="LUCKY", initial_value=True)
        assert glob.name == "LUCKY"
        assert glob.initial_value is True

    def test_propdef(self):
        """PROPDEF creates PropDef."""
        prop = PropDef(name="SIZE", default=5)
        assert prop.name == "SIZE"
        assert prop.default == 5

    def test_directions_def(self):
        """DIRECTIONS creates DirectionsDef."""
        dirs = DirectionsDef(directions=["NORTH", "SOUTH", "EAST", "WEST"])
        assert "NORTH" in dirs.directions
        assert len(dirs.directions) == 4

    def test_synonym_def(self):
        """SYNONYM creates SynonymDef."""
        syn = SynonymDef(primary="WITH", aliases=["USING", "THROUGH"])
        assert syn.primary == "WITH"
        assert "USING" in syn.aliases

    def test_buzz_def(self):
        """BUZZ creates BuzzDef."""
        buzz = BuzzDef(words=["A", "AN", "THE"])
        assert "THE" in buzz.words

    def test_syntax_def_simple(self):
        """Simple SYNTAX creates SyntaxDef."""
        syntax = SyntaxDef(
            verb="QUIT",
            action="V-QUIT",
            objects=[],
            prepositions=[],
            preaction=None
        )
        assert syntax.verb == "QUIT"
        assert syntax.action == "V-QUIT"

    def test_syntax_def_with_object(self):
        """SYNTAX with OBJECT creates SyntaxDef."""
        syntax = SyntaxDef(
            verb="TAKE",
            action="V-TAKE",
            objects=[ObjectConstraint(position=1, constraints=["TAKEABLE"])],
            prepositions=[],
            preaction="PRE-TAKE"
        )
        assert len(syntax.objects) == 1
        assert syntax.preaction == "PRE-TAKE"
```

**Implementation:** `zil_interpreter/compiler/directives.py`

```python
"""Compile-time directive dataclasses."""
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ConstantDef:
    """CONSTANT definition."""
    name: str
    value: Any


@dataclass
class GlobalDef:
    """GLOBAL variable definition."""
    name: str
    initial_value: Any


@dataclass
class PropDef:
    """PROPDEF property default definition."""
    name: str
    default: Any


@dataclass
class DirectionsDef:
    """DIRECTIONS declaration."""
    directions: List[str]


@dataclass
class SynonymDef:
    """SYNONYM declaration."""
    primary: str
    aliases: List[str]


@dataclass
class BuzzDef:
    """BUZZ (noise words) declaration."""
    words: List[str]


@dataclass
class ObjectConstraint:
    """Object constraint in SYNTAX."""
    position: int  # 1 = PRSO, 2 = PRSI
    constraints: List[str] = field(default_factory=list)
    # Constraints: FIND flagbit, HELD, CARRIED, MANY, HAVE, IN-ROOM, ON-GROUND


@dataclass
class SyntaxDef:
    """SYNTAX verb pattern definition."""
    verb: str
    action: str
    objects: List[ObjectConstraint] = field(default_factory=list)
    prepositions: List[str] = field(default_factory=list)
    preaction: Optional[str] = None
```

**Verification:** `pytest tests/compiler/test_directive_ast.py -v`

---

### Task 4.2: CONSTANT Processor

**Test file:** `tests/compiler/test_constant_processor.py`

```python
"""Tests for CONSTANT directive processing."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.compiler.directives import ConstantDef
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String


class TestConstantProcessor:
    """Tests for CONSTANT directive processing."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_constant_number(self, processor):
        """Process CONSTANT with number value."""
        # <CONSTANT M-ENTER 2>
        form = Form(Atom("CONSTANT"), [Atom("M-ENTER"), Number(2)])
        processor.process(form)
        assert processor.constants["M-ENTER"] == 2

    def test_constant_string(self, processor):
        """Process CONSTANT with string value."""
        # <CONSTANT REESSION "0">
        form = Form(Atom("CONSTANT"), [Atom("REESSION"), String("0")])
        processor.process(form)
        assert processor.constants["REESSION"] == "0"

    def test_constant_atom(self, processor):
        """Process CONSTANT with atom value."""
        # <CONSTANT ZORK-NUMBER 1>
        form = Form(Atom("CONSTANT"), [Atom("ZORK-NUMBER"), Number(1)])
        processor.process(form)
        assert processor.constants["ZORK-NUMBER"] == 1

    def test_constant_case_insensitive(self, processor):
        """CONSTANT lookup is case-insensitive."""
        form = Form(Atom("CONSTANT"), [Atom("FOO"), Number(42)])
        processor.process(form)
        assert processor.get_constant("foo") == 42
        assert processor.get_constant("FOO") == 42

    def test_multiple_constants(self, processor):
        """Process multiple CONSTANT definitions."""
        processor.process(Form(Atom("CONSTANT"), [Atom("A"), Number(1)]))
        processor.process(Form(Atom("CONSTANT"), [Atom("B"), Number(2)]))
        processor.process(Form(Atom("CONSTANT"), [Atom("C"), Number(3)]))
        assert len(processor.constants) == 3
```

**Verification:** `pytest tests/compiler/test_constant_processor.py -v`

---

### Task 4.3: GLOBAL Processor

**Test file:** `tests/compiler/test_global_processor.py`

```python
"""Tests for GLOBAL directive processing."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String, GlobalRef


class TestGlobalProcessor:
    """Tests for GLOBAL directive processing."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_global_with_number(self, processor):
        """Process GLOBAL with number value."""
        # <GLOBAL MATCH-COUNT 6>
        form = Form(Atom("GLOBAL"), [Atom("MATCH-COUNT"), Number(6)])
        processor.process(form)
        assert processor.globals["MATCH-COUNT"] == 6

    def test_global_with_false(self, processor):
        """Process GLOBAL with false (<>)."""
        # <GLOBAL RUG-MOVED <>>
        form = Form(Atom("GLOBAL"), [Atom("RUG-MOVED"), Form(Atom("<>"), [])])
        processor.process(form)
        assert processor.globals["RUG-MOVED"] is False

    def test_global_with_true(self, processor):
        """Process GLOBAL with T (true)."""
        # <GLOBAL LUCKY T>
        form = Form(Atom("GLOBAL"), [Atom("LUCKY"), Atom("T")])
        processor.process(form)
        assert processor.globals["LUCKY"] is True

    def test_global_with_table(self, processor):
        """Process GLOBAL with LTABLE value."""
        # <GLOBAL LOUD-RUNS <LTABLE 0 ROOM1 ROOM2>>
        ltable = Form(Atom("LTABLE"), [Number(0), Atom("ROOM1"), Atom("ROOM2")])
        form = Form(Atom("GLOBAL"), [Atom("LOUD-RUNS"), ltable])
        processor.process(form)
        # Store as unevaluated form for now
        assert "LOUD-RUNS" in processor.globals

    def test_global_count(self, processor):
        """Process multiple GLOBAL definitions."""
        processor.process(Form(Atom("GLOBAL"), [Atom("A"), Number(1)]))
        processor.process(Form(Atom("GLOBAL"), [Atom("B"), Number(2)]))
        assert len(processor.globals) == 2
```

**Verification:** `pytest tests/compiler/test_global_processor.py -v`

---

### Task 4.4: PROPDEF Processor

**Test file:** `tests/compiler/test_propdef_processor.py`

```python
"""Tests for PROPDEF directive processing."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom, Number


class TestPropdefProcessor:
    """Tests for PROPDEF directive processing."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_propdef_size(self, processor):
        """Process PROPDEF SIZE 5."""
        form = Form(Atom("PROPDEF"), [Atom("SIZE"), Number(5)])
        processor.process(form)
        assert processor.property_defaults["SIZE"] == 5

    def test_propdef_capacity(self, processor):
        """Process PROPDEF CAPACITY 0."""
        form = Form(Atom("PROPDEF"), [Atom("CAPACITY"), Number(0)])
        processor.process(form)
        assert processor.property_defaults["CAPACITY"] == 0

    def test_multiple_propdefs(self, processor):
        """Process all Zork I PROPDEFs."""
        processor.process(Form(Atom("PROPDEF"), [Atom("SIZE"), Number(5)]))
        processor.process(Form(Atom("PROPDEF"), [Atom("CAPACITY"), Number(0)]))
        processor.process(Form(Atom("PROPDEF"), [Atom("VALUE"), Number(0)]))
        processor.process(Form(Atom("PROPDEF"), [Atom("TVALUE"), Number(0)]))
        assert len(processor.property_defaults) == 4

    def test_propdef_lookup(self, processor):
        """Get default property value."""
        processor.process(Form(Atom("PROPDEF"), [Atom("SIZE"), Number(5)]))
        assert processor.get_property_default("SIZE") == 5
        assert processor.get_property_default("UNKNOWN") is None
```

**Verification:** `pytest tests/compiler/test_propdef_processor.py -v`

---

### Task 4.5: DIRECTIONS Processor

**Test file:** `tests/compiler/test_directions_processor.py`

```python
"""Tests for DIRECTIONS directive processing."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestDirectionsProcessor:
    """Tests for DIRECTIONS directive processing."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_directions_basic(self, processor):
        """Process DIRECTIONS with all 12 Zork directions."""
        # <DIRECTIONS NORTH EAST WEST SOUTH NE NW SE SW UP DOWN IN OUT LAND>
        form = Form(Atom("DIRECTIONS"), [
            Atom("NORTH"), Atom("EAST"), Atom("WEST"), Atom("SOUTH"),
            Atom("NE"), Atom("NW"), Atom("SE"), Atom("SW"),
            Atom("UP"), Atom("DOWN"), Atom("IN"), Atom("OUT"), Atom("LAND")
        ])
        processor.process(form)
        assert len(processor.directions) == 13
        assert "NORTH" in processor.directions
        assert "LAND" in processor.directions

    def test_is_direction(self, processor):
        """Check if word is a direction."""
        form = Form(Atom("DIRECTIONS"), [Atom("NORTH"), Atom("SOUTH")])
        processor.process(form)
        assert processor.is_direction("NORTH")
        assert processor.is_direction("north")  # case-insensitive
        assert not processor.is_direction("TAKE")

    def test_direction_index(self, processor):
        """Get index of direction (for property lookup)."""
        form = Form(Atom("DIRECTIONS"), [
            Atom("NORTH"), Atom("EAST"), Atom("WEST"), Atom("SOUTH")
        ])
        processor.process(form)
        assert processor.direction_index("NORTH") == 0
        assert processor.direction_index("SOUTH") == 3
```

**Verification:** `pytest tests/compiler/test_directions_processor.py -v`

---

### Task 4.6: BUZZ/SYNONYM Vocabulary Processor

**Test file:** `tests/compiler/test_vocabulary_processor.py`

```python
"""Tests for BUZZ and SYNONYM vocabulary processing."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestBuzzProcessor:
    """Tests for BUZZ (noise word) processing."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_buzz_words(self, processor):
        """Process BUZZ directive."""
        # <BUZZ A AN THE IS AND OF THEN>
        form = Form(Atom("BUZZ"), [
            Atom("A"), Atom("AN"), Atom("THE"), Atom("IS"),
            Atom("AND"), Atom("OF"), Atom("THEN")
        ])
        processor.process(form)
        assert processor.is_buzz_word("THE")
        assert processor.is_buzz_word("the")  # case-insensitive
        assert not processor.is_buzz_word("TAKE")

    def test_multiple_buzz(self, processor):
        """Process multiple BUZZ directives."""
        processor.process(Form(Atom("BUZZ"), [Atom("AGAIN"), Atom("G")]))
        processor.process(Form(Atom("BUZZ"), [Atom("A"), Atom("AN"), Atom("THE")]))
        assert len(processor.buzz_words) == 5


class TestSynonymProcessor:
    """Tests for SYNONYM processing."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_synonym_basic(self, processor):
        """Process SYNONYM directive."""
        # <SYNONYM WITH USING THROUGH THRU>
        form = Form(Atom("SYNONYM"), [
            Atom("WITH"), Atom("USING"), Atom("THROUGH"), Atom("THRU")
        ])
        processor.process(form)
        assert processor.get_canonical("USING") == "WITH"
        assert processor.get_canonical("THRU") == "WITH"
        assert processor.get_canonical("WITH") == "WITH"  # primary maps to itself

    def test_synonym_directions(self, processor):
        """Process direction synonyms."""
        # <SYNONYM NORTH N>
        processor.process(Form(Atom("SYNONYM"), [Atom("NORTH"), Atom("N")]))
        assert processor.get_canonical("N") == "NORTH"

    def test_multiple_synonyms(self, processor):
        """Process multiple SYNONYM directives."""
        processor.process(Form(Atom("SYNONYM"), [Atom("IN"), Atom("INSIDE"), Atom("INTO")]))
        processor.process(Form(Atom("SYNONYM"), [Atom("ON"), Atom("ONTO")]))
        assert processor.get_canonical("INSIDE") == "IN"
        assert processor.get_canonical("ONTO") == "ON"

    def test_unknown_canonical(self, processor):
        """Unknown word returns itself."""
        assert processor.get_canonical("TAKE") == "TAKE"
```

**Verification:** `pytest tests/compiler/test_vocabulary_processor.py -v`

---

### Task 4.7: SYNTAX Table Builder

**Test file:** `tests/compiler/test_syntax_table.py`

```python
"""Tests for SYNTAX table building."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.compiler.syntax_table import SyntaxTable
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestSyntaxTableBuilder:
    """Tests for SYNTAX directive processing and table building."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_syntax_simple(self, processor):
        """Process simple SYNTAX without objects."""
        # <SYNTAX QUIT = V-QUIT>
        form = Form(Atom("SYNTAX"), [
            Atom("QUIT"), Atom("="), Atom("V-QUIT")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("QUIT")
        assert len(entries) == 1
        assert entries[0].action == "V-QUIT"

    def test_syntax_with_object(self, processor):
        """Process SYNTAX with single OBJECT."""
        # <SYNTAX TAKE OBJECT = V-TAKE>
        form = Form(Atom("SYNTAX"), [
            Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("TAKE")
        assert len(entries) == 1
        assert len(entries[0].objects) == 1

    def test_syntax_with_constraints(self, processor):
        """Process SYNTAX with object constraints."""
        # <SYNTAX TAKE OBJECT (TAKEABLE HELD) = V-TAKE PRE-TAKE>
        form = Form(Atom("SYNTAX"), [
            Atom("TAKE"), Atom("OBJECT"),
            [Atom("TAKEABLE"), Atom("HELD")],  # constraints as list
            Atom("="), Atom("V-TAKE"), Atom("PRE-TAKE")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("TAKE")
        assert entries[0].preaction == "PRE-TAKE"
        assert "TAKEABLE" in entries[0].objects[0].constraints

    def test_syntax_with_preposition(self, processor):
        """Process SYNTAX with preposition and two objects."""
        # <SYNTAX PUT OBJECT IN OBJECT = V-PUT PRE-PUT>
        form = Form(Atom("SYNTAX"), [
            Atom("PUT"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
            Atom("="), Atom("V-PUT"), Atom("PRE-PUT")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("PUT")
        assert len(entries[0].objects) == 2
        assert "IN" in entries[0].prepositions

    def test_syntax_multiple_patterns(self, processor):
        """Same verb can have multiple SYNTAX patterns."""
        # Multiple DROP patterns
        processor.process(Form(Atom("SYNTAX"), [
            Atom("DROP"), Atom("OBJECT"), Atom("="), Atom("V-DROP")
        ]))
        processor.process(Form(Atom("SYNTAX"), [
            Atom("DROP"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
            Atom("="), Atom("V-PUT"), Atom("PRE-PUT")
        ]))
        entries = processor.syntax_table.lookup("DROP")
        assert len(entries) == 2


class TestSyntaxTableLookup:
    """Tests for SYNTAX table matching."""

    def test_match_simple(self):
        """Match simple verb-only command."""
        table = SyntaxTable()
        table.add_entry("QUIT", [], [], "V-QUIT", None)
        match = table.match("QUIT", 0, None)
        assert match is not None
        assert match.action == "V-QUIT"

    def test_match_with_object(self):
        """Match command with one object."""
        table = SyntaxTable()
        table.add_entry("TAKE", [1], [], "V-TAKE", None)
        match = table.match("TAKE", 1, None)
        assert match is not None
        assert match.action == "V-TAKE"

    def test_match_with_two_objects(self):
        """Match command with two objects."""
        table = SyntaxTable()
        table.add_entry("PUT", [1, 2], ["IN"], "V-PUT", "PRE-PUT")
        match = table.match("PUT", 2, "IN")
        assert match is not None
        assert match.preaction == "PRE-PUT"

    def test_no_match(self):
        """Return None when no pattern matches."""
        table = SyntaxTable()
        table.add_entry("QUIT", [], [], "V-QUIT", None)
        assert table.match("INVALID", 0, None) is None
```

**Verification:** `pytest tests/compiler/test_syntax_table.py -v`

---

### Task 4.8: DirectiveProcessor Integration

**Test file:** `tests/compiler/test_directive_integration.py`

```python
"""Tests for complete directive processing pipeline."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestDirectiveProcessorIntegration:
    """Tests for directive processing from real Zork files."""

    @pytest.fixture
    def zork_dir(self):
        zork_path = Path("/Users/Keith.MacKay/Projects/zork1/zork1")
        if zork_path.exists():
            return zork_path
        pytest.skip("zork1 directory not found")

    @pytest.fixture
    def processed_directives(self, zork_dir):
        """Load and process all directives from Zork I."""
        file_processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)
        directive_processor = DirectiveProcessor()

        ast = file_processor.load_all("zork1.zil")
        expanded = [expander.expand(node) for node in ast]

        for node in expanded:
            if isinstance(node, Form) and isinstance(node.operator, Atom):
                directive_processor.process(node)

        return directive_processor

    def test_syntax_count(self, processed_directives):
        """All 269 SYNTAX entries are processed."""
        assert processed_directives.syntax_table.entry_count >= 269

    def test_constants_count(self, processed_directives):
        """CONSTANT definitions are processed."""
        assert len(processed_directives.constants) >= 100

    def test_globals_count(self, processed_directives):
        """GLOBAL definitions are processed."""
        assert len(processed_directives.globals) >= 150

    def test_propdef_count(self, processed_directives):
        """All 4 PROPDEF entries are processed."""
        assert len(processed_directives.property_defaults) == 4

    def test_directions_defined(self, processed_directives):
        """DIRECTIONS are defined."""
        assert len(processed_directives.directions) >= 12
        assert processed_directives.is_direction("NORTH")

    def test_buzz_words_defined(self, processed_directives):
        """BUZZ words are defined."""
        assert processed_directives.is_buzz_word("THE")
        assert processed_directives.is_buzz_word("A")

    def test_synonyms_defined(self, processed_directives):
        """SYNONYM mappings are defined."""
        assert processed_directives.get_canonical("N") == "NORTH"
        assert processed_directives.get_canonical("USING") == "WITH"
```

**Verification:** `pytest tests/compiler/test_directive_integration.py -v`

---

### Task 4.9: Zork I Integration Tests

**Test file:** `tests/integration/test_zork_directives.py`

```python
"""Integration tests for Zork I directive processing."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.compiler.directive_processor import DirectiveProcessor


class TestZorkDirectives:
    """Integration tests for complete Zork I directive processing."""

    @pytest.fixture
    def zork_dir(self):
        zork_path = Path("/Users/Keith.MacKay/Projects/zork1/zork1")
        if zork_path.exists():
            return zork_path
        pytest.skip("zork1 directory not found")

    @pytest.fixture
    def game_state(self, zork_dir):
        """Build complete game state from Zork I files."""
        file_processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)
        directive_processor = DirectiveProcessor()

        ast = file_processor.load_all("zork1.zil")
        expanded = [expander.expand(node) for node in ast]

        for node in expanded:
            directive_processor.process(node)

        return directive_processor

    def test_syntax_verbs_defined(self, game_state):
        """Common verbs have SYNTAX entries."""
        for verb in ["TAKE", "DROP", "OPEN", "CLOSE", "LOOK", "EXAMINE"]:
            entries = game_state.syntax_table.lookup(verb)
            assert len(entries) > 0, f"Missing SYNTAX for {verb}"

    def test_syntax_prepositions(self, game_state):
        """PUT has IN/ON preposition patterns."""
        entries = game_state.syntax_table.lookup("PUT")
        preps = set()
        for entry in entries:
            preps.update(entry.prepositions)
        assert "IN" in preps or "ON" in preps

    def test_direction_synonyms(self, game_state):
        """Direction abbreviations are synonyms."""
        assert game_state.get_canonical("N") == "NORTH"
        assert game_state.get_canonical("S") == "SOUTH"
        assert game_state.get_canonical("E") == "EAST"
        assert game_state.get_canonical("W") == "WEST"
        assert game_state.get_canonical("U") == "UP"
        assert game_state.get_canonical("D") == "DOWN"

    def test_known_constants(self, game_state):
        """Known Zork I constants are defined."""
        # M-ENTER and similar parser constants
        assert "M-ENTER" in game_state.constants or \
               game_state.get_constant("M-ENTER") is not None

    def test_known_globals(self, game_state):
        """Known Zork I globals are defined."""
        assert "LUCKY" in game_state.globals
        assert "MATCH-COUNT" in game_state.globals

    def test_property_defaults(self, game_state):
        """All 4 property defaults are defined."""
        assert game_state.get_property_default("SIZE") == 5
        assert game_state.get_property_default("CAPACITY") == 0
        assert game_state.get_property_default("VALUE") == 0
        assert game_state.get_property_default("TVALUE") == 0
```

**Verification:** `pytest tests/integration/test_zork_directives.py -v`

---

## File Structure

```
zil_interpreter/
├── compiler/
│   ├── __init__.py           # UPDATE
│   ├── directives.py         # NEW (Task 4.1) - Dataclasses
│   ├── directive_processor.py # NEW (Tasks 4.2-4.8)
│   ├── syntax_table.py       # NEW (Task 4.7)
│   └── ... (existing files)
└── ...

tests/
├── compiler/
│   ├── test_directive_ast.py       # NEW (Task 4.1)
│   ├── test_constant_processor.py  # NEW (Task 4.2)
│   ├── test_global_processor.py    # NEW (Task 4.3)
│   ├── test_propdef_processor.py   # NEW (Task 4.4)
│   ├── test_directions_processor.py # NEW (Task 4.5)
│   ├── test_vocabulary_processor.py # NEW (Task 4.6)
│   ├── test_syntax_table.py        # NEW (Task 4.7)
│   └── test_directive_integration.py # NEW (Task 4.8)
└── integration/
    └── test_zork_directives.py     # NEW (Task 4.9)
```

---

## Success Criteria

| Task | Criteria |
|------|----------|
| 4.1 | All directive dataclasses work |
| 4.2 | 101+ CONSTANT definitions processed |
| 4.3 | 167+ GLOBAL definitions processed |
| 4.4 | 4 PROPDEF defaults stored |
| 4.5 | 12+ DIRECTIONS indexed |
| 4.6 | BUZZ words and SYNONYM mappings work |
| 4.7 | 269 SYNTAX entries in table |
| 4.8 | All directives from Zork I processed |
| 4.9 | Integration tests pass |

---

## Verification Commands

```bash
# Run all chunk 4 tests
pytest tests/compiler/test_directive*.py tests/compiler/test_*_processor.py tests/compiler/test_syntax*.py tests/compiler/test_vocabulary*.py tests/integration/test_zork_directives.py -v

# Run full test suite
pytest tests/ -v
```
