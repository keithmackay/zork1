# Zork I Interpreter Completion Design

**Goal:** Full authentic Zork I gameplay via two-phase ZIL compiler
**Architecture:** AST Transformation (Parse → Expand → Interpret)
**Approach:** Feature-complete chunks (entire subsystems)

---

## Current State

- **74 operations** implemented and registered
- Parser handles basic ZIL syntax (forms, lists, atoms, strings)
- Runtime evaluator, world state, game objects functional
- **Missing:** Compile-time processing layer

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: COMPILE-TIME                       │
├─────────────────────────────────────────────────────────────────┤
│  ZIL Source Files (.zil)                                        │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  Multi-line     │───▶│   INSERT-FILE   │◀─── Recursive      │
│  │  String Parser  │    │   Processor     │     file loading   │
│  └─────────────────┘    └─────────────────┘                    │
│         │                       │                               │
│         ▼                       ▼                               │
│  ┌─────────────────────────────────────────┐                   │
│  │           Unified AST                   │                   │
│  │  (all files merged, forms preserved)    │                   │
│  └─────────────────────────────────────────┘                   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  Macro Registry │───▶│  Macro Expander │◀─── TELL macro     │
│  │  (DEFMAC)       │    │  (AST → AST)    │     expansion      │
│  └─────────────────┘    └─────────────────┘                    │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────┐                   │
│  │        Directive Processor              │                   │
│  │  SYNTAX, PROPDEF, CONSTANT, DIRECTIONS  │                   │
│  └─────────────────────────────────────────┘                   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────┐                   │
│  │        Compiled Game State              │                   │
│  │  • Syntax tables  • Object definitions  │                   │
│  │  • Routines       • Global values       │                   │
│  └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      PHASE 2: RUNTIME                           │
├─────────────────────────────────────────────────────────────────┤
│  Player Input                                                   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  Lexer (LEX)    │───▶│  Parser (PARSE) │◀─── SYNTAX tables  │
│  └─────────────────┘    └─────────────────┘                    │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────┐                   │
│  │        AST Evaluator                    │                   │
│  │  • Operation Registry (97+ operations)  │                   │
│  │  • Routine Executor                     │                   │
│  │  • World State                          │                   │
│  └─────────────────────────────────────────┘                   │
│         │                                                       │
│         ▼                                                       │
│  Game Output                                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Chunks

### Chunk 1: Parser Foundation (~20 tasks)

Fix grammar to handle full ZIL syntax.

**Tasks:**
- Multi-line string support in grammar
- Quoted atom syntax (`'ATOM`, `,ATOM`, `.ATOM`)
- Percent-bracket evaluation (`%<...>`)
- Hash declarations (`#DECL`)
- Property shorthand in OBJECT definitions
- TABLE/LTABLE/ITABLE literal syntax
- Segment syntax (`.X` for local, `,X` for global)

**Files:**
- `zil_interpreter/parser/grammar.py`
- `zil_interpreter/parser/ast_nodes.py`
- `tests/parser/test_grammar.py`

---

### Chunk 2: File Processing (~15 tasks)

Handle multi-file compilation.

**Tasks:**
- INSERT-FILE directive processor
- Recursive file loading with cycle detection
- Path resolution relative to main file
- Unified AST merger (9 files → single tree)
- VERSION directive handling
- Conditional inclusion support

**Files:**
- `zil_interpreter/compiler/file_processor.py` (new)
- `zil_interpreter/compiler/ast_merger.py` (new)
- `tests/compiler/test_file_processor.py`

---

### Chunk 3: Macro System (~25 tasks)

Implement compile-time macro expansion.

**Tasks:**
- DEFMAC parser and registry
- Macro parameter binding (required, optional, "ARGS")
- AST-to-AST transformation engine
- **TELL macro implementation** (critical - 1,086 uses)
- Conditional compilation (`%<COND ...>`)
- FORM evaluation at compile-time
- Nested macro expansion

**TELL Macro Expansion:**
```zil
; Input:
<TELL "The " D ,LAMP " is here." CR>

; Expands to:
<PROG ()
  <PRINT "The ">
  <PRINTD ,LAMP>
  <PRINT " is here.">
  <CRLF>>
```

**TELL Indicators:**
| Indicator | Expands To |
|-----------|------------|
| `CR/CRLF` | `<CRLF>` |
| `D obj` | `<PRINTD obj>` |
| `N num` | `<PRINTN num>` |
| `C char` | `<PRINTC char>` |
| `string` | `<PRINT "string">` |

**Files:**
- `zil_interpreter/compiler/macro_registry.py` (new)
- `zil_interpreter/compiler/macro_expander.py` (new)
- `zil_interpreter/compiler/tell_macro.py` (new)
- `tests/compiler/test_macro_expander.py`
- `tests/compiler/test_tell_macro.py`

---

### Chunk 4: Compile-Time Directives (~20 tasks)

Process ZIL directives that build game tables.

**Tasks:**
- CONSTANT definitions
- PROPDEF property definitions
- DIRECTIONS table builder
- SYNTAX table builder (269 verb patterns)
- BUZZ/SYNONYM vocabulary builder
- Global initialization (SETG at compile-time)
- OBJECT property compilation

