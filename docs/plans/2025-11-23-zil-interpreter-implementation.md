# ZIL Interpreter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI interpreter to run Zork I from .zil source files with save/restore functionality.

**Architecture:** Domain-driven design with 4 core components: ZIL Parser (lark-based), Game World Model (objects/rooms/state), Command Engine (player input processing), Story Engine (ZIL routine execution). TDD approach building from parser up through full REPL.

**Tech Stack:** Python 3.11+, lark (parsing), pydantic (validation), rich/textual (CLI), pytest (testing)

**Design Reference:** See `docs/plans/2025-11-23-zil-interpreter-design.md` for full architecture details.

---

## Phase 1: Project Setup

### Task 1: Initialize Python Project

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `zil_interpreter/__init__.py`

**Step 1: Create pyproject.toml with dependencies**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "zil-interpreter"
version = "0.1.0"
description = "Python interpreter for ZIL (Zork Implementation Language)"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "lark>=1.1.8",
    "pydantic>=2.5.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "pytest-cov>=4.1.0",
    "black>=23.12.0",
    "mypy>=1.7.1",
]

[project.scripts]
zil = "zil_interpreter.cli.repl:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Step 2: Create basic README**

```markdown
# ZIL Interpreter

A Python interpreter for ZIL (Zork Implementation Language) that can play Zork I from source files.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
zil path/to/zork1.zil
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=zil_interpreter --cov-report=html

# Format code
black zil_interpreter tests
```

## Architecture

See `docs/plans/2025-11-23-zil-interpreter-design.md` for detailed architecture.
```

**Step 3: Create package structure**

```bash
mkdir -p zil_interpreter/{parser,world,engine,runtime,cli}
touch zil_interpreter/__init__.py
touch zil_interpreter/parser/__init__.py
touch zil_interpreter/world/__init__.py
touch zil_interpreter/engine/__init__.py
touch zil_interpreter/runtime/__init__.py
touch zil_interpreter/cli/__init__.py
mkdir -p tests/{parser,world,engine,runtime,cli}
touch tests/__init__.py
```

**Step 4: Install dependencies**

Run: `pip install -e ".[dev]"`
Expected: Successfully installed dependencies

**Step 5: Verify installation with basic test**

Create: `tests/test_import.py`

```python
def test_can_import_package():
    import zil_interpreter
    assert zil_interpreter is not None
```

Run: `pytest tests/test_import.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add .
git commit -m "feat: initialize Python project structure

- Add pyproject.toml with dependencies
- Create package structure (parser, world, engine, runtime, cli)
- Add basic README with installation instructions
- Verify package imports successfully

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 2: Parser Foundation

### Task 2: ZIL Lexer and Basic Grammar

**Files:**
- Create: `zil_interpreter/parser/grammar.py`
- Create: `tests/parser/test_lexer.py`

**Step 1: Write failing test for basic ZIL tokens**

Create: `tests/parser/test_lexer.py`

```python
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


def test_lexer_recognizes_angle_brackets():
    """Test that lexer can tokenize angle brackets."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    # Should not raise
    parser.parse('<>')


def test_lexer_recognizes_routine_keyword():
    """Test that lexer recognizes ROUTINE keyword."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    result = parser.parse('<ROUTINE FOO ()>')
    assert result is not None


def test_lexer_recognizes_strings():
    """Test that lexer can tokenize quoted strings."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    result = parser.parse('"hello world"')
    assert result is not None


def test_lexer_recognizes_atoms():
    """Test that lexer recognizes atoms (identifiers)."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    result = parser.parse('FOO-BAR')
    assert result is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_lexer.py -v`
Expected: FAIL with "No module named 'zil_interpreter.parser.grammar'"

**Step 3: Write minimal grammar implementation**

Create: `zil_interpreter/parser/grammar.py`

```python
"""ZIL language grammar definition using Lark parser."""

ZIL_GRAMMAR = r"""
    ?start: expression+

    expression: form
              | atom
              | string
              | number

    form: "<" atom expression* ">"

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_lexer.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/parser/grammar.py tests/parser/test_lexer.py
git commit -m "feat(parser): add basic ZIL lexer and grammar

- Define Lark grammar for ZIL syntax
- Support forms (<ATOM ...>), atoms, strings, numbers
- Add comment support (semicolon syntax)
- Test basic tokenization

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Task 3: AST Node Definitions

**Files:**
- Create: `zil_interpreter/parser/ast_nodes.py`
- Create: `tests/parser/test_ast_nodes.py`

**Step 1: Write failing test for AST node creation**

Create: `tests/parser/test_ast_nodes.py`

```python
import pytest
from zil_interpreter.parser.ast_nodes import (
    Form, Atom, String, Number, Routine, Object, Global
)


def test_form_creation():
    """Test basic Form node creation."""
    form = Form(operator=Atom("ROUTINE"), args=[Atom("FOO"), []])
    assert form.operator.value == "ROUTINE"
    assert len(form.args) == 2


