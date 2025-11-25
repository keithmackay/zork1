# Output Buffer Unification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix TELL routine output not appearing in CLI by ensuring all components share a single OutputBuffer instance.

**Architecture:** Modify WorldLoader to accept OutputBuffer as parameter instead of creating its own. GameCLI and REPL create the buffer and pass it to all components. This ensures TELL writes to the same buffer that CLI reads from.

**Tech Stack:** Python 3.12, pytest, ZIL interpreter

---

## Task 1: Write Test for TELL Output

**Files:**
- Create: `tests/test_tell_output.py`

**Step 1: Write the failing test**

```python
"""Test that TELL routine output appears correctly."""

from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_tell_routine_produces_output():
    """Test that V-LOOK routine using TELL writes to output buffer."""
    # Create single output buffer
    output = OutputBuffer()

    # Load world with shared buffer
    loader = WorldLoader()
    world, executor = loader.load_world(
        Path('tests/fixtures/simple_game.zil'),
        output
    )

    # Call V-LOOK routine which uses <TELL "You are in a small room." CR>
    executor.call_routine('V-LOOK', [])

    # Get output from the shared buffer
    result = output.flush()

    # Verify output contains the TELL text
    assert "You are in a small room" in result
    assert result == "You are in a small room.\n"


def test_multiple_tell_calls_accumulate():
    """Test that multiple TELL calls accumulate in buffer."""
    output = OutputBuffer()

    loader = WorldLoader()
    world, executor = loader.load_world(
        Path('tests/fixtures/simple_game.zil'),
        output
    )

    # Call multiple routines
    executor.call_routine('V-LOOK', [])
    executor.call_routine('V-INVENTORY', [])

    result = output.flush()

    # Both outputs should be present
    assert "You are in a small room" in result
    assert "You are carrying nothing" in result
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_tell_output.py -v`

Expected output:
```
FAILED tests/test_tell_output.py::test_tell_routine_produces_output - TypeError: load_world() takes 2 positional arguments but 3 were given
```

**Step 3: Commit the failing test**

```bash
git add tests/test_tell_output.py
git commit -m "test: add failing test for TELL output buffer sharing"
```

---

## Task 2: Modify WorldLoader to Accept OutputBuffer

**Files:**
- Modify: `zil_interpreter/loader/world_loader.py:19-47`

**Step 1: Update load_world signature**

```python
# In zil_interpreter/loader/world_loader.py

def load_world(self, main_file: Path, output: OutputBuffer) -> Tuple[WorldState, RoutineExecutor]:
    """Load game world from ZIL files.

    Args:
        main_file: Path to main .zil file
        output: OutputBuffer instance to use for all components

    Returns:
        Tuple of (WorldState, RoutineExecutor)
    """
    # Load and parse main file
    ast = self.zil_loader.load_file(main_file)

    # Create world and executor with provided output buffer
    world = WorldState()
    executor = RoutineExecutor(world, output)  # Use provided buffer, don't create new one

    # Process AST nodes
    for node in ast:
        if isinstance(node, Global):
            world.set_global(node.name, self._eval_value(node.value))

        elif isinstance(node, Routine):
            executor.register_routine(node)

        elif isinstance(node, ObjectNode):
            self._create_object(world, node)

    return world, executor
```

**Step 2: Run test to verify it passes**

Run: `python3 -m pytest tests/test_tell_output.py::test_tell_routine_produces_output -v`

Expected: PASS

**Step 3: Run full test suite**

Run: `python3 -m pytest tests/test_tell_output.py -v`

Expected: Both tests PASS

**Step 4: Commit**

```bash
git add zil_interpreter/loader/world_loader.py
git commit -m "feat: make WorldLoader accept OutputBuffer parameter

- Change load_world() signature to accept OutputBuffer
- Use provided buffer instead of creating new one
- Ensures all components share same buffer instance
- Fixes TELL output not appearing in CLI"
```

---

