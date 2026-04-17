# Zork Tri-Game Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the Python ZIL interpreter to achieve full gameplay parity for Zork I, II, and III — every game loads, plays, and passes its acceptance playthrough.

**Architecture:** Audit all three games' ZIL files to build an operation gap list, fix the shared `g*.zil` engine once (benefits all three games), add game-specific support, then validate with unit tests, integration tests, and per-game smoke scripts. No changes to the overall pipeline; all work is additive.

**Tech Stack:** Python 3.11+, Lark (parser), Pydantic (data models), pytest + pytest-timeout (tests), bash (smoke scripts)

---

## File Map

### New files
| Path | Purpose |
|------|---------|
| `scripts/audit_zil_ops.py` | Scan all .zil files; produce gap list |
| `docs/audit/zil-operation-gap-list.md` | Output of audit — drives Phase 2/3 work |
| `zil_interpreter/engine/zil_errors.py` | `ZILRuntimeError` exception class |
| `tests/test_object_scope.py` | Regression: scope resolver uses room context |
| `tests/test_game_init.py` | Regression: no duplicate room output on start |
| `tests/test_climb_routing.py` | Regression: CLIMB routes to correct verb |
| `tests/test_error_handling.py` | ZILRuntimeError surfaces on unknown ops/routines |
| `tests/test_macro_depth.py` | Macro expansion depth guard |
| `tests/zork2/__init__.py` | Test package |
| `tests/zork2/test_zork2_loading.py` | Zork II loads without errors |
| `tests/zork2/test_zork2_commands.py` | Zork II command sequences |
| `tests/zork2/test_zork2_ops.py` | Zork II-specific operations unit tests |
| `tests/zork3/__init__.py` | Test package |
| `tests/zork3/test_zork3_loading.py` | Zork III loads without errors |
| `tests/zork3/test_zork3_commands.py` | Zork III command sequences |
| `tests/zork3/test_zork3_ops.py` | Zork III-specific operations unit tests |
| `scripts/smoke_test_zork2.sh` | Smoke test for Zork II |
| `scripts/smoke_test_zork3.sh` | Smoke test for Zork III |

### Modified files
| Path | Change |
|------|--------|
| `zil_interpreter/engine/operations/missing_ops.py` | All stubs raise `NotImplementedError` |
| `zil_interpreter/engine/operations/zork2_ops.py` | Complete NEXTP, FIXED-FONT, PUSH, RSTACK implementations |
| `zil_interpreter/engine/operations/__init__.py` | Register any new operations from audit |
| `zil_interpreter/runtime/object_resolver.py` | Fix `is_accessible()` to respect room scope |
| `zil_interpreter/loader/world_loader.py` | Fix duplicate init; set ZORK-NUMBER at load time |
| `zil_interpreter/compiler/file_processor.py` | Add max-depth guard on INSERT-FILE recursion |
| `zil_interpreter/engine/evaluator.py` | Use `ZILRuntimeError` for unknown ops/routines |
| `zil_interpreter/engine/routine_executor.py` | Use `ZILRuntimeError` for missing routines |
| `zil_interpreter/runtime/command_processor.py` | Fix CLIMB verb routing |

---

## Phase 1: Audit

### Task 1: Write ZIL operation audit script

**Files:**
- Create: `scripts/audit_zil_ops.py`

- [ ] **Step 1: Write the audit script**

```python
#!/usr/bin/env python3
"""Scan ZIL files for all operations used; compare against interpreter registry."""
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zil_interpreter.engine.operations import create_default_registry

GAME_DIRS = {
    "Zork I": Path(__file__).parent.parent / "zork1",
    "Zork II": Path(__file__).parent.parent.parent / "zork2/zork2",
    "Zork III": Path(__file__).parent.parent.parent / "zork3/zork3",
}

# Regex: match <OP_NAME ..> where OP_NAME is all-caps and may include ? - +
OP_PATTERN = re.compile(r'<([A-Z][A-Z0-9?!\-+*/=<>]+)')

def scan_dir(game_dir: Path) -> set[str]:
    ops = set()
    for zil_file in game_dir.glob("*.zil"):
        text = zil_file.read_text(errors="replace")
        ops.update(OP_PATTERN.findall(text))
    return ops

def main():
    registry = create_default_registry()
    registered = set(registry._operations.keys())

    all_used: dict[str, set[str]] = {}
    for game, path in GAME_DIRS.items():
        if not path.exists():
            print(f"WARNING: {path} not found, skipping")
            continue
        all_used[game] = scan_dir(path)

    # Union of all ops used across all games
    all_ops = set()
    for ops in all_used.values():
        all_ops.update(ops)

    # Classify each op
    rows = []
    for op in sorted(all_ops):
        games = [g for g, ops in all_used.items() if op in ops]
        if op in registered:
            status = "ok"
        else:
            status = "missing"
        rows.append((op, games, status))

    # Print markdown table
    print("| Operation | Game(s) | Status | Notes |")
    print("|-----------|---------|--------|-------|")
    for op, games, status in rows:
        game_str = ", ".join(games)
        print(f"| {op} | {game_str} | {status} | |")

    missing = [r for r in rows if r[2] == "missing"]
    print(f"\n### Summary")
    print(f"Total unique operations across all games: {len(rows)}")
    print(f"Registered in interpreter: {len(registered)}")
    print(f"Missing from interpreter: {len(missing)}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the audit and save output**

```bash
cd /Users/Keith.MacKay/Projects/zork1
python scripts/audit_zil_ops.py > docs/audit/zil-operation-gap-list.md
cat docs/audit/zil-operation-gap-list.md
```

Expected: A markdown table listing all operations with status `ok` or `missing`. Review manually and add `stubbed` / `buggy` annotations by hand for operations that are registered but broken (e.g., NEXTP returns None).

- [ ] **Step 3: Commit the audit script and initial gap list**

```bash
git add scripts/audit_zil_ops.py docs/audit/zil-operation-gap-list.md
git commit -m "feat: add ZIL operation audit script and initial gap list"
```

---

### Task 2: Inspect diff files and document findings

**Files:**
- Modify: `docs/audit/zil-operation-gap-list.md` (add diff file findings section)

- [ ] **Step 1: Inspect Zork II diff files**

```bash
head -60 ../zork2/zork2/gsyntax.diffs
head -60 ../zork2/zork2/gverbs.diffs
```

Determine: Are these TOPS-20 comparison listings (informational only) or patches that must be applied? If they show divergence from the current `g*.zil` files, document which lines differ.

- [ ] **Step 2: Inspect Zork III diff files**

```bash
head -60 ../zork3/zork3/syntax.diffs
head -60 ../zork3/zork3/verbs.diffs
```

Same determination as Step 1.

- [ ] **Step 3: Document findings in gap list**

Add a "## Diff File Analysis" section to `docs/audit/zil-operation-gap-list.md`:

```markdown
## Diff File Analysis