def test_atom_creation():
    """Test Atom node preserves value."""
    atom = Atom("FOO-BAR")
    assert atom.value == "FOO-BAR"


def test_string_creation():
    """Test String node creation."""
    string = String("Hello world")
    assert string.value == "Hello world"


def test_number_creation():
    """Test Number node creation."""
    num = Number(42)
    assert num.value == 42


def test_routine_node():
    """Test Routine AST node."""
    routine = Routine(
        name="FOO",
        args=["X", "Y"],
        body=[Form(operator=Atom("TELL"), args=[String("test")])]
    )
    assert routine.name == "FOO"
    assert len(routine.args) == 2
    assert len(routine.body) == 1


def test_object_node():
    """Test Object AST node."""
    obj = Object(
        name="LAMP",
        properties={
            "DESC": String("brass lamp"),
            "SYNONYM": [Atom("LAMP"), Atom("LANTERN")]
        }
    )
    assert obj.name == "LAMP"
    assert obj.properties["DESC"].value == "brass lamp"


def test_global_node():
    """Test Global variable node."""
    global_var = Global(name="SCORE", value=Number(0))
    assert global_var.name == "SCORE"
    assert global_var.value.value == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_ast_nodes.py -v`
Expected: FAIL with "No module named 'zil_interpreter.parser.ast_nodes'"

**Step 3: Write minimal AST node implementation**

Create: `zil_interpreter/parser/ast_nodes.py`

```python
"""AST node definitions for ZIL parse tree."""

from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    pass


@dataclass
class Atom(ASTNode):
    """Represents a ZIL atom (identifier)."""
    value: str


@dataclass
class String(ASTNode):
    """Represents a string literal."""
    value: str


@dataclass
class Number(ASTNode):
    """Represents a numeric literal."""
    value: int | float


@dataclass
class Form(ASTNode):
    """Represents a ZIL form: <operator args...>"""
    operator: Atom
    args: List[Any] = field(default_factory=list)


@dataclass
class Routine(ASTNode):
    """Represents a ROUTINE definition."""
    name: str
    args: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class Object(ASTNode):
    """Represents an OBJECT definition."""
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Global(ASTNode):
    """Represents a GLOBAL variable definition."""
    name: str
    value: Any = None


@dataclass
class InsertFile(ASTNode):
    """Represents an INSERT-FILE directive."""
    filename: str
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_ast_nodes.py -v`
Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/parser/ast_nodes.py tests/parser/test_ast_nodes.py
git commit -m "feat(parser): add AST node definitions

- Define dataclasses for ZIL AST nodes
- Support basic types: Atom, String, Number, Form
- Support declarations: Routine, Object, Global
- Add InsertFile for file inclusion

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Task 4: Parse Tree to AST Transformer

**Files:**
- Create: `zil_interpreter/parser/transformer.py`
- Create: `tests/parser/test_transformer.py`

**Step 1: Write failing test for parse tree transformation**

Create: `tests/parser/test_transformer.py`

```python
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR
from zil_interpreter.parser.transformer import ZILTransformer
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number


def test_transform_simple_atom():
    """Test transforming a simple atom."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('FOO')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result[0], Atom)
    assert result[0].value == "FOO"


def test_transform_string():
    """Test transforming a string literal."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('"hello"')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result[0], String)
    assert result[0].value == "hello"


def test_transform_number():
    """Test transforming a number."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('42')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result[0], Number)
    assert result[0].value == 42


def test_transform_simple_form():
    """Test transforming a simple form."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('<TELL "hello">')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result[0], Form)
    assert result[0].operator.value == "TELL"
    assert len(result[0].args) == 1
    assert isinstance(result[0].args[0], String)


def test_transform_nested_form():
    """Test transforming nested forms."""
    parser = Lark(ZIL_GRAMMAR, start='expression', parser='lalr')
    tree = parser.parse('<COND (<EQUAL? X 1> <TELL "one">)>')
    transformer = ZILTransformer()
    result = transformer.transform(tree)
    assert isinstance(result[0], Form)
    assert result[0].operator.value == "COND"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/parser/test_transformer.py -v`
Expected: FAIL with "No module named 'zil_interpreter.parser.transformer'"

**Step 3: Write minimal transformer implementation**

Create: `zil_interpreter/parser/transformer.py`

```python
"""Transformer to convert Lark parse tree to AST."""

from lark import Transformer, Token
from zil_interpreter.parser.ast_nodes import (
    Form, Atom, String, Number, ASTNode
)


class ZILTransformer(Transformer):
    """Transforms Lark parse tree into ZIL AST."""

    def atom(self, items):
        """Transform atom token."""
        return Atom(str(items[0]).upper())

    def string(self, items):
        """Transform string literal."""
        # Remove quotes
        value = str(items[0])[1:-1]
        # Handle escape sequences
        value = value.replace('\\n', '\n').replace('\\t', '\t')
        return String(value)

    def number(self, items):
        """Transform number literal."""
        value = str(items[0])
        if '.' in value:
            return Number(float(value))
        return Number(int(value))

    def form(self, items):
        """Transform form <operator args...>"""
        operator = items[0]
        args = items[1:] if len(items) > 1 else []
        return Form(operator=operator, args=args)

    def expression(self, items):
        """Pass through expression."""
        return items[0] if items else None

    def start(self, items):
        """Return list of top-level expressions."""
        return [item for item in items if item is not None]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/parser/test_transformer.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/parser/transformer.py tests/parser/test_transformer.py
