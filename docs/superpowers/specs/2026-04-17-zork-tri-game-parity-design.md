# ZIL Interpreter: Tri-Game Parity Design

**Date:** 2026-04-17  
**Scope:** Extend the ZIL interpreter to achieve full gameplay parity for Zork I, II, and III  
**Approach:** Audit shared core → fix once → validate all three games

---

## Goals

- The Python ZIL interpreter (reads `.zil` source directly) must fully support Zork I, II, and III
- "Full parity" means: anything that worked in the original Z-Machine interpreter works here
- Every ZIL operation used by any of the three games must be implemented and tested

### Concrete Acceptance Criteria Per Game

Full parity is met when a game passes its smoke script AND a minimum playthrough:

**Zork I:** West of House → open mailbox → take leaflet → read leaflet → go north → go east → open window → enter house → take lantern → take knife → inventory
**Zork II:** Inside Barrow → take sword → take lantern → look → go north → go east → at least one wizard encounter triggers (I-WIZARD interrupt fires)
**Zork III:** Start room → navigate at least 3 rooms → at least one daemon event fires correctly (verified via game output)

These playthroughs exercise: room navigation, object interaction, inventory, game-specific subsystems (time travel, shadow, daemons).

---

## Architecture

### Phase 1 — Audit

Parse all ZIL files for all three games and extract every operation, directive, macro, and language pattern used. Diff against the interpreter's current operation registry to produce a structured gap list.

**Inputs:**
- Zork I: `/Users/Keith.MacKay/Projects/zork1/zork1/`
- Zork II: `/Users/Keith.MacKay/Projects/zork2/zork2/`
- Zork III: `/Users/Keith.MacKay/Projects/zork3/zork3/`

**Audit output — gap list file:** `docs/audit/zil-operation-gap-list.md`

Format per entry:
```
| Operation | Game(s) | Status | Notes |
|-----------|---------|--------|-------|
| NEXTP     | Zork II | stubbed | in zork2_ops.py, returns None |
| DEMONS    | Zork III | missing | not in registry |
```

Status values: `missing`, `stubbed` (no-ops in `missing_ops.py` or `zork2_ops.py`), `buggy` (implemented but incorrect), `ok`.

The gap list drives all Phase 2/3 work. No implementation begins until the gap list is complete.

**Also resolved in Phase 1:**

*Integration test hang root cause:* Profile macro expansion during `WorldLoader` initialization to identify whether the hang is infinite recursion, pathological backtracking in the Lark grammar, or a depth-unbounded loop. The root cause must be identified and fixed before Phase 4 integration tests are written. The 30s `pytest-timeout` is a safety net only — it does not substitute for fixing the hang.

*Zork II diff files:* `../zork2/zork2/` contains `gsyntax.diffs`, `gverbs.diffs`, and `.zap` files alongside the standard `.zil` files. Audit must determine: are these patches applied on top of the shared `g*.zil` files, or are they independent artifacts? If Zork II applies patches to shared files, `WorldLoader` must apply them before processing. This must be resolved before Phase 2 shared-core fixes begin, since it determines whether "fix the shared file once" is valid or whether Zork II requires a modified copy.

*`ZORK-NUMBER` timing:* Determine at which layer `ZORK-NUMBER` is set: during `FileProcessor` expansion (compile time), during `WorldLoader` initialization, or during engine `GO` routine execution. If `ZORK-NUMBER`-gated conditionals appear in `gmacros.zil` or other files processed at expansion time, the value must be available before macro expansion runs. Document the correct insertion point.

*Zork III alternative core files (resolved):* `zork3.zil` only includes the standard `g*.zil` files plus `3DUNGEON` and `3ACTIONS`. The non-prefixed alternates (`macros.zil`, `main.zil`, `parser.zil`, `syntax.zil`, `verbs.zil`) and `.zap` files are build artifacts from an alternate compilation path and are NOT part of the load chain. No `WorldLoader` changes needed for file inclusion. Similarly, `shadow.zil` and `tm.zil` are NOT referenced by `INSERT-FILE` in `zork3.zil` — shadow mechanic logic lives inline in `3actions.zil`. These files are not Phase 3 targets.

*Zork III diff files:* `../zork3/zork3/` contains `syntax.diffs` and `verbs.diffs`. As with the Zork II diff files, Phase 1 must determine whether these are patches applied to the shared `g*.zil` files. If so, `WorldLoader` must apply them before processing Zork III.

### Phase 2 — Shared Core Fixes

Fix bugs and add missing features in the shared `g*.zil` systems. Prerequisite: Phase 1 audit complete, Zork II diff file question resolved.

After each individual bug fix, run the full Zork I test suite (`pytest tests/ -x --timeout=30`) before proceeding. All 240+ existing tests must remain green throughout Phase 2.