### Zork II
- `gsyntax.diffs`: [TOPS-20 comparison only | Patches required — see lines X-Y]
- `gverbs.diffs`: [TOPS-20 comparison only | Patches required — see lines X-Y]
- **Action required:** [None | Apply diffs in WorldLoader before processing Zork II]

### Zork III  
- `syntax.diffs`: [TOPS-20 comparison only | Patches required — see lines X-Y]
- `verbs.diffs`: [TOPS-20 comparison only | Patches required — see lines X-Y]
- **Action required:** [None | Apply diffs in WorldLoader before processing Zork III]
```

- [ ] **Step 4: Determine ZORK-NUMBER timing**

```bash
grep -n "ZORK-NUMBER" ../zork2/zork2/zork2.zil | head -10
grep -n "ZORK-NUMBER" zork1/zork1.zil | head -10
grep -n "ZORK-NUMBER" ../zork2/zork2/gmacros.zil | head -10
```

Confirm: Is `SETG ZORK-NUMBER` at the top of each root `.zil` file, before any `INSERT-FILE`? If yes, `FileProcessor.load_all()` processes it before expanding macros — timing is correct and no change needed. Document finding.

- [ ] **Step 5: Profile macro expansion hang**

```bash
cd /Users/Keith.MacKay/Projects/zork1
python -c "
import time, cProfile
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer

pr = cProfile.Profile()
pr.enable()
start = time.time()
try:
    loader = WorldLoader()
    loader.load_world(Path('zork1/zork1.zil'), OutputBuffer())
    elapsed = time.time() - start
    print(f'Loaded in {elapsed:.1f}s')
except Exception as e:
    print(f'Error: {e}')
pr.disable()
pr.print_stats(sort='cumulative', limit=20)
" 2>&1 | head -50
```

Expected: cProfile output showing which function consumes the most time. Document the top function and cumulative time. This reveals whether it's the Lark parser, macro expansion, or something else.

- [ ] **Step 6: Commit diff findings and profiling notes**

```bash
git add docs/audit/zil-operation-gap-list.md
git commit -m "docs: document diff file analysis and macro expansion profiling findings"
```

---

## Phase 2: Shared Core Fixes

> **Prerequisite:** Phase 1 complete. Run `pytest tests/ -x --timeout=30` after EACH task to confirm no regressions.

### Task 3: Add ZILRuntimeError

**Files:**
- Create: `zil_interpreter/engine/zil_errors.py`
- Modify: `zil_interpreter/engine/evaluator.py`
- Modify: `zil_interpreter/engine/routine_executor.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_error_handling.py
import pytest
from zil_interpreter.engine.zil_errors import ZILRuntimeError

def test_zil_runtime_error_has_operation_context():
    err = ZILRuntimeError("Unknown operation: FROBNICATE")
    assert "FROBNICATE" in str(err)

def test_zil_runtime_error_is_exception():
    with pytest.raises(ZILRuntimeError):
        raise ZILRuntimeError("test")
```

Run: `pytest tests/test_error_handling.py -v`
Expected: FAIL — `ZILRuntimeError` not found

- [ ] **Step 2: Create the error class**

```python
# zil_interpreter/engine/zil_errors.py
class ZILRuntimeError(Exception):
    """Raised when the ZIL evaluator encounters an unrecoverable error."""
    pass
```

- [ ] **Step 3: Run test**

Run: `pytest tests/test_error_handling.py -v`
Expected: PASS

- [ ] **Step 4: Use ZILRuntimeError in evaluator for unknown operations**

In `zil_interpreter/engine/evaluator.py`, find where unknown operations are handled (search for `# unknown` or a fallback `return None` at the end of the `evaluate()` dispatch). Replace the silent fallback with:

```python
from zil_interpreter.engine.zil_errors import ZILRuntimeError
# ... in evaluate() when op_name not in registry:
raise ZILRuntimeError(
    f"Unknown operation '{op_name}' in expression {expr!r}"
)
```