git commit -m "feat(parser): add parse tree to AST transformer

- Implement Lark Transformer for ZIL syntax
- Transform atoms, strings, numbers, forms
- Handle nested forms and escape sequences
- Convert all atoms to uppercase (ZIL convention)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Task 5: ZIL File Loader

**Files:**
- Create: `zil_interpreter/parser/loader.py`
- Create: `tests/parser/test_loader.py`
- Create: `tests/fixtures/simple.zil`

**Step 1: Create test fixture file**

Create: `tests/fixtures/simple.zil`

```zil
"Simple test ZIL file"

<GLOBAL TEST-VAR 42>

<ROUTINE TEST-ROUTINE ()
    <TELL "Hello from ZIL!">>
```

**Step 2: Write failing test for file loading**

Create: `tests/parser/test_loader.py`

```python
import pytest
from pathlib import Path
from zil_interpreter.parser.loader import ZILLoader
from zil_interpreter.parser.ast_nodes import Global, Routine, String


def test_load_simple_file():
    """Test loading a simple ZIL file."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "simple.zil"
    loader = ZILLoader()
    ast = loader.load_file(fixture_path)

    assert len(ast) >= 2  # At least GLOBAL and ROUTINE

    # Find the global definition
    globals_found = [node for node in ast if isinstance(node, Global)]
    assert len(globals_found) == 1
    assert globals_found[0].name == "TEST-VAR"

    # Find the routine definition
    routines_found = [node for node in ast if isinstance(node, Routine)]
    assert len(routines_found) == 1
    assert routines_found[0].name == "TEST-ROUTINE"


def test_loader_handles_comments():
    """Test that loader ignores comments."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "simple.zil"
    loader = ZILLoader()
    ast = loader.load_file(fixture_path)

    # Comments should not appear in AST
    comment_nodes = [node for node in ast if isinstance(node, str) and node.startswith(';')]
    assert len(comment_nodes) == 0


def test_loader_nonexistent_file():
    """Test that loader raises error for nonexistent file."""
    loader = ZILLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_file(Path("nonexistent.zil"))
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/parser/test_loader.py -v`
Expected: FAIL with "No module named 'zil_interpreter.parser.loader'"

**Step 4: Write minimal loader implementation**

Create: `zil_interpreter/parser/loader.py`

```python
"""ZIL file loader and parser."""

from pathlib import Path
from typing import List
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR
from zil_interpreter.parser.transformer import ZILTransformer
from zil_interpreter.parser.ast_nodes import ASTNode, Form, Atom, Global, Routine


class ZILLoader:
    """Loads and parses ZIL source files."""

    def __init__(self):
        self.parser = Lark(ZIL_GRAMMAR, start='start', parser='lalr')
        self.transformer = ZILTransformer()

    def load_file(self, filepath: Path) -> List[ASTNode]:
        """Load and parse a ZIL file into AST.

        Args:
            filepath: Path to the .zil file

        Returns:
            List of AST nodes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not filepath.exists():
            raise FileNotFoundError(f"ZIL file not found: {filepath}")

        content = filepath.read_text()
        tree = self.parser.parse(content)
        ast = self.transformer.transform(tree)

        # Convert top-level forms to semantic nodes
        return self._process_top_level(ast)

    def _process_top_level(self, nodes: List[ASTNode]) -> List[ASTNode]:
        """Process top-level forms into semantic nodes.

        Args:
            nodes: Raw AST nodes from transformer

        Returns:
            Processed nodes with ROUTINE, GLOBAL, etc. recognized
        """
        processed = []

        for node in nodes:
            if isinstance(node, Form):
                # Recognize special forms
                op = node.operator.value.upper()

                if op == "GLOBAL" and len(node.args) >= 1:
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    value = node.args[1] if len(node.args) > 1 else None
                    processed.append(Global(name=name, value=value))

                elif op == "ROUTINE" and len(node.args) >= 2:
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    args = node.args[1] if isinstance(node.args[1], list) else []
                    body = node.args[2:] if len(node.args) > 2 else []
                    processed.append(Routine(name=name, args=args, body=body))

                else:
                    # Keep as generic form
                    processed.append(node)
            else:
                # Keep other nodes as-is
                if node is not None:
                    processed.append(node)

        return processed
```

**Step 5: Create fixtures directory**

Run: `mkdir -p tests/fixtures`

**Step 6: Run test to verify it passes**

Run: `pytest tests/parser/test_loader.py -v`
Expected: PASS (3 tests)