## Task 3: Update GameCLI to Pass OutputBuffer

**Files:**
- Modify: `zil_interpreter/cli/game_cli.py:30-58`

**Step 1: Update load_game method**

```python
# In zil_interpreter/cli/game_cli.py, update load_game() method

def load_game(self) -> bool:
    """Load the game file.

    Returns:
        True if successful
    """
    try:
        loader = WorldLoader()
        # Pass CLI's output buffer to loader - ensures shared instance
        self.world, executor = loader.load_world(self.game_file, self.output_buffer)

        if not self.world:
            self._error("Failed to load game world")
            return False

        # Create game engine with the SAME output buffer
        self.engine = GameEngine(self.world, self.output_buffer)
        self.engine.executor = executor

        if not self.json_mode:
            print(f"Loaded: {self.game_file.name}")
            print(f"Objects: {len(self.world.objects)}")
            print(f"Routines: {len(executor.routines)}")
            print()

        return True

    except Exception as e:
        self._error(f"Failed to load game: {e}")
        return False
```

**Step 2: Test manually with simple game**

Run: `echo "look" | python3 -m zil_interpreter tests/fixtures/simple_game.zil --json`

Expected output:
```json
{"type": "init", "output": "You are in a small room.\n", "room": "unknown"}
{"type": "response", "command": "look", "output": "You are in a small room.\n", "is_dead": false, "is_complete": false}
```

**Step 3: Commit**

```bash
git add zil_interpreter/cli/game_cli.py
git commit -m "fix: GameCLI passes output buffer to WorldLoader

- Update load_game() to pass self.output_buffer to loader
- Ensures GameEngine and RoutineExecutor share same buffer
- TELL output now appears in CLI"
```

---

## Task 4: Update REPL to Use New Signature

**Files:**
- Modify: `zil_interpreter/cli/repl.py:94-126`

**Step 1: Update main() function**

```python
# In zil_interpreter/cli/repl.py

def main() -> None:
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage: zil <path-to-zil-file>")
        sys.exit(1)

    from pathlib import Path
    from zil_interpreter.loader.world_loader import WorldLoader

    zil_file = Path(sys.argv[1])
    if not zil_file.exists():
        print(f"Error: File not found: {zil_file}")
        sys.exit(1)

    # Create output buffer BEFORE loading world
    from zil_interpreter.runtime.output_buffer import OutputBuffer
    output = OutputBuffer()

    # Load game world with shared output buffer
    loader = WorldLoader()

    try:
        world, executor = loader.load_world(zil_file, output)
        print(f"Loaded: {zil_file}")
        print(f"Routines: {len(executor.routines)}")
        print(f"Objects: {len(world.objects)}")
        print()
    except Exception as e:
        print(f"Error loading game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Create REPL with loaded world
    repl = REPL(world)
    repl.engine.executor = executor  # Use loaded executor
    repl.run()
```

**Step 2: Test REPL manually**

Run: `python3 -m zil_interpreter.cli.repl tests/fixtures/simple_game.zil`

Then type: `look`

Expected: See "You are in a small room." output

**Step 3: Commit**

```bash
git add zil_interpreter/cli/repl.py
git commit -m "fix: update REPL to use new WorldLoader signature

- Create OutputBuffer before loading world
- Pass buffer to load_world()
- Maintains backward compatibility for REPL users"
```

---

## Task 5: Add Integration Test for CLI

**Files:**
- Create: `tests/test_cli_tell_integration.py`

**Step 1: Write integration test**

