# ZIL Interpreter Design - Zork I Python CLI

**Date:** 2025-11-23
**Goal:** Build a Python CLI interpreter to run Zork I from .zil source files, with extensibility for other ZIL games.

## Requirements Summary

- **Scope**: Zork I-specific interpreter, designed to extend to other games over time
- **Execution Model**: Direct interpretation (parse ZIL → AST → interpret)
- **CLI Features**: Basic REPL with save/restore game state
- **Technology Stack**: Modern Python ecosystem (rich/textual, lark, pydantic, pytest)
- **Development Approach**: Test-Driven Development

## Architecture: Domain-Driven (Game-First)

The interpreter is organized around four core domains that mirror interactive fiction:

### 1. ZIL Parser
Converts .zil source files into Python data structures. Uses lark parsing library to handle ZIL's LISP-like syntax. Produces an AST capturing ZIL constructs: objects, routines, globals, properties, syntax definitions.

### 2. Game World Model
Represents game state: objects (with properties and flags), rooms, inventory, global variables. Built from parsed ZIL data during initialization. This is the "database" that changes as the player interacts.

### 3. Command Engine
Handles player input. Uses syntax definitions from ZIL files to parse commands like "take lamp" into structured actions (verb + direct object + indirect object). Maps English commands to ZIL verbs.

### 4. Story Engine
Executes ZIL routines (game logic). When Command Engine determines "TAKE LAMP", Story Engine runs the corresponding action routine, updates Game World Model, and generates output.

**Integration**: CLI wrapper (rich/textual) ties these together: read input → Command Engine → Story Engine → update World Model → display output → repeat.

## Module Structure

```
zil_interpreter/
├── parser/
│   ├── lexer.py          # Tokenizes ZIL source
│   ├── grammar.py        # Lark grammar for ZIL syntax
│   ├── ast_nodes.py      # Python classes for AST nodes
│   └── loader.py         # Loads and parses .zil files
├── world/
│   ├── game_object.py    # Object with properties/flags
│   ├── room.py           # Room representation
│   ├── globals.py        # Global variables manager
│   └── world_state.py    # Complete game state
├── engine/
│   ├── command_parser.py # Parses player commands using syntax
│   ├── routine_executor.py # Executes ZIL routines (ROUTINE bodies)
│   ├── verb_handlers.py  # Built-in verb implementations
│   └── evaluator.py      # Evaluates ZIL expressions
├── runtime/
│   ├── save_manager.py   # Save/restore game state
│   └── output_buffer.py  # Manages TELL output
└── cli/
    ├── repl.py           # Main REPL loop
    └── ui.py             # Rich/textual interface

tests/                    # Mirror structure with test_*.py files
```

**Design Principles:**
- **world/** - Pure data, no logic (like database models)
- **engine/** - All execution logic (routines, verbs, evaluation)
- **parser/** - Isolated, testable with ZIL snippets
- **runtime/** - Cross-session concerns (save/load, I/O)

## Data Flow

### Initialization (Game Start)
1. Parser loads all .zil files → builds complete AST
2. World State initializer walks AST → creates objects, rooms, globals
3. Command Parser loads syntax definitions → builds verb-to-action mappings
4. Story Engine registers all routines → ready to execute
5. CLI displays initial room description → enters REPL loop

### Command Execution (e.g., "take lamp")
1. **CLI** receives raw input: "take lamp"
2. **Command Parser** tokenizes and matches against syntax table → identifies VERB=TAKE, PRSO=LAMP
3. **Command Parser** resolves "lamp" → finds OBJECT(LAMP) in world state
4. **Story Engine** checks if LAMP has an ACTION routine → calls LAMP-F if exists
5. **Routine Executor** runs the routine body:
   - Evaluates `<VERB? TAKE>` → true
   - Checks conditions (lamp reachable, not already held)
   - Updates world: moves LAMP to player inventory
   - Executes `<TELL "Taken.">` → adds to output buffer
6. **Runtime** flushes output buffer → "Taken." appears in CLI
7. **REPL** waits for next command

### Save/Restore
- **Save**: Serialize world state (objects, globals, PRSA/PRSO/PRSI) to JSON
- **Restore**: Deserialize JSON → rebuild world state, resume REPL

**Critical Insight**: ZIL routines contain expressions that reference world state. Routine Executor needs an evaluator that handles ZIL constructs like `<FSET? OBJ FLAG>`, `<IN? OBJ CONTAINER>`, `<VERB? ACTION>`, etc.

## ZIL Language Support - Phased Implementation

### Phase 1: Minimum Playable (Core ZIL Constructs)
Essential features for basic gameplay:
- `<ROUTINE name (args) ...>` - Function definitions
- `<OBJECT name (props...)>` - Object declarations with IN, DESC, SYNONYM, ADJECTIVE, ACTION, FLAGS
- `<GLOBAL var value>` - Global variables
- `<INSERT-FILE "name" T>` - File inclusion
- `<TELL "text">` - Output to player
- `<VERB? action>` - Check current verb
- `<FSET? obj flag>` / `<FCLEAR obj flag>` / `<FSET obj flag>` - Flag operations
- `<EQUAL? a b>`, `<COND ...>` - Basic conditionals
- `<MOVE obj dest>` - Object movement

### Phase 2: Full Zork I Support (Extended Features)
Complete Zork I functionality:
- `<PROPDEF>`, `<CONSTANT>`, `<DIRECTIONS>` - Declarations
- Property access: `<GETP obj prop>`, `<PUTP obj prop val>`
- Container checks: `<IN? obj container>`, `<FIRST? container>`
- Parser state: PRSA, PRSO, PRSI globals
- String operations for parser
- Arithmetic and comparison operators
- `<SETG>`, `<SET>` - Variable assignment

### Phase 3: Multi-Game Support (Future)
Extensibility for other ZIL games:
- Macro system (`<DEFMAC>`) - critical for other games
- Tables and arrays
- More complex control flow
- Game-specific extensions

## Testing Strategy (TDD)

1. **Parser tests**: "does `<ROUTINE FOO ()>` parse correctly?"
2. **Integration tests**: "can we parse 1dungeon.zil?"
3. **Execution tests**: "does `<TELL 'Hello'>` produce 'Hello'?"
4. **Fixture mini-games**: tiny .zil files testing specific features
5. **End-to-end test**: "can we play through the first room of Zork I?"

Build progressively from unit tests to full game execution.

## Development Dependencies

- **lark** - Parser generation
- **rich/textual** - Modern CLI interface
- **pydantic** - Data validation for game objects
- **pytest** - Testing framework
- **pytest-cov** - Code coverage

## Success Criteria

**Minimum Viable:**
- Parse all Zork I .zil files without errors
- Execute basic commands (LOOK, TAKE, DROP, GO)
- Display room descriptions and object interactions
- Basic game loop works

**Full Feature:**
- Complete Zork I playthrough possible
- Save/restore functionality
- All verbs and puzzles work correctly
- Clean, testable, documented code

**Stretch:**
- Debug mode showing interpreter state
- Support for other Infocom games
- Performance optimization for larger games
