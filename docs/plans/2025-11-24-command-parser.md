# Command Parser & REPL Integration - Tasks 21-25

**Date:** 2025-11-24
**Goal:** Implement command parser to convert player text input into game actions, and wire the REPL to the game engine.

## Overview

To make the interpreter interactive, we need:
- Command parser (tokenize and parse player input like "take lamp")
- Verb resolution (map "take" to TAKE action)
- Object resolution (find "lamp" object in world)
- Parser state management (set PRSA, PRSO, PRSI)
- REPL integration (connect CLI to game engine)

---

## Task 21: Basic Command Parser

### Step 1: Write failing test

Create `tests/engine/test_command_parser.py`:

```python
import pytest
from zil_interpreter.engine.command_parser import CommandParser
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject


def test_parse_simple_command():
    """Test parsing simple one-word command."""
    world = WorldState()
    parser = CommandParser(world)

    result = parser.parse("look")

    assert result is not None
    assert result['verb'] == 'LOOK'
    assert result['direct_object'] is None
    assert result['indirect_object'] is None


def test_parse_verb_object():
    """Test parsing verb with direct object."""
    world = WorldState()
    lamp = GameObject(name="LAMP", synonyms=["LAMP", "LANTERN"])
    world.add_object(lamp)

    parser = CommandParser(world)
    result = parser.parse("take lamp")

    assert result is not None
    assert result['verb'] == 'TAKE'
    assert result['direct_object'] == 'LAMP'
    assert result['indirect_object'] is None


def test_parse_verb_two_objects():
    """Test parsing verb with direct and indirect objects."""
    world = WorldState()
    lamp = GameObject(name="LAMP", synonyms=["LAMP", "LANTERN"])
    box = GameObject(name="BOX", synonyms=["BOX", "CONTAINER"])
    world.add_object(lamp)
    world.add_object(box)

    parser = CommandParser(world)
    result = parser.parse("put lamp in box")

    assert result is not None
    assert result['verb'] == 'PUT'
    assert result['direct_object'] == 'LAMP'
    assert result['indirect_object'] == 'BOX'
```

### Step 2: Implement CommandParser

Create `zil_interpreter/engine/command_parser.py`:

```python
"""Command parser for player input."""

from typing import Optional, Dict, List
from zil_interpreter.world.world_state import WorldState


class CommandParser:
    """Parses player commands into structured actions."""

    # Common verbs and their variations
    VERBS = {
        'LOOK': ['look', 'l'],
        'TAKE': ['take', 'get', 'pick up'],
        'DROP': ['drop', 'put down'],
        'INVENTORY': ['inventory', 'i'],
        'GO': ['go', 'walk', 'run'],
        'NORTH': ['north', 'n'],
        'SOUTH': ['south', 's'],
        'EAST': ['east', 'e'],
        'WEST': ['west', 'w'],
        'UP': ['up', 'u'],
        'DOWN': ['down', 'd'],
        'OPEN': ['open'],
        'CLOSE': ['close'],
        'EXAMINE': ['examine', 'x', 'inspect'],
        'READ': ['read'],
        'PUT': ['put', 'place'],
    }

    # Prepositions to ignore/handle
    PREPOSITIONS = ['in', 'on', 'with', 'to', 'at', 'from']

    def __init__(self, world: WorldState):
        self.world = world

    def parse(self, command: str) -> Optional[Dict]:
        """Parse a player command.

        Args:
            command: Player input string

        Returns:
            Dict with verb, direct_object, indirect_object
            or None if parsing fails
        """
        # Tokenize
        tokens = command.lower().strip().split()
        if not tokens:
            return None

        # Find verb
        verb = self._find_verb(tokens)
        if not verb:
            return None

        # Remove verb from tokens
        verb_token = self._get_verb_token(tokens[0])
        if verb_token:
            tokens = tokens[1:]
        else:
            # Multi-word verb like "pick up"
            for i in range(len(tokens)):
                test_phrase = ' '.join(tokens[:i+1])
                if self._get_verb_token(test_phrase):
                    tokens = tokens[i+1:]
                    break

        # Remove prepositions and find objects
        cleaned_tokens = []
        prep_index = -1

        for i, token in enumerate(tokens):
            if token in self.PREPOSITIONS:
                prep_index = i
                break
            cleaned_tokens.append(token)

        # Direct object (before preposition)
        direct_obj = None
        if cleaned_tokens:
            direct_obj = self._find_object(' '.join(cleaned_tokens))

        # Indirect object (after preposition)
        indirect_obj = None
        if prep_index >= 0 and prep_index + 1 < len(tokens):
            remaining = ' '.join(tokens[prep_index + 1:])
            indirect_obj = self._find_object(remaining)

        return {
            'verb': verb,
            'direct_object': direct_obj,
            'indirect_object': indirect_obj
        }

    def _find_verb(self, tokens: List[str]) -> Optional[str]:
        """Find verb in tokens."""
        # Try first token
        verb = self._get_verb_token(tokens[0])
        if verb:
            return verb

        # Try multi-word verbs
        for i in range(min(3, len(tokens))):
            phrase = ' '.join(tokens[:i+1])
            verb = self._get_verb_token(phrase)
            if verb:
                return verb

        return None

    def _get_verb_token(self, token: str) -> Optional[str]:
        """Get canonical verb for token."""
        for canonical, variations in self.VERBS.items():
            if token in variations:
                return canonical
        return None

    def _find_object(self, text: str) -> Optional[str]:
        """Find object matching text."""
        obj = self.world.find_object_by_word(text)
        return obj.name if obj else None
```