- [ ] **Step 5: Use ZILRuntimeError in routine_executor for missing routines**

In `zil_interpreter/engine/routine_executor.py`, find where a missing routine currently returns `False`. Replace with:

```python
from zil_interpreter.engine.zil_errors import ZILRuntimeError
# ... when routine_name not in self.routines:
raise ZILRuntimeError(
    f"Missing routine '{routine_name}' — not registered in world"
)
```

- [ ] **Step 6: Run full test suite**

```bash
pytest tests/ -x --timeout=30 -q
```

Expected: All existing tests pass. If any test was relying on silent `None` from unknown ops, update that test to expect `ZILRuntimeError`.

- [ ] **Step 7: Commit**

```bash
git add zil_interpreter/engine/zil_errors.py zil_interpreter/engine/evaluator.py \
        zil_interpreter/engine/routine_executor.py tests/test_error_handling.py
git commit -m "feat: add ZILRuntimeError for unknown operations and missing routines"
```

---

### Task 4: Change missing_ops stubs to raise NotImplementedError

**Files:**
- Modify: `zil_interpreter/engine/operations/missing_ops.py`

The stubs are 22 Operation subclasses in `missing_ops.py`. They currently silently return `None`, `False`, or a no-op value. Change each `execute()` to raise `NotImplementedError`.

- [ ] **Step 1: Write failing test**

```python
# Add to tests/test_error_handling.py
from zil_interpreter.engine.operations.missing_ops import (
    MapstopOperation, ChtypeOperation, StuffOperation
)
from unittest.mock import MagicMock

def test_stub_ops_raise_not_implemented():
    evaluator = MagicMock()
    for OpClass in [MapstopOperation, ChtypeOperation, StuffOperation]:
        op = OpClass()
        with pytest.raises(NotImplementedError, match=op.name):
            op.execute([], evaluator)
```

Run: `pytest tests/test_error_handling.py::test_stub_ops_raise_not_implemented -v`
Expected: FAIL — no exception raised

- [ ] **Step 2: Update every stub in missing_ops.py**

For each `execute()` method that currently no-ops, replace the body with:
```python
raise NotImplementedError(f"ZIL operation '{self.name}' is not yet implemented")
```

Operations that already have real logic (PROB, WEIGHT, THIS-IS-IT, THIS-IT?, GLOBAL-IN?, SEE-INSIDE?, ASSIGNED?, GASSIGNED?, NUMBER?, MIN, MAX, ABS) should keep their implementation. Only replace bodies that are `return None`, `return False`, `return ""`, or similar no-ops.

Operations to stub: `MAPSTOP`, `CHTYPE`, `SPNAME`, `STUFF`, `ZMEMQ`, `ZMEMQB`, `ZREST`, `LENGTH?`, `PUTREST`, `SEARCH-LIST`, `FIND-IN`.

- [ ] **Step 3: Run test**

Run: `pytest tests/test_error_handling.py -v`
Expected: PASS

- [ ] **Step 4: Run full suite**

```bash
pytest tests/ -x --timeout=30 -q
```

Expected: All existing tests pass. Any test that was relying on a no-op stub needs to be updated to expect `NotImplementedError`, or the stub needs a real implementation.

- [ ] **Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/missing_ops.py tests/test_error_handling.py
git commit -m "fix: stub operations now raise NotImplementedError instead of silently no-oping"
```

---

### Task 5: Add macro expansion depth guard

**Files:**
- Modify: `zil_interpreter/compiler/file_processor.py`
- Create (add to): `tests/test_macro_depth.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_macro_depth.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from zil_interpreter.compiler.file_processor import FileProcessor, CircularDependencyError

def test_max_depth_raises_on_deep_recursion():
    """FileProcessor should raise an error if INSERT-FILE nesting exceeds max depth."""
    processor = FileProcessor(Path("/tmp"), max_depth=3)
    # Simulate a deeply nested call stack by patching internal depth tracking
    with pytest.raises((CircularDependencyError, RecursionError, ValueError), match="depth|recursion|circular"):
        # Create a chain of 5 levels when max is 3
        processor._depth = 4  # Force depth beyond limit
        processor._check_depth()
```

Run: `pytest tests/test_macro_depth.py -v`
Expected: FAIL — `max_depth` parameter and `_check_depth` don't exist

- [ ] **Step 2: Add depth tracking to FileProcessor**

In `zil_interpreter/compiler/file_processor.py`, modify `__init__` to accept `max_depth`:

```python
def __init__(self, base_path: Path, max_depth: int = 100):
    # ... existing init code ...
    self.max_depth = max_depth
    self._depth = 0

def _check_depth(self):
    if self._depth > self.max_depth:
        raise CircularDependencyError(
            f"INSERT-FILE nesting depth {self._depth} exceeds maximum {self.max_depth}. "
            f"Possible infinite recursion in ZIL files."
        )
```

In `load_all()` (or wherever recursion happens), wrap recursive calls:
```python
self._depth += 1
self._check_depth()
try:
    result = self._recursive_load(...)
finally:
    self._depth -= 1
