# Zork I Interpreter - Improvement Plan
**Date:** 2026-04-15  
**Status:** Ready to implement  
**Context:** Review session — play-through testing, test suite analysis, deployment audit

---

## Summary of Findings

### Test Suite Status
- **Passes (non-integration):** 832/832 ✅
- **Fails:** `test_cli_json_mode` — uses hardcoded `python3` instead of venv Python
- **Hangs:** All 5 integration tests in `tests/integration/` that parse full zork1.zil — timeout indefinitely during macro expansion of 130+ KB ZIL files

### Play-Through Results (zork1/zork1.zil)
The game loads and runs. Key bugs observed:

| # | Severity | Bug | Observed |
|---|----------|-----|----------|
| 1 | 🔴 Critical (FIXED) | JSON mode hangs on stdin EOF | `readline()` returns `""` at EOF; `if not command: continue` loops forever |
| 2 | 🟠 High | Duplicate room description on init | GO routine runs (prints intro + room), then `_display_initial_state()` calls look again |
| 3 | 🟠 High | BROKEN-LAMP takeable from West of House | Object resolver ignores room scope — finds BROKEN-LAMP (no IN property) anywhere |
| 4 | 🟡 Medium | "climb" returns "I don't know how to climb" | Parser maps "climb" → V-CLIMB (doesn't exist); real routines are V-CLIMB-UP, V-CLIMB-FOO, V-CLIMB-ON |
| 5 | 🟡 Medium | Room displayed as "unknown" in JSON init | `_display_initial_state` reads `current_room.name` but room has no `.name` attr |
| 6 | 🟢 Low | test_cli_json_mode uses wrong Python | Uses `python3` (system, no lark) instead of venv; should use `sys.executable` |

### Performance
- Loading zork1.zil: ~2-3 seconds (250 objects, 439 routines) — acceptable but parseable
- Integration tests that parse full ZIL: hang indefinitely (no timeout guard)
- No caching of parsed AST — every run re-parses all ZIL files from scratch

### Deployment Gaps
- No Dockerfile
- No `requirements.txt` (only `pyproject.toml` — fine for development, not for quick deploys)
- No health-check / smoke-test script
- `zork-ui/` Bun app exists but unclear integration status with Python interpreter

---

## Bugs to Fix

### Bug 1: ✅ ALREADY FIXED — JSON mode EOF hang
**File:** `zil_interpreter/cli/game_cli.py:132`  
**Fix applied:** Changed `sys.stdin.readline().strip()` to check for empty line = EOF and break.

### Bug 2: Duplicate room description on init
**File:** `zil_interpreter/cli/game_cli.py:75-85` (`_initialize_game`)  
**Root cause:** `_initialize_game` calls `GO` routine (which prints the game intro + first room via TELL). Then `_display_initial_state` calls `engine.execute_command("look")` which prints the room again.  
**Fix:** Before calling `_display_initial_state`, check if the output buffer already has content from GO. If so, emit that as the init message and skip the redundant look.  
**Alternative fix:** Clear the output buffer after calling GO, then call look once for canonical init output.

```python
def _initialize_game(self) -> None:
    if self.engine.executor and "GO" in self.engine.executor.routines:
        try:
            self.engine.executor.call_routine("GO", [])
        except Exception:
            pass
    # Flush GO output — will be used in _display_initial_state
    self._go_output = self.output_buffer.flush()
    ...

def _display_initial_state(self) -> None:
    output = getattr(self, '_go_output', '') or ""
    if not output:
        # fallback: run look
        self.engine.execute_command("look")
        output = self.output_buffer.flush()
    ...
```

### Bug 3: BROKEN-LAMP takeable from wrong room
**File:** `zil_interpreter/world/world_state.py` — `find_object_by_word()`  
**Root cause:** Object resolver doesn't filter by current room scope. Objects without an `(IN ...)` property are accessible everywhere.  
**Fix:** In `find_object_by_word()`, filter candidates to only those that are:
  1. In the player's inventory (carried)
  2. In the current room
  3. In LOCAL-GLOBALS (items accessible everywhere, like boarded windows)
  Objects with no location should default to an inaccessible limbo, not be globally accessible.

### Bug 4: "climb" verb routing
**File:** `zil_interpreter/engine/command_parser.py` (VERBS dict) and `game_engine.py`  
**Root cause:** CLIMB maps to V-CLIMB which doesn't exist. Real routines are V-CLIMB-UP, V-CLIMB-DOWN, V-CLIMB-FOO, V-CLIMB-ON depending on object and syntax.  
**Fix options:**
  - Add "climb up", "climb down", "climb on" as multi-word verbs mapping to CLIMB-UP, CLIMB-DOWN, CLIMB-ON
  - Plain "climb" without object → call V-CLIMB-FOO  
  - "climb tree" (no direction word) → V-CLIMB-FOO
  - "climb up tree" → V-CLIMB-UP
  - "climb down rope" → V-CLIMB-DOWN

### Bug 5: Room name "unknown" in JSON init
**File:** `zil_interpreter/cli/game_cli.py:172`  
**Root cause:** `current_room.name if current_room and hasattr(current_room, 'name') else "unknown"` — GameObject uses `obj_name` not `name`.  
**Fix:** Use `current_room.obj_name` or whatever the correct attribute is.

### Bug 6: test_cli_json_mode uses wrong Python
**File:** `tests/test_cli_json_mode.py:15`  
**Root cause:** `["python3", "-m", "zil_interpreter", ...]` uses system Python which doesn't have lark.  
**Fix:** Use `[sys.executable, "-m", "zil_interpreter", ...]` which uses the test runner's Python.

---

## Integration Tests: Hanging Issue

**Files:** `tests/integration/test_zork_commands.py`, `test_zork_directives.py`, `test_zork_loading.py`, `test_zork_macros.py`  
**Root cause:** These tests call `file_processor.load_all("zork1.zil")` + macro expansion on 130+ KB of ZIL, which may take minutes or hang during complex macro recursion.

**Fix options:**
1. **Add pytest timeout** — `pip install pytest-timeout` and add `@pytest.mark.timeout(30)` to each test class
2. **Add `pyproject.toml` timeout** — `timeout = 30` in `[tool.pytest.ini_options]`
3. **Mock heavy fixtures** — Replace full-game loading with pre-parsed snapshots
4. **Mark as slow** — `@pytest.mark.slow` and exclude by default with `-m "not slow"`

**Recommendation:** Use pytest-timeout + mark slow tests. Add to pyproject.toml:
```toml
[tool.pytest.ini_options]
timeout = 30
markers = ["slow: marks tests as slow (deselect with '-m not slow')"]
```
And add `@pytest.mark.slow` to the 4 integration test classes that load full ZIL.

---

## Performance Improvements

### AST Caching
**Opportunity:** zork1.zil is re-parsed every run (2-3 seconds). Cache the parsed AST to disk.  
**Implementation:** 
- Serialize AST to JSON/pickle after first parse
- Cache file: `.cache/zork1_ast.pkl` (or similar)  
- Invalidate cache if any source `.zil` file is newer than cache
- Adds ~0.05s to load vs 2-3s

### Lazy Loading for Integration Tests
Currently integration tests load the full game. Could be replaced with minimal fixtures.

---

## Deployment Improvements

### 1. Add Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY zil_interpreter/ ./zil_interpreter/
COPY zork1/ ./zork1/
RUN pip install -e .
ENTRYPOINT ["python", "-m", "zil_interpreter", "zork1/zork1.zil", "--json"]
```

### 2. Add requirements.txt (for non-pyproject environments)
Derive from pyproject.toml:
```
lark>=1.1.8
pydantic>=2.5.0
rich>=13.7.0
```

### 3. Add smoke test script
`scripts/smoke_test.sh` — runs a quick play-through via JSON mode and checks output.

### 4. Fix hardcoded paths in tests
Several tests use `/Users/Keith.MacKay/Projects/zork1/zork1` — replace with `Path(__file__).parent / "../../../zork1"` relative paths.

---

## Implementation Priority

| Priority | Item | Effort |
|----------|------|--------|
| P0 | Bug 2: Duplicate init output | 30 min |
| P0 | Bug 3: Object scope in resolver | 1-2 hr |
| P0 | Bug 6: test_cli_json_mode Python path | 5 min |
| P1 | Integration test timeout/slow marks | 15 min |
| P1 | Bug 4: CLIMB verb routing | 45 min |
| P1 | Bug 5: Room name in JSON | 5 min |
| P2 | AST caching | 2 hr |
| P2 | Dockerfile | 30 min |
| P2 | requirements.txt | 5 min |
| P3 | Fix hardcoded paths in tests | 30 min |
| P3 | Smoke test script | 30 min |