### Step 3: Commit

```bash
git add tests/engine/test_command_parser.py zil_interpreter/engine/command_parser.py
git commit -m "feat(engine): add basic command parser

- Parse player commands into structured actions
- Support verb resolution with synonyms
- Find objects by synonyms in world state
- Handle prepositions (in, on, with, etc.)
- Parse single verb, verb+object, verb+obj+prep+obj

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 22: Game Engine Integration

### Step 1: Write failing test

Create `tests/engine/test_game_engine.py`:

```python
import pytest
from zil_interpreter.engine.game_engine import GameEngine
from zil_interpreter.parser.ast_nodes import Routine, Form, Atom, String
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_game_engine_initialization():
    """Test GameEngine initializes components."""
    world = WorldState()
    output = OutputBuffer()
    engine = GameEngine(world, output)

    assert engine.world is world
    assert engine.output is output
    assert engine.parser is not None
    assert engine.executor is not None


def test_game_engine_execute_command():
    """Test executing a simple command."""
    world = WorldState()
    output = OutputBuffer()
    engine = GameEngine(world, output)

    # Register a LOOK routine
    look_routine = Routine(
        name="V-LOOK",
        args=[],
        body=[Form(operator=Atom("TELL"), args=[String("You look around.")])]
    )
    engine.executor.register_routine(look_routine)

    # Execute "look" command
    engine.execute_command("look")

    assert "You look around." in output.get_output()


def test_game_engine_sets_parser_state():
    """Test engine sets PRSA, PRSO, PRSI."""
    world = WorldState()
    output = OutputBuffer()
    engine = GameEngine(world, output)

    lamp = GameObject(name="LAMP", synonyms=["LAMP"])
    world.add_object(lamp)

    # Register TAKE routine
    take_routine = Routine(
        name="V-TAKE",
        args=[],
        body=[Form(operator=Atom("TELL"), args=[String("Taken.")])]
    )
    engine.executor.register_routine(take_routine)

    # Execute "take lamp"
    engine.execute_command("take lamp")

    assert world.get_global("PRSA") == "V-TAKE"
    assert world.get_global("PRSO") == "LAMP"
```

### Step 2: Implement GameEngine

Create `zil_interpreter/engine/game_engine.py`:

```python
"""Game engine - coordinates parser, executor, and world state."""

from typing import Optional
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.command_parser import CommandParser
from zil_interpreter.engine.routine_executor import RoutineExecutor