```

- [ ] **Step 3: Run test**

Run: `pytest tests/test_macro_depth.py -v`
Expected: PASS

- [ ] **Step 4: Run full suite**

```bash
pytest tests/ -x --timeout=30 -q
```

- [ ] **Step 5: Commit**

```bash
git add zil_interpreter/compiler/file_processor.py tests/test_macro_depth.py
git commit -m "fix: add INSERT-FILE nesting depth guard to prevent infinite recursion hang"
```

---

### Task 6: Fix macro expansion hang (root cause from Phase 1)

> **Prerequisite:** Phase 1 Task 2 Step 5 profiling output reviewed. Fill in the specific fix below based on what the profiler reveals. Common root causes:

**If the hang is in the Lark parser (grammar backtracking):**
Add `parser="lalr"` to the Lark constructor in `file_processor.py`:
```python
self._parser = Lark(ZIL_GRAMMAR, parser="lalr", ...)
```

**If the hang is in macro_expander recursion:**
Add depth limit to `MacroExpander.expand()` and raise on excess.

**If the hang is in a `REPEAT`/`AGAIN` loop during world loading:**
Add a loop iteration counter to `control.py` repeat operations.

- [ ] **Step 1: Apply the specific fix identified in Phase 1**

(Fill in based on profiler output)

- [ ] **Step 2: Verify world loads in under 5 seconds**

```bash
time python -m zil_interpreter zork1/zork1.zil --json <<< "quit"
```

Expected: Game loads and exits in < 5 seconds total.

- [ ] **Step 3: Run full suite**

```bash
pytest tests/ -x --timeout=30 -q
```

- [ ] **Step 4: Commit**

```bash
git add <changed files>
git commit -m "fix: resolve macro expansion hang — <description of root cause>"
```

---

### Task 7: Fix object scope resolver

**Files:**
- Modify: `zil_interpreter/runtime/object_resolver.py` (line 90, `is_accessible()`)
- Create: `tests/test_object_scope.py`

The bug: `is_accessible()` at line 90 does not correctly limit search to the current room, player inventory, and open containers. Objects from other rooms are reachable.

- [ ] **Step 1: Write failing test**

```python
# tests/test_object_scope.py
import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.runtime.object_resolver import ObjectResolver
from zil_interpreter.runtime.command_types import NounPhrase

def make_world():
    world = WorldState()
    return world

def test_object_in_other_room_not_accessible():
    """Objects in a different room should not be accessible to the player."""
    world = make_world()
    # Create two rooms
    room_a = world.create_object("ROOM-A")
    room_a.set_flag("ROOMBIT", True)
    room_b = world.create_object("ROOM-B")
    room_b.set_flag("ROOMBIT", True)
    # Put an object in room B
    other_obj = world.create_object("BROKEN-LAMP")
    other_obj.add_synonym("LAMP")
    world.move_object(other_obj, room_b)
    # Player is in room A
    resolver = ObjectResolver(world)
    noun = NounPhrase(noun="LAMP", adjectives=[])
    matches = resolver.find_matches(noun, current_room=room_a)
    assert len(matches) == 0, f"Expected no matches, got {matches}"

def test_object_in_current_room_is_accessible():
    """Objects in the current room should be accessible."""
    world = make_world()
    room = world.create_object("ROOM-A")
    room.set_flag("ROOMBIT", True)
    lamp = world.create_object("LAMP")
    lamp.add_synonym("LAMP")
    world.move_object(lamp, room)
    resolver = ObjectResolver(world)
    noun = NounPhrase(noun="LAMP", adjectives=[])
    matches = resolver.find_matches(noun, current_room=room)
    assert len(matches) == 1
    assert matches[0].name == "LAMP"
```

Run: `pytest tests/test_object_scope.py -v`
Expected: `test_object_in_other_room_not_accessible` FAILS (finds object in other room)

- [ ] **Step 2: Fix `is_accessible()` in object_resolver.py**

The fix: when checking accessibility, an object is accessible only if it is:
1. Directly in `current_room`
2. In the player's inventory (player is the `WINNER` global or similar)
3. In an open container that is in 1 or 2

Read the current `is_accessible()` at line 90. It likely does a broad world-wide search. Change `find_matches()` (line 56) to only iterate over children of `current_room` and the player's inventory, not all world objects:

```python
def find_matches(self, noun_phrase: NounPhrase, current_room: GameObject) -> List[GameObject]:
    candidates = []
    # Objects in current room (direct children)
    for obj in self.world.get_children(current_room):
        candidates.append(obj)
        # Contents of open containers
        if obj.has_flag("OPENBIT") or obj.has_flag("TRANSBIT"):
            candidates.extend(self.world.get_children(obj))
    # Player inventory
    player = self.world.get_global("WINNER") or self.world.get_global("PLAYER")
    if player:
        for obj in self.world.get_children(player):
            candidates.append(obj)
            if obj.has_flag("OPENBIT") or obj.has_flag("TRANSBIT"):
                candidates.extend(self.world.get_children(obj))
    # LOCAL-GLOBALS (room-scoped global objects)
    local_globals = self.world.get_object("LOCAL-GLOBALS")
    if local_globals:
        candidates.extend(self.world.get_children(local_globals))
    return [
        obj for obj in candidates
        if self._matches_noun(obj, noun_phrase.noun)
        and self._matches_adjectives(obj, noun_phrase.adjectives)
    ]
```

- [ ] **Step 3: Run test**

Run: `pytest tests/test_object_scope.py -v`
Expected: PASS

- [ ] **Step 4: Run full suite**

```bash
pytest tests/ -x --timeout=30 -q
```

- [ ] **Step 5: Commit**

```bash
git add zil_interpreter/runtime/object_resolver.py tests/test_object_scope.py
git commit -m "fix: object resolver now restricts scope to current room and player inventory"
```

---

### Task 8: Fix duplicate room description on game init

**Files:**
- Modify: `zil_interpreter/loader/world_loader.py` OR `zil_interpreter/cli/game_cli.py`
- Create: `tests/test_game_init.py`

The bug: The room description prints twice on startup. The `GO` routine calls `V-LOOK`, then `game_cli.py` also calls a look command after init.

- [ ] **Step 1: Write failing test**

```python
# tests/test_game_init.py
import pytest
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer

@pytest.mark.timeout(30)
def test_no_duplicate_room_on_init():
    """Room description should appear exactly once on game start."""
    buf = OutputBuffer()
    loader = WorldLoader()
    world, executor = loader.load_world(Path("zork1/zork1.zil"), buf)
    output = buf.get_output()
    # Count occurrences of the starting room name
    count = output.count("West of House")
    assert count == 1, f"Expected 'West of House' once, found {count} times. Output:\n{output[:500]}"
```

Run: `pytest tests/test_game_init.py -v`
Expected: FAIL — room description appears twice

- [ ] **Step 2: Find and fix the double init**

In `zil_interpreter/cli/game_cli.py`, examine `_initialize_game()` (called from `load_game()` at line 57). Check if it calls `V-LOOK` directly after `GO` already called it. If so, remove the redundant call:

```python
def _initialize_game(self):
    # Call GO to run game setup (GO calls V-LOOK internally)
    self.engine.execute_routine("GO")
    # DO NOT call V-LOOK again here — GO already printed the room
```

Alternatively, if `GO` doesn't call `V-LOOK` and the double-print is from two different code paths, identify which path runs twice and remove the duplicate.

- [ ] **Step 3: Run test**

Run: `pytest tests/test_game_init.py -v`
Expected: PASS

- [ ] **Step 4: Run full suite**

```bash
pytest tests/ -x --timeout=30 -q
```

- [ ] **Step 5: Commit**

```bash
git add zil_interpreter/cli/game_cli.py tests/test_game_init.py
git commit -m "fix: remove duplicate room description on game initialization"
```

---

### Task 9: Fix CLIMB verb routing

**Files:**
- Modify: `zil_interpreter/runtime/command_processor.py` (or wherever verb → routine mapping lives)
- Create: `tests/test_climb_routing.py`

The bug: `CLIMB` maps to non-existent `V-CLIMB`. Should route to `V-CLIMB-UP` or `V-CLIMB-DOWN` based on context.

- [ ] **Step 1: Find the verb routing table**

```bash
grep -rn "CLIMB\|V-CLIMB" zil_interpreter/ --include="*.py"
grep -n "CLIMB" zork1/gsyntax.zil
```

This reveals where the mapping is defined.

- [ ] **Step 2: Write failing test**

> **Note:** After running Step 1 greps, rewrite this test to match the actual routing mechanism found (verb table dict, gsyntax-derived mapping, etc.). The skeleton below will likely need the assertion updated.

```python
# tests/test_climb_routing.py
import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.game_engine import GameEngine

def test_climb_does_not_route_to_nonexistent_v_climb():
    """CLIMB should route to V-CLIMB-UP or V-CLIMB-DOWN, not V-CLIMB.
    
    After Step 1 grep, update this to assert on the specific routing structure
    found — e.g. a verb dict key, a syntax table entry, or the actual command
    output text. Replace the body below with the real assertion once you know
    where the mapping lives.
    """
    # Step 1 grep will reveal where to look. After that, write the real test:
    # Example (if routing is in a verb dict on GameEngine):
    #   engine = GameEngine(WorldState(), OutputBuffer())
    #   assert engine.verb_table.get("CLIMB") in ("V-CLIMB-UP", "V-CLIMB-DOWN")
    # Example (if routing produces a ZILRuntimeError for V-CLIMB):
    #   with pytest.raises(ZILRuntimeError, match="V-CLIMB-UP"):
    #       engine.execute_command("climb")  # should error on V-CLIMB, not V-CLIMB-UP
    pytest.fail("Replace this with real assertion after Step 1 grep — see comment above")