**Step 7: Commit**

```bash
git add zil_interpreter/parser/loader.py tests/parser/test_loader.py tests/fixtures/
git commit -m "feat(parser): add ZIL file loader

- Implement ZILLoader to parse .zil files
- Recognize GLOBAL and ROUTINE top-level forms
- Convert forms to semantic AST nodes
- Add test fixtures for parser testing
- Handle file not found errors

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 3: Game World Model

### Task 6: Game Object Implementation

**Files:**
- Create: `zil_interpreter/world/game_object.py`
- Create: `tests/world/test_game_object.py`

**Step 1: Write failing test for game objects**

Create: `tests/world/test_game_object.py`

```python
import pytest
from zil_interpreter.world.game_object import GameObject, ObjectFlag


def test_create_simple_object():
    """Test creating a basic game object."""
    lamp = GameObject(name="LAMP", description="brass lamp")
    assert lamp.name == "LAMP"
    assert lamp.description == "brass lamp"


def test_object_properties():
    """Test setting and getting object properties."""
    obj = GameObject(name="CHEST")
    obj.set_property("SIZE", 20)
    obj.set_property("CAPACITY", 100)

    assert obj.get_property("SIZE") == 20
    assert obj.get_property("CAPACITY") == 100
    assert obj.get_property("NONEXISTENT") is None


def test_object_flags():
    """Test setting and checking object flags."""
    obj = GameObject(name="DOOR")

    assert not obj.has_flag(ObjectFlag.OPEN)
    obj.set_flag(ObjectFlag.OPEN)
    assert obj.has_flag(ObjectFlag.OPEN)

    obj.clear_flag(ObjectFlag.OPEN)
    assert not obj.has_flag(ObjectFlag.OPEN)


def test_object_synonyms():
    """Test object synonyms for parser."""
    lamp = GameObject(
        name="LAMP",
        synonyms=["LAMP", "LANTERN", "LIGHT"]
    )

    assert "LAMP" in lamp.synonyms
    assert "LANTERN" in lamp.synonyms
    assert lamp.matches_word("LANTERN")
    assert not lamp.matches_word("SWORD")


def test_object_location():
    """Test object parent/location tracking."""
    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)

    assert lamp.parent == room
    assert lamp in room.children

    # Move object
    player = GameObject(name="PLAYER")
    lamp.move_to(player)

    assert lamp.parent == player
    assert lamp not in room.children
    assert lamp in player.children
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/world/test_game_object.py -v`
Expected: FAIL with "No module named 'zil_interpreter.world.game_object'"

**Step 3: Write minimal game object implementation**

Create: `zil_interpreter/world/game_object.py`

```python
"""Game object representation for ZIL world model."""

from enum import Flag, auto
from typing import Any, Dict, List, Optional, Set


class ObjectFlag(Flag):
    """Standard ZIL object flags."""
    OPEN = auto()
    CONTAINER = auto()
    SURFACE = auto()
    TAKEABLE = auto()
    LOCKED = auto()
    NDESCBIT = auto()  # No automatic description
    TOUCHBIT = auto()
    LIGHTBIT = auto()
    ONBIT = auto()  # Light is on
    INVISIBLE = auto()


class GameObject:
    """Represents a game object in the ZIL world."""

    def __init__(
        self,
        name: str,
        description: str = "",
        synonyms: Optional[List[str]] = None,
        adjectives: Optional[List[str]] = None,
        parent: Optional['GameObject'] = None
    ):
        self.name = name
        self.description = description
        self.synonyms = synonyms or []
        self.adjectives = adjectives or []
        self._parent: Optional['GameObject'] = None
        self.children: Set['GameObject'] = set()
        self.properties: Dict[str, Any] = {}
        self.flags: ObjectFlag = ObjectFlag(0)
        self.action_routine: Optional[str] = None

        if parent:
            self.move_to(parent)

    @property
    def parent(self) -> Optional['GameObject']:
        """Get object's parent/location."""
        return self._parent

    def move_to(self, new_parent: Optional['GameObject']) -> None:
        """Move object to a new parent/location."""
        # Remove from old parent
        if self._parent:
            self._parent.children.discard(self)

        # Add to new parent
        self._parent = new_parent
        if new_parent:
            new_parent.children.add(self)

    def set_property(self, prop_name: str, value: Any) -> None:
        """Set an object property."""
        self.properties[prop_name] = value

    def get_property(self, prop_name: str, default: Any = None) -> Any:
        """Get an object property."""
        return self.properties.get(prop_name, default)

    def set_flag(self, flag: ObjectFlag) -> None:
        """Set an object flag."""
        self.flags |= flag

    def clear_flag(self, flag: ObjectFlag) -> None:
        """Clear an object flag."""
        self.flags &= ~flag

    def has_flag(self, flag: ObjectFlag) -> bool:
        """Check if object has a flag set."""
        return bool(self.flags & flag)

    def matches_word(self, word: str) -> bool:
        """Check if word matches this object's synonyms."""
        word_upper = word.upper()
        return word_upper in [s.upper() for s in self.synonyms]

    def __repr__(self) -> str:
        return f"GameObject({self.name})"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/world/test_game_object.py -v`
Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/world/game_object.py tests/world/test_game_object.py
git commit -m "feat(world): add game object implementation

- Define GameObject class with properties and flags
- Support object hierarchy (parent/children)
- Implement object flags (OPEN, CONTAINER, TAKEABLE, etc.)
- Add synonym/adjective matching for parser
- Support object movement between containers

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Task 7: World State Manager

**Files:**
- Create: `zil_interpreter/world/world_state.py`
- Create: `tests/world/test_world_state.py`

**Step 1: Write failing test for world state**

Create: `tests/world/test_world_state.py`

```python
import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject


def test_create_empty_world():
    """Test creating an empty world state."""
    world = WorldState()
    assert len(world.objects) == 0
    assert len(world.globals) == 0


def test_add_object_to_world():
    """Test adding objects to world state."""
    world = WorldState()
    lamp = GameObject(name="LAMP")

    world.add_object(lamp)
    assert "LAMP" in world.objects
    assert world.get_object("LAMP") == lamp


def test_find_object_by_synonym():
    """Test finding object by synonym."""
    world = WorldState()
    lamp = GameObject(name="LAMP", synonyms=["LAMP", "LANTERN"])
    world.add_object(lamp)

    result = world.find_object_by_word("LANTERN")
    assert result == lamp


def test_global_variables():
    """Test getting and setting global variables."""
    world = WorldState()

    world.set_global("SCORE", 0)
    world.set_global("MOVES", 1)

    assert world.get_global("SCORE") == 0
    assert world.get_global("MOVES") == 1
    assert world.get_global("NONEXISTENT") is None


def test_parser_state():
    """Test parser state variables (PRSA, PRSO, PRSI)."""
    world = WorldState()

    world.set_parser_state(verb="TAKE", direct_obj="LAMP", indirect_obj=None)

    assert world.get_global("PRSA") == "TAKE"
    assert world.get_global("PRSO") == "LAMP"
    assert world.get_global("PRSI") is None


def test_current_room():
    """Test getting and setting current room."""
    world = WorldState()
    room = GameObject(name="WEST-OF-HOUSE")
    world.add_object(room)

    world.set_current_room(room)
    assert world.get_current_room() == room
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/world/test_world_state.py -v`
Expected: FAIL with "No module named 'zil_interpreter.world.world_state'"

**Step 3: Write minimal world state implementation**

Create: `zil_interpreter/world/world_state.py`

```python
"""World state manager for ZIL interpreter."""

from typing import Dict, Any, Optional, List
from zil_interpreter.world.game_object import GameObject


class WorldState:
    """Manages the complete game world state."""

    def __init__(self):
        self.objects: Dict[str, GameObject] = {}
        self.globals: Dict[str, Any] = {}
        self._current_room: Optional[GameObject] = None

        # Initialize parser state globals
        self.globals["PRSA"] = None  # PRimary Action (verb)
        self.globals["PRSO"] = None  # PRimary object
        self.globals["PRSI"] = None  # Secondary/Indirect object

    def add_object(self, obj: GameObject) -> None:
        """Add an object to the world.

        Args:
            obj: The GameObject to add
        """
        self.objects[obj.name] = obj

    def get_object(self, name: str) -> Optional[GameObject]:
        """Get an object by name.

        Args:
            name: Object name

        Returns:
            GameObject if found, None otherwise
        """
        return self.objects.get(name.upper())

    def find_object_by_word(self, word: str) -> Optional[GameObject]:
        """Find an object that matches the given word.

        Args:
            word: Word to match against object synonyms

        Returns:
            First matching GameObject, or None
        """
        for obj in self.objects.values():
            if obj.matches_word(word):
                return obj
        return None

    def set_global(self, name: str, value: Any) -> None:
        """Set a global variable.

        Args:
            name: Variable name
            value: Variable value
        """
        self.globals[name.upper()] = value

    def get_global(self, name: str, default: Any = None) -> Any:
        """Get a global variable.

        Args:
            name: Variable name
            default: Default value if not found

        Returns:
            Variable value or default
        """
        return self.globals.get(name.upper(), default)

    def set_parser_state(
        self,
        verb: Optional[str] = None,
        direct_obj: Optional[str] = None,
        indirect_obj: Optional[str] = None
    ) -> None:
        """Set parser state variables.

        Args:
            verb: Current verb (PRSA)
            direct_obj: Direct object (PRSO)
            indirect_obj: Indirect object (PRSI)
        """
        if verb is not None:
            self.globals["PRSA"] = verb.upper()
        if direct_obj is not None:
            self.globals["PRSO"] = direct_obj.upper()
        if indirect_obj is not None:
            self.globals["PRSI"] = indirect_obj.upper() if indirect_obj else None

    def set_current_room(self, room: GameObject) -> None:
        """Set the current room.

        Args:
            room: Room object
        """
        self._current_room = room
        self.globals["HERE"] = room.name

    def get_current_room(self) -> Optional[GameObject]:
        """Get the current room.

        Returns:
            Current room GameObject
        """
        return self._current_room
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/world/test_world_state.py -v`
Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/world/world_state.py tests/world/test_world_state.py
git commit -m "feat(world): add world state manager

- Implement WorldState to track game state
- Manage object registry and lookup
- Track global variables (SCORE, MOVES, etc.)
- Manage parser state (PRSA, PRSO, PRSI)
- Track current room location

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 4: Expression Evaluator

### Task 8: Basic ZIL Expression Evaluator

**Files:**
- Create: `zil_interpreter/engine/evaluator.py`
- Create: `tests/engine/test_evaluator.py`

**Step 1: Write failing test for expression evaluation**

Create: `tests/engine/test_evaluator.py`

```python
import pytest
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject, ObjectFlag