class GameEngine:
    """Main game engine coordinating all components."""

    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
        self.parser = CommandParser(world)
        self.executor = RoutineExecutor(world, self.output)

    def execute_command(self, command: str) -> bool:
        """Execute a player command.

        Args:
            command: Player input string

        Returns:
            True if command was recognized and executed
        """
        # Parse command
        parsed = self.parser.parse(command)
        if not parsed:
            self.output.write("I don't understand that.\n")
            return False

        verb = parsed['verb']
        direct_obj = parsed['direct_object']
        indirect_obj = parsed['indirect_object']

        # Set parser state
        self.world.set_parser_state(
            verb=f"V-{verb}",
            direct_obj=direct_obj,
            indirect_obj=indirect_obj
        )

        # Try to call verb routine
        routine_name = f"V-{verb}"
        try:
            self.executor.call_routine(routine_name, [])
            return True
        except ValueError:
            # Routine not found
            self.output.write(f"I don't know how to {verb.lower()}.\n")
            return False
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add game engine integration

- Create GameEngine to coordinate components
- Parse commands and set parser state (PRSA, PRSO, PRSI)
- Call verb routines (V-VERB naming convention)
- Handle unknown commands gracefully

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 23: Wire REPL to Game Engine

### Step 1: Update REPL implementation

Modify `zil_interpreter/cli/repl.py`:

```python
from zil_interpreter.engine.game_engine import GameEngine

class REPL:
    """Interactive REPL for playing ZIL games."""

    def __init__(self, world: WorldState):
        self.world = world
        self.output = OutputBuffer()
        self.engine = GameEngine(world, self.output)
        self.running = False

    def process_command(self, command: str) -> None:
        """Process a user command."""
        if not command.strip():
            return

        # Execute command through game engine
        self.engine.execute_command(command)

        # Display output
        output = self.output.flush()
        if output:
            print(output)
```

### Step 2: Update tests

Update `tests/cli/test_repl.py`:

```python
def test_repl_executes_commands():
    """Test REPL executes commands through game engine."""
    from zil_interpreter.parser.ast_nodes import Routine, Form, Atom, String

    world = WorldState()
    repl = REPL(world)

    # Register a test routine
    routine = Routine(
        name="V-LOOK",
        args=[],
        body=[Form(operator=Atom("TELL"), args=[String("Test output")])]
    )
    repl.engine.executor.register_routine(routine)

    # Capture output
    import io
    import sys
    captured = io.StringIO()
    sys.stdout = captured

    repl.process_command("look")

    sys.stdout = sys.__stdout__
    result = captured.getvalue()

    assert "Test output" in result
```

### Step 3: Commit

```bash
git commit -m "feat(cli): wire REPL to game engine

- Connect REPL to GameEngine for command execution
- Display engine output after each command
- Flush output buffer after command execution
- Update REPL tests for engine integration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 24: Load Zork I Files

### Step 1: Create world loader

Create `zil_interpreter/loader/world_loader.py`:

```python
"""Load ZIL files and build game world."""

from pathlib import Path
from typing import List
from zil_interpreter.parser.loader import ZILLoader
from zil_interpreter.parser.ast_nodes import Global, Routine, Object as ObjectNode
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.engine.routine_executor import RoutineExecutor
from zil_interpreter.runtime.output_buffer import OutputBuffer


class WorldLoader:
    """Loads ZIL files and builds game world."""

    def __init__(self):
        self.zil_loader = ZILLoader()

    def load_world(self, main_file: Path) -> tuple[WorldState, RoutineExecutor]:
        """Load game world from ZIL files.

        Args:
            main_file: Path to main .zil file

        Returns:
            Tuple of (WorldState, RoutineExecutor)
        """
        # Load and parse main file
        ast = self.zil_loader.load_file(main_file)

        # Create world and executor
        world = WorldState()
        output = OutputBuffer()
        executor = RoutineExecutor(world, output)

        # Process AST nodes
        for node in ast:
            if isinstance(node, Global):
                world.set_global(node.name, self._eval_value(node.value))

            elif isinstance(node, Routine):
                executor.register_routine(node)

            elif isinstance(node, ObjectNode):
                self._create_object(world, node)

        return world, executor

    def _eval_value(self, value):
        """Evaluate a simple value (Number, String, Atom)."""
        from zil_interpreter.parser.ast_nodes import Number, String, Atom

        if isinstance(value, Number):
            return value.value
        elif isinstance(value, String):
            return value.value
        elif isinstance(value, Atom):
            return value.value
        return value

    def _create_object(self, world: WorldState, obj_node: ObjectNode):
        """Create GameObject from Object AST node."""
        # Create game object
        game_obj = GameObject(name=obj_node.name)

        # Set properties from AST
        for prop_name, prop_value in obj_node.properties.items():
            if prop_name == "DESC":
                game_obj.description = self._eval_value(prop_value)
            elif prop_name == "SYNONYM":
                # Handle synonym list
                if isinstance(prop_value, list):
                    game_obj.synonyms = [self._eval_value(v) for v in prop_value]
            else:
                game_obj.set_property(prop_name, self._eval_value(prop_value))

        world.add_object(game_obj)