```

Run: `pytest tests/test_climb_routing.py -v`
Expected: FAIL or reveal where the mapping lives

- [ ] **Step 3: Fix the routing**

Based on the grep output from Step 1, update the verb → routine mapping so CLIMB routes to `V-CLIMB-UP` (default) with context-sensitive routing to `V-CLIMB-DOWN` when appropriate. This likely means editing a dictionary or a `gsyntax.zil`-derived table in the command processor.

- [ ] **Step 4: Run test and full suite**

```bash
pytest tests/test_climb_routing.py tests/ -x --timeout=30 -q
```

- [ ] **Step 5: Commit**

```bash
git add <changed files> tests/test_climb_routing.py
git commit -m "fix: CLIMB verb now routes to V-CLIMB-UP instead of non-existent V-CLIMB"
```

---

## Phase 3: Game-Specific Support

### Task 10: Set ZORK-NUMBER correctly at load time

**Files:**
- Modify: `zil_interpreter/loader/world_loader.py` OR `zil_interpreter/compiler/file_processor.py`

- [ ] **Step 1: Verify current behavior**

```bash
python -c "
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer
loader = WorldLoader()
world, _ = loader.load_world(Path('zork1/zork1.zil'), OutputBuffer())
print('ZORK-NUMBER:', world.get_global('ZORK-NUMBER'))
"
```

Expected for Zork I: `1`. If it returns `None` or wrong value, the global isn't being set.

- [ ] **Step 2: If broken, fix WorldLoader to set ZORK-NUMBER**

In `world_loader.py`, after loading the root file and before processing game logic, ensure the `SETG ZORK-NUMBER` directive in the root `.zil` file is processed first. The root files are:
- `zork1/zork1.zil` — `<SETG ZORK-NUMBER 1>`
- `../zork2/zork2/zork2.zil` — `<SETG ZORK-NUMBER 2>`
- `../zork3/zork3/zork3.zil` — `<SETG ZORK-NUMBER 3>`

These should be the first expressions processed by `FileProcessor.load_all()`. If they aren't being evaluated, check that `WorldLoader` processes `SETG` directives in file order.

- [ ] **Step 3: Verify for all three games**

```bash
for game in "zork1/zork1.zil" "../zork2/zork2/zork2.zil" "../zork3/zork3/zork3.zil"; do
    python -c "
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer
loader = WorldLoader()
world, _ = loader.load_world(Path('$game'), OutputBuffer())
print('Game: $game  ZORK-NUMBER:', world.get_global('ZORK-NUMBER'))
" 2>&1
done
```

Expected: 1, 2, 3 respectively.

- [ ] **Step 4: Commit**

```bash
git add zil_interpreter/loader/world_loader.py
git commit -m "fix: ZORK-NUMBER global set correctly at load time for all three games"
```

---

### Task 11: Complete Zork II operations

**Files:**
- Modify: `zil_interpreter/engine/operations/zork2_ops.py`
- Modify: `tests/engine/operations/test_zork2_ops.py`

The four stubbed/incomplete Zork II operations: `NEXTP`, `FIXED-FONT-ON`, `FIXED-FONT-OFF`, `PUSH`, `RSTACK`.

- [ ] **Step 1: Review current implementations in zork2_ops.py**

Read lines 13-129 of `zil_interpreter/engine/operations/zork2_ops.py`. Current state:
- `NextpOp` (line 13): Has logic but returns first property when given `0` — verify correctness
- `FixedFontOnOp` (line 62): Sets global `FIXED-FONT` to True — likely OK
- `FixedFontOffOp` (line 75): Sets global `FIXED-FONT` to False — likely OK
- `PushOp` (line 88): Pushes to `evaluator.stack` — verify `evaluator.stack` exists
- `RstackOp` (line 113): Pops from `evaluator.stack` — verify stack exists and handles empty

- [ ] **Step 2: Write tests for each operation**

```python
# tests/engine/operations/test_zork2_ops.py (add to existing file)
from unittest.mock import MagicMock, PropertyMock
from zil_interpreter.engine.operations.zork2_ops import (
    NextpOp, FixedFontOnOp, FixedFontOffOp, PushOp, RstackOp
)

def make_evaluator_with_object(props=None):
    ev = MagicMock()
    obj = MagicMock()
    obj.properties = props or {"DESC": "a lamp", "CAPACITY": 10}
    ev.evaluate.return_value = obj
    ev.world.get_global.return_value = None
    ev.stack = []
    return ev, obj

def test_nextp_returns_next_property():
    ev, obj = make_evaluator_with_object({"DESC": "lamp", "CAPACITY": 10})
    # When given prop name, returns next prop name
    op = NextpOp()
    # First prop from 0 should return first property name
    ev.evaluate.side_effect = [obj, 0]
    result = op.execute([MagicMock(), MagicMock()], ev)
    assert result is not None  # Should return a property name, not None

def test_push_adds_to_stack():
    ev, _ = make_evaluator_with_object()
    ev.stack = []
    ev.evaluate.return_value = 42
    PushOp().execute([MagicMock()], ev)
    assert 42 in ev.stack

def test_rstack_pops_from_stack():
    ev, _ = make_evaluator_with_object()
    ev.stack = [10, 20, 30]
    result = RstackOp().execute([], ev)
    assert result == 30
    assert ev.stack == [10, 20]

def test_rstack_empty_raises():
    ev, _ = make_evaluator_with_object()
    ev.stack = []
    with pytest.raises((IndexError, ZILRuntimeError)):
        RstackOp().execute([], ev)

def test_fixed_font_on_sets_global():
    ev = MagicMock()
    FixedFontOnOp().execute([], ev)
    ev.world.set_global.assert_called_with("FIXED-FONT", True)

def test_fixed_font_off_sets_global():
    ev = MagicMock()
    FixedFontOffOp().execute([], ev)
    ev.world.set_global.assert_called_with("FIXED-FONT", False)
```

Run: `pytest tests/engine/operations/test_zork2_ops.py -v`
Expected: Some tests FAIL

- [ ] **Step 3: Fix implementations**

For `RstackOp`: add guard for empty stack:
```python
def execute(self, args, evaluator):
    if not evaluator.stack:
        from zil_interpreter.engine.zil_errors import ZILRuntimeError
        raise ZILRuntimeError("RSTACK called on empty stack")
    return evaluator.stack.pop()
```

For `NextpOp`: verify property iteration order is consistent. ZIL `NEXTP` takes an object and a property name, returns the next property name (or False if no more). Implement correctly using `obj.properties.keys()`.

- [ ] **Step 4: Run tests and full suite**

```bash
pytest tests/engine/operations/test_zork2_ops.py tests/ -x --timeout=30 -q
```

- [ ] **Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/zork2_ops.py \
        tests/engine/operations/test_zork2_ops.py
git commit -m "fix: complete NEXTP, PUSH, RSTACK implementations for Zork II"
```