**SYNTAX Table Structure:**
```python
@dataclass
class SyntaxEntry:
    verb: str                    # "TAKE", "PUT"
    pattern: List[str]           # ["OBJECT", "IN", "OBJECT"]
    action: str                  # "V-PUT-IN"
    preaction: Optional[str]     # "PRE-TAKE" or None
    flags: int                   # Special handling

class SyntaxTable:
    entries: Dict[str, List[SyntaxEntry]]

    def match(self, verb: str, objects: List) -> Optional[SyntaxEntry]:
        """Find matching syntax for parsed command."""
```

**Files:**
- `zil_interpreter/compiler/directive_processor.py` (new)
- `zil_interpreter/compiler/syntax_table.py` (new)
- `zil_interpreter/compiler/vocabulary.py` (new)
- `tests/compiler/test_syntax_table.py`

---

### Chunk 5: Command Parser Integration (~25 tasks)

Connect compiled tables to runtime command parsing.

**Tasks:**
- Lexer using vocabulary tables
- SYNTAX table lookup at runtime
- Parser state machine (from gparser.zil)
- PRSA/PRSO/PRSI binding
- Disambiguation handling ("Which do you mean?")
- Adjective/noun matching
- Preposition handling

**Command Flow:**
```
"put lamp in case"
    │
    ▼
Lexer: ["PUT", "LAMP", "IN", "CASE"]
    │
    ▼
Parser: verb="PUT", obj1="LAMP", prep="IN", obj2="CASE"
    │
    ▼
SyntaxTable.match("PUT", [obj, "IN", obj])
    │
    ▼
Set PRSA=V-PUT-IN, PRSO=LAMP, PRSI=CASE
    │
    ▼
Execute V-PUT-IN routine
```

**Files:**
- `zil_interpreter/runtime/command_lexer.py` (new)
- `zil_interpreter/runtime/command_parser.py` (new)
- `zil_interpreter/runtime/disambiguation.py` (new)
- `tests/runtime/test_command_parser.py`

---

### Chunk 6: Missing Operations & Polish (~30 tasks)

Complete runtime and integration.

**Missing Operations:**
- SAVE/RESTORE/RESTART game state
- VERIFY (story file verification)
- PRINC (print character)
- DIRIN/DIROUT (I/O redirection)
- SPNAME (get string property name)
- CHTYPE (change type)
- LENGTH? (length predicate)
- MAPSTOP (stop MAPF iteration)
- GASSIGNED?/ASSIGNED? (variable check)
- ERROR (error handling)

**Integration Tasks:**
- Game loop improvements
- Score/moves tracking
- Room description formatting
- Status line support
- End-to-end testing with Zork I

**Files:**
- `zil_interpreter/engine/operations/` (various)
- `zil_interpreter/runtime/game_loop.py`
- `tests/integration/test_zork1.py`

---

## Success Criteria

| Milestone | Criteria | Verification |
|-----------|----------|--------------|
| **M1: Loads** | All 9 ZIL files parse without error | `load zork1/zork1.zil` succeeds |
| **M2: Initializes** | World state populated (110 objects, 69 rooms) | Object/room counts match |
| **M3: Starts** | Opening text displays correctly | Compare to reference |
| **M4: Navigates** | Can move N/S/E/W between rooms | 10 movement tests |
| **M5: Interacts** | TAKE, DROP, OPEN, LOOK work | 20 verb tests |
| **M6: Puzzles** | Game-specific actions work | First 5 puzzles |
| **M7: Full game** | Complete Zork I start to finish | Walkthrough playable |

---

## Testing Strategy

| Chunk | Test Approach |
|-------|---------------|
| 1 (Parser) | Unit tests for each grammar fix |
| 2 (Files) | Integration test loading all 9 files |
| 3 (Macros) | TELL expansion golden tests (50+ cases) |
| 4 (Directives) | Verify 269 SYNTAX entries built |
| 5 (Commands) | Parser tests against known inputs |
| 6 (Operations) | Full integration + walkthrough |

**Reference Testing:**
- Use Frotz/Bocfel with compiled .z3 as ground truth
- Compare interpreter output to reference for same inputs
- Automated regression testing against command sequences

---

## File Structure (New)

```
zil_interpreter/
├── compiler/           # NEW: Compile-time processing
│   ├── __init__.py
│   ├── file_processor.py
│   ├── ast_merger.py
│   ├── macro_registry.py
│   ├── macro_expander.py
│   ├── tell_macro.py
│   ├── directive_processor.py
│   ├── syntax_table.py
│   └── vocabulary.py
├── runtime/            # Enhanced runtime
│   ├── command_lexer.py
│   ├── command_parser.py
│   └── disambiguation.py
└── ...
```

---

## Estimated Effort

| Chunk | Tasks | Complexity |
|-------|-------|------------|
| 1. Parser Foundation | ~20 | Medium |
| 2. File Processing | ~15 | Medium |
| 3. Macro System | ~25 | High |
| 4. Compile-Time Directives | ~20 | High |
| 5. Command Parser | ~25 | High |
| 6. Operations & Polish | ~30 | Medium |
| **Total** | **~135** | |

---

## Dependencies

```
Chunk 1 (Parser) ─────┐
                      ├──▶ Chunk 3 (Macros) ──┐
Chunk 2 (Files) ──────┘                       │
                                              ├──▶ Chunk 5 (Commands) ──▶ Chunk 6 (Polish)
                      ┌──▶ Chunk 4 (Directives)┘
Chunk 1 (Parser) ─────┘
```

Chunks 1 & 2 can run in parallel. Chunks 3 & 4 can run in parallel after 1 & 2.