```

### Step 2: Update main CLI

Update `zil_interpreter/cli/repl.py` `main()` function:

```python
def main() -> None:
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage: zil <path-to-zil-file>")
        sys.exit(1)

    zil_file = Path(sys.argv[1])
    if not zil_file.exists():
        print(f"Error: File not found: {zil_file}")
        sys.exit(1)

    # Load game world
    from zil_interpreter.loader.world_loader import WorldLoader
    loader = WorldLoader()

    try:
        world, executor = loader.load_world(zil_file)
        print(f"Loaded: {zil_file}")
        print(f"Routines: {len(executor.routines)}")
        print(f"Objects: {len(world.objects)}")
        print()
    except Exception as e:
        print(f"Error loading game: {e}")
        sys.exit(1)

    # Create REPL with loaded world
    repl = REPL(world)
    repl.engine.executor = executor  # Use loaded executor
    repl.run()
```

### Step 3: Commit

```bash
git commit -m "feat(loader): add world loader for ZIL files

- Create WorldLoader to build game from AST
- Load globals, routines, and objects
- Wire loaded world to REPL
- Update CLI to load .zil files on startup

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 25: Test with Simple Game

### Step 1: Create test game file

Create `tests/fixtures/simple_game.zil`:

```zil
"Simple test game"

<GLOBAL SCORE 0>

<OBJECT ROOM
    (DESC "a small room")>

<OBJECT LAMP
    (IN ROOM)
    (SYNONYM LAMP LANTERN)
    (DESC "brass lamp")>

<ROUTINE V-LOOK ()
    <TELL "You are in " <GETP ,HERE DESC> "." CR>>

<ROUTINE V-TAKE ()
    <COND (<IN? ,PRSO ,HERE>
           <MOVE ,PRSO ,PLAYER>
           <TELL "Taken." CR>)
          (T <TELL "You can't see that here." CR>)>>

<ROUTINE V-INVENTORY ()
    <TELL "You are carrying: " CR>
    <TELL "Nothing." CR>>
```

### Step 2: Create integration test

```python
def test_simple_game_integration():
    """Test loading and playing a simple game."""
    from zil_interpreter.loader.world_loader import WorldLoader
    from pathlib import Path

    loader = WorldLoader()
    test_file = Path(__file__).parent.parent / "fixtures" / "simple_game.zil"

    world, executor = loader.load_world(test_file)

    # Verify world loaded
    assert world.get_global("SCORE") == 0
    assert "ROOM" in world.objects
    assert "LAMP" in world.objects

    # Verify routines loaded
    assert "V-LOOK" in executor.routines
    assert "V-TAKE" in executor.routines
```

### Step 3: Commit

```bash
git commit -m "test: add simple game integration test

- Create simple_game.zil test fixture
- Test world loading from file
- Verify globals, objects, routines loaded
- End-to-end integration test

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Completion

After Tasks 21-25, we have:
- ✅ Command parser (player input → structured commands)
- ✅ Game engine (coordinates all components)
- ✅ REPL integration (interactive gameplay)
- ✅ World loader (load .zil files)
- ✅ Integration tests (end-to-end validation)

The interpreter is now playable with simple ZIL games!