def test_evaluate_atom():
    """Test evaluating an atom (variable lookup)."""
    world = WorldState()
    world.set_global("TEST-VAR", 42)

    evaluator = Evaluator(world)
    result = evaluator.evaluate(Atom("TEST-VAR"))
    assert result == 42


def test_evaluate_string():
    """Test evaluating a string literal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(String("hello"))
    assert result == "hello"


def test_evaluate_number():
    """Test evaluating a number literal."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Number(42))
    assert result == 42


def test_evaluate_equal():
    """Test EQUAL? form."""
    world = WorldState()
    evaluator = Evaluator(world)

    form = Form(operator=Atom("EQUAL?"), args=[Number(5), Number(5)])
    assert evaluator.evaluate(form) is True

    form2 = Form(operator=Atom("EQUAL?"), args=[Number(5), Number(3)])
    assert evaluator.evaluate(form2) is False


def test_evaluate_fset_check():
    """Test FSET? form (flag check)."""
    world = WorldState()
    door = GameObject(name="DOOR")
    door.set_flag(ObjectFlag.OPEN)
    world.add_object(door)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("FSET?"), args=[Atom("DOOR"), Atom("OPENBIT")])
    assert evaluator.evaluate(form) is True


def test_evaluate_cond():
    """Test COND form (conditional)."""
    world = WorldState()
    evaluator = Evaluator(world)

    # <COND (<EQUAL? 1 1> 42)>
    form = Form(
        operator=Atom("COND"),
        args=[
            [Form(operator=Atom("EQUAL?"), args=[Number(1), Number(1)]), Number(42)]
        ]
    )
    result = evaluator.evaluate(form)
    assert result == 42


def test_evaluate_verb_check():
    """Test VERB? form."""
    world = WorldState()
    world.set_parser_state(verb="TAKE")

    evaluator = Evaluator(world)

    form = Form(operator=Atom("VERB?"), args=[Atom("TAKE")])
    assert evaluator.evaluate(form) is True

    form2 = Form(operator=Atom("VERB?"), args=[Atom("DROP")])
    assert evaluator.evaluate(form2) is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/test_evaluator.py -v`
Expected: FAIL with "No module named 'zil_interpreter.engine.evaluator'"

**Step 3: Write minimal evaluator implementation**

Create: `zil_interpreter/engine/evaluator.py`

```python
"""ZIL expression evaluator."""

from typing import Any, Optional
from zil_interpreter.parser.ast_nodes import Form, Atom, String, Number, ASTNode
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import ObjectFlag


