# Output Buffer Unification Design

**Date:** 2025-11-24
**Status:** Approved
**Author:** Claude (with Keith MacKay)

## Problem Statement

The TELL routine in ZIL is fully implemented and working correctly, but game output is not appearing in the CLI. Investigation revealed that multiple `OutputBuffer` instances exist:

- `WorldLoader` creates its own `OutputBuffer` and passes it to `RoutineExecutor`
- `GameCLI` creates a separate `OutputBuffer` and passes it to `GameEngine`
- TELL writes to the executor's buffer, but CLI reads from the engine's buffer (which is empty)

**Root Cause:** Multiple OutputBuffer instances mean TELL output goes to the wrong buffer.

## Design Decision

**Chosen Approach:** Single unified buffer architecture

The `OutputBuffer` should be created once by the highest-level component (GameCLI) and passed down to all child components. This ensures all components write to and read from the same buffer instance.

**Alternative Approaches Considered:**

1. **Share output buffer** - Make engine use executor's buffer (simpler but wrong ownership)
2. **Executor uses engine's buffer** - Replace executor's buffer after loading (complex rewiring)
3. **Single unified buffer** ✓ - CLI creates and passes to all components (clean architecture)

## Component Changes

### 1. WorldLoader (zil_interpreter/loader/world_loader.py)

**Change:** Accept `OutputBuffer` as parameter instead of creating one.

```python
def load_world(self, main_file: Path, output: OutputBuffer) -> Tuple[WorldState, RoutineExecutor]:
    """Load game world from ZIL files.

    Args:
        main_file: Path to main .zil file
        output: OutputBuffer instance to use for all components

    Returns:
        Tuple of (WorldState, RoutineExecutor)
    """
    ast = self.zil_loader.load_file(main_file)

    world = WorldState()
    executor = RoutineExecutor(world, output)  # Use provided buffer

    for node in ast:
        if isinstance(node, Global):
            world.set_global(node.name, self._eval_value(node.value))
        elif isinstance(node, Routine):
            executor.register_routine(node)
        elif isinstance(node, ObjectNode):
            self._create_object(world, node)

    return world, executor
```

**Impact:** Breaking API change - requires updating all callers.

### 2. GameCLI (zil_interpreter/cli/game_cli.py)

**Change:** Pass CLI's `output_buffer` to `WorldLoader`.

```python
def load_game(self) -> bool:
    """Load the game file."""
    try:
        loader = WorldLoader()
        # Pass the CLI's output buffer to the loader
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

### 3. REPL (zil_interpreter/cli/repl.py)

**Change:** Update to use new `load_world()` signature.

```python
def main() -> None:
    """Main entry point for CLI."""
    # ... existing code ...

    # Load game world
    loader = WorldLoader()
    output = OutputBuffer()  # Create output buffer first

    try:
        world, executor = loader.load_world(zil_file, output)  # Pass buffer
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

## Data Flow

**Before (Broken):**
```
GameCLI creates OutputBuffer A
  ↓
WorldLoader creates OutputBuffer B
  ↓
RoutineExecutor uses Buffer B
  ↓
TELL writes to Buffer B ← Game output goes here

GameEngine uses Buffer A
  ↓
CLI reads from Buffer A ← Empty, no output!
```

**After (Fixed):**
```
GameCLI creates OutputBuffer
  ↓
  ├─→ WorldLoader receives Buffer
  │     ↓
  │   RoutineExecutor uses Buffer
  │     ↓
  │   TELL writes to Buffer ← Game output
  │
  └─→ GameEngine uses Buffer
        ↓
      CLI reads from Buffer ← Game output appears!
```

## Testing Strategy

### Unit Test
```python
def test_tell_routine_output():
    """Test that TELL writes to output buffer correctly."""
    output = OutputBuffer()
    loader = WorldLoader()
    world, executor = loader.load_world(
        Path('tests/fixtures/simple_game.zil'),
        output
    )

    # Call V-LOOK routine which uses TELL
    executor.call_routine('V-LOOK', [])
    result = output.flush()

    assert result == "You are in a small room.\n"
    assert "You are in a small room" in result
```

### Integration Test
```python
def test_game_cli_look_command():
    """Test that 'look' command produces output in CLI."""
    cli = GameCLI(
        Path('tests/fixtures/simple_game.zil'),
        json_mode=True
    )
    assert cli.load_game()

    # Mock stdin/stdout for testing
    cli._process_command("look")

    # Verify output contains game text
    # (implementation depends on testing framework)
```

## Migration Guide

**For existing code using WorldLoader:**

```python
# OLD
loader = WorldLoader()
world, executor = loader.load_world(game_file)

# NEW
loader = WorldLoader()
output = OutputBuffer()
world, executor = loader.load_world(game_file, output)
```

## Success Criteria

1. ✅ TELL output appears in CLI when running `python3 -m zil_interpreter`
2. ✅ "look" command shows room descriptions
3. ✅ All existing tests pass
4. ✅ Both interactive REPL and JSON mode work correctly
5. ✅ No duplicate OutputBuffer instances created

## Implementation Notes

- The TELL routine itself (zil_interpreter/engine/operations/io.py) requires NO changes
- OutputBuffer class (zil_interpreter/runtime/output_buffer.py) requires NO changes
- Only the component wiring needs to be updated
- This is a simple dependency injection fix, not a fundamental architecture change

## Files Modified

1. `zil_interpreter/loader/world_loader.py` - Add output parameter
2. `zil_interpreter/cli/game_cli.py` - Pass output buffer to loader
3. `zil_interpreter/cli/repl.py` - Update for new signature
4. `tests/loader/test_integration.py` - Update test calls (if exists)

## Risks & Mitigations

**Risk:** Breaking existing code that calls `load_world()`
**Mitigation:** The only known callers are GameCLI and REPL, both updated in this change

**Risk:** Tests may fail if they don't pass OutputBuffer
**Mitigation:** Update all test files to use new signature

## Future Considerations

This change improves the architecture for potential future enhancements:
- Multiple output streams (debug, game text, errors)
- Output formatting/styling
- Output capture for testing
- Transcript recording

All of these become easier with a single, well-defined OutputBuffer instance.