```python
"""Integration test for CLI TELL output."""

import json
from pathlib import Path
from zil_interpreter.cli.game_cli import GameCLI


def test_cli_look_command_shows_output():
    """Test that 'look' command shows TELL output in JSON mode."""
    cli = GameCLI(Path('tests/fixtures/simple_game.zil'), json_mode=True)

    # Load game
    assert cli.load_game() is True

    # Process 'look' command
    cli._process_command("look")

    # Get output from buffer
    output = cli.output_buffer.flush()

    # Should contain the TELL text from V-LOOK
    assert "You are in a small room" in output


def test_cli_initial_state_shows_output():
    """Test that initial game state executes look and shows output."""
    cli = GameCLI(Path('tests/fixtures/simple_game.zil'), json_mode=True)

    # Load game (triggers _display_initial_state)
    assert cli.load_game() is True

    # Check that output buffer has content from initial look
    # Note: _display_initial_state calls execute_command("look")
    # and the output should be in the buffer or displayed
    # This verifies the full integration works
```

**Step 2: Run integration tests**

Run: `python3 -m pytest tests/test_cli_tell_integration.py -v`

Expected: PASS

**Step 3: Commit**

```bash
git add tests/test_cli_tell_integration.py
git commit -m "test: add integration tests for CLI TELL output

- Test look command shows TELL output
- Verify initial state displays correctly
- End-to-end validation of buffer sharing"
```

---

## Task 6: Run Full Test Suite and Verify

**Step 1: Run all tests**

Run: `python3 -m pytest tests/ -v --tb=short`

Expected: All tests pass (except pre-existing NEXT? test failure)

**Step 2: Test manually with Bun UI**

Run in separate terminal:
```bash
cd zork-ui
bun run start
```

Then:
1. Select option 1 (Start New Game)
2. Select option 4 (Test Game)
3. Type `look`

Expected: See "You are in a small room." output

**Step 3: Final verification**

Run: `python3 -m pytest tests/test_tell_output.py tests/test_cli_tell_integration.py -v`

Expected: All TELL-related tests PASS

---

## Task 7: Update Documentation

**Files:**
- Modify: `README.md` (if exists, add usage example)
- Already have: `docs/plans/2025-11-24-output-buffer-unification-design.md`

**Step 1: Add example to README (if applicable)**

If README.md exists and has usage examples, add:

```markdown
### Using the Interpreter

The interpreter now properly displays TELL output:

```bash
# Run a game
python3 -m zil_interpreter tests/fixtures/simple_game.zil

# JSON mode (for Bun UI integration)
python3 -m zil_interpreter tests/fixtures/simple_game.zil --json
```

Output from TELL directives will now appear correctly.
```

**Step 2: Commit documentation**

```bash
git add README.md  # only if modified
git commit -m "docs: update README with TELL output fix notes"
```

---

## Task 8: Final Cleanup and Push

**Step 1: Review all changes**

Run: `git log --oneline main..HEAD`

Expected: See all commits for this feature

**Step 2: Run final test suite**

Run: `python3 -m pytest tests/ -x`

Expected: Tests pass (except pre-existing NEXT? failure)

**Step 3: Create summary commit (if needed)**

If any final tweaks needed, commit them:

```bash
git add .
git commit -m "chore: final cleanup for output buffer unification"
```

**Step 4: Push branch**

Run: `git push -u origin feature/output-buffer-fix`

---

## Success Criteria

- ✅ `test_tell_routine_produces_output` passes
- ✅ `test_cli_look_command_shows_output` passes
- ✅ Manual test: `python3 -m zil_interpreter` shows TELL output
- ✅ Manual test: Bun UI shows game descriptions
- ✅ No new test failures introduced
- ✅ All commits follow conventional commit format

## Files Modified Summary

1. `zil_interpreter/loader/world_loader.py` - Accept OutputBuffer parameter
2. `zil_interpreter/cli/game_cli.py` - Pass buffer to loader
3. `zil_interpreter/cli/repl.py` - Update for new signature
4. `tests/test_tell_output.py` - Unit tests for TELL output
5. `tests/test_cli_tell_integration.py` - Integration tests
6. `README.md` - Documentation (optional)

## Rollback Plan

If issues arise:

```bash
git reset --hard main
git worktree remove .worktrees/output-buffer-fix
git branch -D feature/output-buffer-fix
```

Then investigate the issue before retrying.