class Evaluator:
    """Evaluates ZIL expressions in the context of world state."""

    # Map ZIL flag names to ObjectFlag enum
    FLAG_MAP = {
        "OPENBIT": ObjectFlag.OPEN,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "TAKEABLEBIT": ObjectFlag.TAKEABLE,
        "LOCKEDBIT": ObjectFlag.LOCKED,
        "NDESCBIT": ObjectFlag.NDESCBIT,
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "ONBIT": ObjectFlag.ONBIT,
    }

    def __init__(self, world: WorldState):
        self.world = world

    def evaluate(self, expr: Any) -> Any:
        """Evaluate a ZIL expression.

        Args:
            expr: Expression to evaluate

        Returns:
            Result of evaluation
        """
        if isinstance(expr, Number):
            return expr.value

        elif isinstance(expr, String):
            return expr.value

        elif isinstance(expr, Atom):
            # Variable lookup
            return self.world.get_global(expr.value)

        elif isinstance(expr, Form):
            return self._evaluate_form(expr)

        elif isinstance(expr, list):
            # Evaluate each element
            return [self.evaluate(item) for item in expr]

        else:
            return expr

    def _evaluate_form(self, form: Form) -> Any:
        """Evaluate a form (function call).

        Args:
            form: Form to evaluate

        Returns:
            Result of form evaluation
        """
        op = form.operator.value.upper()

        if op == "EQUAL?":
            return self._eval_equal(form.args)

        elif op == "FSET?":
            return self._eval_fset_check(form.args)

        elif op == "VERB?":
            return self._eval_verb_check(form.args)

        elif op == "COND":
            return self._eval_cond(form.args)

        else:
            raise NotImplementedError(f"Form not implemented: {op}")

    def _eval_equal(self, args: list) -> bool:
        """Evaluate EQUAL? comparison."""
        if len(args) < 2:
            return False
        val1 = self.evaluate(args[0])
        val2 = self.evaluate(args[1])
        return val1 == val2

    def _eval_fset_check(self, args: list) -> bool:
        """Evaluate FSET? flag check."""
        if len(args) < 2:
            return False

        obj_name = self.evaluate(args[0])
        flag_name = self.evaluate(args[1]) if isinstance(args[1], Atom) else args[1].value

        obj = self.world.get_object(obj_name)
        if not obj:
            return False

        flag = self.FLAG_MAP.get(flag_name.upper())
        if not flag:
            return False

        return obj.has_flag(flag)

    def _eval_verb_check(self, args: list) -> bool:
        """Evaluate VERB? check."""
        if not args:
            return False

        verb_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        current_verb = self.world.get_global("PRSA")

        return current_verb == verb_name.upper()

    def _eval_cond(self, args: list) -> Any:
        """Evaluate COND conditional.

        Args:
            args: List of [condition, result] pairs

        Returns:
            Result of first true condition
        """
        for clause in args:
            if isinstance(clause, list) and len(clause) >= 2:
                condition = clause[0]
                result_expr = clause[1]

                if self.evaluate(condition):
                    return self.evaluate(result_expr)

        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/test_evaluator.py -v`
Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/engine/evaluator.py tests/engine/test_evaluator.py
git commit -m "feat(engine): add ZIL expression evaluator

- Implement basic expression evaluation
- Support literals (numbers, strings, atoms)
- Implement EQUAL?, FSET?, VERB? operations
- Add COND conditional evaluation
- Map ZIL flag names to ObjectFlag enum

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 5: Output and Runtime

### Task 9: Output Buffer

**Files:**
- Create: `zil_interpreter/runtime/output_buffer.py`
- Create: `tests/runtime/test_output_buffer.py`

**Step 1: Write failing test for output buffer**

Create: `tests/runtime/test_output_buffer.py`

```python
import pytest
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_create_empty_buffer():
    """Test creating an empty output buffer."""
    buffer = OutputBuffer()
    assert buffer.get_output() == ""


def test_write_to_buffer():
    """Test writing text to buffer."""
    buffer = OutputBuffer()
    buffer.write("Hello")
    buffer.write(" ")
    buffer.write("world")

    assert buffer.get_output() == "Hello world"


def test_flush_buffer():
    """Test flushing buffer clears it."""
    buffer = OutputBuffer()
    buffer.write("Test")

    output = buffer.flush()
    assert output == "Test"
    assert buffer.get_output() == ""


def test_write_line():
    """Test writing a line with newline."""
    buffer = OutputBuffer()
    buffer.writeln("Line 1")
    buffer.writeln("Line 2")

    assert buffer.get_output() == "Line 1\nLine 2\n"


def test_tell_directive():
    """Test TELL directive formatting."""
    buffer = OutputBuffer()
    buffer.tell("You are in a room.")
    buffer.tell("There is a lamp here.")

    output = buffer.get_output()
    assert "You are in a room" in output
    assert "There is a lamp here" in output
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/runtime/test_output_buffer.py -v`
Expected: FAIL with "No module named 'zil_interpreter.runtime.output_buffer'"

**Step 3: Write minimal output buffer implementation**

Create: `zil_interpreter/runtime/output_buffer.py`

```python
"""Output buffer for game text."""

from typing import List


class OutputBuffer:
    """Manages game output text."""

    def __init__(self):
        self._buffer: List[str] = []

    def write(self, text: str) -> None:
        """Write text to buffer without newline.

        Args:
            text: Text to write
        """
        self._buffer.append(text)

    def writeln(self, text: str) -> None:
        """Write text to buffer with newline.

        Args:
            text: Text to write
        """
        self._buffer.append(text)
        self._buffer.append("\n")

    def tell(self, text: str) -> None:
        """Write text in TELL format (for ZIL TELL directive).

        Args:
            text: Text to output
        """
        self.write(text)

    def get_output(self) -> str:
        """Get current buffer contents.

        Returns:
            Buffer contents as string
        """
        return "".join(self._buffer)

    def flush(self) -> str:
        """Get buffer contents and clear buffer.

        Returns:
            Buffer contents as string
        """
        output = self.get_output()
        self._buffer.clear()
        return output

    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer.clear()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/runtime/test_output_buffer.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/runtime/output_buffer.py tests/runtime/test_output_buffer.py
git commit -m "feat(runtime): add output buffer

- Implement OutputBuffer for managing game text
- Support write, writeln, and tell methods
- Add flush and clear functionality
- Buffer accumulates text until flushed to CLI

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 6: Basic CLI REPL