---

### Task 12: Implement audit-discovered missing operations

> **Prerequisite:** Review `docs/audit/zil-operation-gap-list.md`. For each operation with status `missing`, implement it following the pattern below. Create one commit per operation or per logical group.

For each missing operation `OP-NAME`:

- [ ] **Step A: Write failing test**

```python
# tests/engine/operations/test_<op_name_lower>.py
from zil_interpreter.engine.operations.<module> import <OpClass>
from unittest.mock import MagicMock

def test_<op_name_lower>_basic():
    ev = MagicMock()
    # Set up evaluator.evaluate return values for the operation's args
    ev.evaluate.side_effect = [<arg1>, <arg2>]
    result = <OpClass>().execute([MagicMock(), MagicMock()], ev)
    assert result == <expected>
```

- [ ] **Step B: Implement in appropriate module** (create new file under `engine/operations/` if needed, following existing patterns)

- [ ] **Step C: Register in `__init__.py`**

```python
# In create_default_registry(), add:
from zil_interpreter.engine.operations.<module> import <OpClass>
registry.register(<OpClass>())
```

- [ ] **Step D: Run test and full suite**

```bash
pytest tests/ -x --timeout=30 -q
```

- [ ] **Step E: Commit per operation or group**

```bash
git add <files>
git commit -m "feat: implement ZIL operation <OP-NAME>"
```

---

## Phase 4: Integration Tests and Smoke Scripts

### Task 13: Add Zork II integration tests

**Files:**
- Create: `tests/zork2/__init__.py`
- Create: `tests/zork2/test_zork2_loading.py`
- Create: `tests/zork2/test_zork2_commands.py`

- [ ] **Step 1: Create test package**

```bash
touch tests/zork2/__init__.py
```

- [ ] **Step 2: Write Zork II loading test**

```python
# tests/zork2/test_zork2_loading.py
import pytest
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer

ZORK2_PATH = Path(__file__).parent.parent.parent.parent / "zork2/zork2/zork2.zil"

@pytest.fixture(scope="module")
def zork2_world():
    if not ZORK2_PATH.exists():
        pytest.skip(f"Zork II not found at {ZORK2_PATH}")
    buf = OutputBuffer()
    loader = WorldLoader()
    world, executor = loader.load_world(ZORK2_PATH, buf)
    return world, executor, buf

@pytest.mark.timeout(30)
def test_zork2_loads_without_error(zork2_world):
    world, executor, buf = zork2_world
    assert world is not None

@pytest.mark.timeout(30)
def test_zork2_zork_number_is_2(zork2_world):
    world, _, _ = zork2_world
    assert world.get_global("ZORK-NUMBER") == 2

@pytest.mark.timeout(30)
def test_zork2_starts_in_inside_barrow(zork2_world):
    world, _, _ = zork2_world
    here = world.get_global("HERE")
    assert here is not None
    assert "BARROW" in here.name.upper()

@pytest.mark.timeout(30)
def test_zork2_sword_and_lantern_present(zork2_world):
    world, _, _ = zork2_world
    sword = world.get_object("SWORD")
    lantern = world.get_object("LANTERN")
    assert sword is not None
    assert lantern is not None
```

Run: `pytest tests/zork2/test_zork2_loading.py -v`
Expected: Tests pass (or skip if Zork II not found)

- [ ] **Step 3: Write Zork II command tests**

```python
# tests/zork2/test_zork2_commands.py
import pytest
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.engine.game_engine import GameEngine
from zil_interpreter.runtime.output_buffer import OutputBuffer

ZORK2_PATH = Path(__file__).parent.parent.parent.parent / "zork2/zork2/zork2.zil"

@pytest.fixture(scope="module")
def zork2_engine():
    if not ZORK2_PATH.exists():
        pytest.skip(f"Zork II not found at {ZORK2_PATH}")
    buf = OutputBuffer()
    loader = WorldLoader()
    world, executor = loader.load_world(ZORK2_PATH, buf)
    engine = GameEngine(world, buf)
    engine.executor = executor
    engine.run_go_routine()
    return engine, buf

@pytest.mark.timeout(30)
def test_zork2_take_sword(zork2_engine):
    engine, buf = zork2_engine
    buf.clear()
    engine.execute_command("take sword")
    output = buf.get_output()
    assert "Taken" in output or "sword" in output.lower()

@pytest.mark.timeout(30)
def test_zork2_take_lantern(zork2_engine):
    engine, buf = zork2_engine
    buf.clear()
    engine.execute_command("take lantern")
    output = buf.get_output()
    assert "Taken" in output or "lantern" in output.lower()

@pytest.mark.timeout(30)
def test_zork2_look_shows_barrow(zork2_engine):
    engine, buf = zork2_engine
    buf.clear()
    engine.execute_command("look")
    output = buf.get_output()
    assert "Barrow" in output or "barrow" in output
```

Run: `pytest tests/zork2/ -v`

- [ ] **Step 4: Commit**

```bash
git add tests/zork2/
git commit -m "test: add Zork II loading and command integration tests"
```

---

### Task 14: Add Zork III integration tests

**Files:**
- Create: `tests/zork3/__init__.py`
- Create: `tests/zork3/test_zork3_loading.py`
- Create: `tests/zork3/test_zork3_commands.py`