**Known bugs to fix:**
- Object scope resolver ignores room context (finds objects anywhere in world)
- Duplicate room description on game init (GO routine runs twice)
- CLIMB verb routes to non-existent `V-CLIMB` instead of `V-CLIMB-UP`/`V-CLIMB-DOWN`
- Macro expansion hang: fix root cause identified in Phase 1
- `missing_ops.py` stubs silently no-op → change all stubs to raise `NotImplementedError` with operation name

**Error handling improvements:**
- Unknown operations → `ZILRuntimeError` with operation name, file, expression context
- Missing routines → `ZILRuntimeError` (not silent `False`)
- Type mismatches → explicit error instead of Python exception bleedthrough
- `INSERT-FILE` for unknown targets → descriptive error with filename + referencing game file
- Macro expansion depth → configurable max (default 100) with clear error message

### Phase 3 — Game-Specific Support

**`ZORK-NUMBER` global:**
- Set at the layer identified in Phase 1 audit
- All ZIL conditionals that branch on `ZORK-NUMBER` must evaluate correctly for each game

**Zork II:**
- Apply `gsyntax.diffs`/`gverbs.diffs` to loader if Phase 1 determines they are patches (see Phase 1)
- Implement `crufty.zil` content (characterize during audit)
- Complete Zork II operations currently stubbed in `zork2_ops.py`: `NEXTP`, `FIXED-FONT-ON/OFF`, `PUSH`, `RSTACK`

**Zork III:**
- Apply `syntax.diffs`/`verbs.diffs` to loader if Phase 1 determines they are patches (see Phase 1)
- `demons.zil` is NOT in the load chain — daemon logic lives in `3actions.zil`; implement required daemon/interrupt operations identified in the gap list
- Any additional operations in gap list with status `missing` or `stubbed`

### Phase 4 — Test Suite

Three-tier strategy:

**Tier 1 — Unit tests**
- Every fixed bug gets a focused pytest test (no full ZIL file loading; <1s)
- Every new/completed operation gets a unit test
- All `NotImplementedError` stubs get a test confirming they raise on call

**Tier 2 — Per-game integration tests**
- Load full ZIL for each game, execute a command sequence
- All integration tests guarded with `@pytest.mark.timeout(30)`
- Macro expansion hang fixed in Phase 1; timeout is the safety net only
- New test directories: `tests/zork2/`, `tests/zork3/`

**Tier 3 — Smoke scripts**
- One shell script per game, modeled exactly on `scripts/smoke_test.sh`
- Validation method: shell `grep` on JSON mode output, exit 0 on all checks pass, exit 1 on any failure
- Each script: load game in `--json` mode, send 8-10 commands, grep for expected strings
- Coverage: start room render, navigation, object interaction, inventory, one game-specific feature
- New scripts: `scripts/smoke_test_zork2.sh`, `scripts/smoke_test_zork3.sh`

**Test file additions:**
```
tests/
  test_object_scope.py       # Scope bug regression
  test_game_init.py          # No duplicate output on init
  test_climb_routing.py      # CLIMB verb routing
  test_error_handling.py     # ZILRuntimeError surfacing
  test_macro_depth.py        # Macro expansion depth guard
  zork2/
    test_zork2_loading.py
    test_zork2_commands.py
    test_zork2_ops.py
  zork3/
    test_zork3_loading.py
    test_zork3_commands.py
    test_zork3_ops.py
docs/
  audit/
    zil-operation-gap-list.md  # Output of Phase 1 audit
scripts/
  smoke_test_zork2.sh
  smoke_test_zork3.sh
```

**Coverage target:** Every ZIL operation used in any of the three games has at least one unit test. Every game passes its smoke script and minimum playthrough end-to-end.

---

## Data Flow

```
.zil files (per game)
    → WorldLoader (file_processor + macro_expander)
         ↑ ZORK-NUMBER set here (timing confirmed in Phase 1)
         ↑ Zork II diffs applied here if needed (confirmed in Phase 1)
    → AST (parser + transformer)
    → WorldState (objects, globals, routines)
    → GameEngine.execute_command(player_input)
        → CommandLexer → CommandParser → CommandProcessor
        → RoutineExecutor → Evaluator → Operations
        → WorldState mutations
    → output string
```

No changes to the overall pipeline structure. Work is additive: new/fixed operations, better error surfacing, loader correctness for Zork II/III files.

---

## Key Constraints

- Python ZIL interpreter is the product — no ZILF compilation, no Z-Machine backend
- `WorldLoader` already accepts arbitrary root `.zil` path — loading Zork II/III is architecturally supported today
- All existing Zork I tests must remain green after every Phase 2 change (run after each bug fix)
- New code follows existing patterns (pydantic models, operation registry, pytest fixtures)
- Smoke scripts follow `scripts/smoke_test.sh` as the model (shell + grep + exit codes)