### Task 10: Minimal REPL Implementation

**Files:**
- Create: `zil_interpreter/cli/repl.py`
- Create: `tests/cli/test_repl.py`

**Step 1: Write failing test for REPL**

Create: `tests/cli/test_repl.py`

```python
import pytest
from io import StringIO
from unittest.mock import Mock, patch
from zil_interpreter.cli.repl import REPL
from zil_interpreter.world.world_state import WorldState


def test_create_repl():
    """Test creating a REPL instance."""
    world = WorldState()
    repl = REPL(world)
    assert repl.world == world


def test_repl_welcome_message():
    """Test REPL displays welcome message."""
    world = WorldState()
    repl = REPL(world)

    output = StringIO()
    with patch('sys.stdout', output):
        repl.display_welcome()

    result = output.getvalue()
    assert "ZIL Interpreter" in result


def test_repl_prompt():
    """Test REPL prompt."""
    world = WorldState()
    repl = REPL(world)

    assert repl.get_prompt() == "> "


def test_process_quit_command():
    """Test processing quit command."""
    world = WorldState()
    repl = REPL(world)

    assert repl.should_quit("quit") is True
    assert repl.should_quit("exit") is True
    assert repl.should_quit("q") is True
    assert repl.should_quit("take lamp") is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cli/test_repl.py -v`
Expected: FAIL with "No module named 'zil_interpreter.cli.repl'"

**Step 3: Write minimal REPL implementation**

Create: `zil_interpreter/cli/repl.py`

```python
"""REPL (Read-Eval-Print Loop) for ZIL interpreter."""

import sys
from typing import Optional
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer


class REPL:
    """Interactive REPL for playing ZIL games."""

    def __init__(self, world: WorldState):
        self.world = world
        self.output = OutputBuffer()
        self.running = False

    def display_welcome(self) -> None:
        """Display welcome message."""
        print("=" * 60)
        print("ZIL Interpreter v0.1.0")
        print("Python interpreter for Zork Implementation Language")
        print("=" * 60)
        print()
        print("Commands: quit, exit, q - Exit the interpreter")
        print("          save <file> - Save game state")
        print("          restore <file> - Restore game state")
        print()

    def get_prompt(self) -> str:
        """Get the input prompt.

        Returns:
            Prompt string
        """
        return "> "

    def should_quit(self, command: str) -> bool:
        """Check if command is a quit command.

        Args:
            command: User input

        Returns:
            True if should quit
        """
        return command.strip().lower() in ("quit", "exit", "q")

    def run(self) -> None:
        """Run the main REPL loop."""
        self.running = True
        self.display_welcome()

        # Display initial room description if available
        current_room = self.world.get_current_room()
        if current_room and current_room.description:
            print(current_room.description)
            print()

        while self.running:
            try:
                command = input(self.get_prompt())

                if self.should_quit(command):
                    print("Goodbye!")
                    break

                # Process command (placeholder for now)
                self.process_command(command)

            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

    def process_command(self, command: str) -> None:
        """Process a user command.

        Args:
            command: User input
        """
        # Placeholder - will be implemented with command parser
        if command.strip():
            print(f"[Command not yet implemented: {command}]")


def main() -> None:
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage: zil <path-to-zil-file>")
        sys.exit(1)

    # TODO: Load ZIL file and initialize world
    print(f"Loading: {sys.argv[1]}")
    print("Note: File loading not yet implemented")

    world = WorldState()
    repl = REPL(world)
    repl.run()


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/cli/test_repl.py -v`
Expected: PASS (4 tests)

**Step 5: Test CLI manually**

Run: `python -m zil_interpreter.cli.repl dummy.zil`
Expected: Shows welcome message and prompt (exit with 'quit')

**Step 6: Commit**

```bash
git add zil_interpreter/cli/repl.py tests/cli/test_repl.py
git commit -m "feat(cli): add basic REPL implementation

- Implement REPL class with welcome message
- Add command prompt and quit handling
- Create main entry point for CLI
- Add placeholder for command processing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Next Steps

This plan covers the foundation. Continue with:

1. **Task 11-15**: Extend evaluator with TELL, MOVE, FSET, FCLEAR operations
2. **Task 16-20**: Implement routine executor to run ZIL routines
3. **Task 21-25**: Build command parser using syntax definitions
4. **Task 26-30**: Wire up REPL to command parser and story engine
5. **Task 31-35**: Load actual Zork I .zil files and build world
6. **Task 36-40**: Implement save/restore functionality
7. **Task 41+**: Extend ZIL language support for full Zork I compatibility

**Reference Skills:**
- Use @superpowers:test-driven-development for all implementation
- Use @superpowers:systematic-debugging when encountering issues
- Use @superpowers:verification-before-completion before claiming done

**Development Principles:**
- Write test first, watch it fail, implement minimal code, watch it pass, commit
- Keep tasks small (2-5 minutes each)
- Commit frequently with descriptive messages
- DRY - don't repeat yourself
- YAGNI - implement only what's needed now