Follow the same pattern as Task 13, substituting:
- Path: `../zork3/zork3/zork3.zil`
- `ZORK-NUMBER` expected: 3
- Starting room: determined from `<SETG HERE ,<starting-room>>` in `3dungeon.zil` (search for `<SETG HERE`)
- Key objects: determined by inspecting `3dungeon.zil` starting room contents

```bash
grep -n "SETG HERE\|<ROUTINE GO" ../zork3/zork3/3dungeon.zil | head -10
```

Use the starting room and nearby objects as test assertions, following the Task 13 pattern exactly.

- [ ] **Step 1: Find Zork III start room and objects**
- [ ] **Step 2: Write loading tests** (mirror Task 13 Step 2)
- [ ] **Step 3: Write command tests** (mirror Task 13 Step 3)
- [ ] **Step 4: Run tests**

```bash
pytest tests/zork3/ -v
```

- [ ] **Step 5: Commit**

```bash
git add tests/zork3/
git commit -m "test: add Zork III loading and command integration tests"
```

---

### Task 15: Add Zork II smoke script

**Files:**
- Create: `scripts/smoke_test_zork2.sh`

Model exactly on `scripts/smoke_test.sh`. Key differences:
- Game file: `../zork2/zork2/zork2.zil` (relative to project root)
- Starting room: "Barrow" (Inside Barrow)
- Commands: `take sword`, `take lantern`, `look`, `north`, `east`, `quit`
- Assertions: game title contains "ZORK II", room contains "Barrow", inventory shows sword and lantern

- [ ] **Step 1: Write the smoke script**

```bash
#!/usr/bin/env bash
set -e
PYTHON="${PYTHON:-python3}"
GAME="../zork2/zork2/zork2.zil"
PASS=0
FAIL=0

run_check() {
    local desc="$1"
    local pattern="$2"
    local output="$3"
    if echo "$output" | grep -q "$pattern"; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc (expected '$pattern')"
        FAIL=$((FAIL + 1))
    fi
}

OUTPUT=$(printf "look\ntake sword\ntake lantern\nnorth\neast\nquit\n" \
    | "$PYTHON" -m zil_interpreter "$GAME" --json 2>&1)

run_check "Game title shows ZORK II" "ZORK II" "$OUTPUT"
run_check "Starting room is Inside Barrow" "Barrow" "$OUTPUT"
run_check "Sword can be taken" "[Tt]aken\|sword" "$OUTPUT"

echo ""
echo "Smoke test results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
```

- [ ] **Step 2: Make executable and run**

```bash
chmod +x scripts/smoke_test_zork2.sh
bash scripts/smoke_test_zork2.sh
```

Expected: All checks PASS

- [ ] **Step 3: Commit**

```bash
git add scripts/smoke_test_zork2.sh
git commit -m "test: add Zork II smoke test script"
```

---

### Task 16: Add Zork III smoke script

**Files:**
- Create: `scripts/smoke_test_zork3.sh`

Follow the same pattern as Task 15, with:
- Game file: `../zork3/zork3/zork3.zil`
- Starting room: determined from Task 14 Step 1
- Commands: `look`, navigate 2 rooms, `quit`
- Assertions: "ZORK III" in title, starting room name in output

- [ ] **Step 1: Write script** (mirror Task 15)
- [ ] **Step 2: Run it**
- [ ] **Step 3: Commit**

```bash
git add scripts/smoke_test_zork3.sh
git commit -m "test: add Zork III smoke test script"
```

---

### Task 17: Run full acceptance playthroughs

- [ ] **Step 1: Run Zork I acceptance playthrough**

```bash
printf "open mailbox\ntake leaflet\nread leaflet\nnorth\neast\nopen window\nenter house\ntake lantern\ntake knife\ninventory\nquit\n" \
    | python -m zil_interpreter zork1/zork1.zil --json 2>&1
```

Verify: All commands produce expected output. No `ZILRuntimeError` or Python tracebacks.

- [ ] **Step 2: Run Zork II acceptance playthrough**

```bash
printf "take sword\ntake lantern\nlook\nnorth\neast\nquit\n" \
    | python -m zil_interpreter ../zork2/zork2/zork2.zil --json 2>&1
```

Verify: Wizard encounter fires (I-WIZARD fires on turn 4), no errors.

- [ ] **Step 3: Run Zork III acceptance playthrough**

> **Before running:** Fill in the nav commands using the starting room and exits discovered in Task 14 Step 1. Run `grep -n "SETG HERE\|<ROOM\|TO [A-Z]" ../zork3/zork3/3dungeon.zil | head -30` to find 3 navigable rooms from the start.

```bash
# Replace <nav N> with actual direction commands from Task 14 Step 1 findings:
printf "look\n<nav 1>\n<nav 2>\n<nav 3>\nquit\n" \
    | python -m zil_interpreter ../zork3/zork3/zork3.zil --json 2>&1
```

Verify: 3 rooms navigated, daemon event fires, no errors.

- [ ] **Step 4: Fix any failures found**

For each error: use superpowers:systematic-debugging to identify root cause. Fix in the appropriate operation module. Add a regression test. Run full suite.

- [ ] **Step 5: Final full suite run**

```bash
pytest tests/ --timeout=30 -q
bash scripts/smoke_test.sh
bash scripts/smoke_test_zork2.sh
bash scripts/smoke_test_zork3.sh
```

Expected: All tests pass. All smoke scripts exit 0.

- [ ] **Step 6: Final commit and push**

```bash
git add -A
git commit -m "feat: achieve full tri-game parity for Zork I, II, and III"
git push origin main
```
