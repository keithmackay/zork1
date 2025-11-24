# ZIL Interpreter

A Python interpreter for ZIL (Zork Implementation Language) built from scratch using Test-Driven Development.

## Features

- **Complete ZIL Parser**: Lexer, grammar, AST, and transformer for ZIL source files
- **Game World Model**: Objects with properties, flags, hierarchies, and synonyms
- **Expression Evaluator**: Execute ZIL expressions (TELL, MOVE, FSET, GETP, COND, etc.)
- **Routine Executor**: Run ZIL functions with arguments, local variables, and returns
- **Command Parser**: Natural language input parsing ("take lamp", "put x in y")
- **Interactive REPL**: Play games directly from the command line
- **World Loader**: Load complete game worlds from .zil source files

## Installation

```bash
# From the project root
pip install -e ".[dev]"
```

## Usage

### Playing a Game

```bash
# Run the interpreter with a ZIL file
zil path/to/game.zil

# Try the included simple game
zil tests/fixtures/simple_game.zil
```

### Example Commands

```
> look
You are in a small room.

> take lamp
Taken.

> inventory
You are carrying:
Nothing.
```

## Architecture

The interpreter uses a domain-driven architecture with four core layers:

### 1. Parser Layer (`zil_interpreter/parser/`)
- **Lexer/Grammar**: Lark-based parser for ZIL syntax
- **AST Nodes**: Typed representations of ZIL constructs
- **Transformer**: Converts parse trees to AST
- **Loader**: Loads .zil files and builds AST

### 2. World Model Layer (`zil_interpreter/world/`)
- **GameObject**: Objects with properties, flags, parent/child relationships
- **WorldState**: Complete game state manager (objects, globals, parser state)

### 3. Engine Layer (`zil_interpreter/engine/`)
- **Evaluator**: Evaluates ZIL expressions in context
- **RoutineExecutor**: Executes ZIL routines with local scope
- **CommandParser**: Parses player input into structured commands
- **GameEngine**: Coordinates all components

### 4. Runtime Layer (`zil_interpreter/runtime/`, `zil_interpreter/cli/`)
- **OutputBuffer**: Manages game text output
- **REPL**: Interactive command-line interface
- **WorldLoader**: Builds game world from AST

## Supported ZIL Features

### Data Types
- Numbers (integers and floats)
- Strings (with escape sequences)
- Atoms (identifiers/variables)
- Lists (parenthesized expressions)
- Forms (angle bracket expressions)

### Expressions
- **Arithmetic**: `+`
- **Comparison**: `EQUAL?`
- **Conditionals**: `COND`
- **Predicates**: `FSET?`, `VERB?`, `IN?`, `FIRST?`

### Operations
- **Output**: `TELL` (with CR/CRLF support)
- **Object Manipulation**: `MOVE`, `FSET`, `FCLEAR`
- **Property Access**: `GETP`, `PUTP`
- **Variables**: `SET` (local), `SETG` (global)
- **Returns**: `RTRUE`, `RFALSE`

### Routines
- Function definitions with arguments
- Local variable scope
- Early returns
- Recursive calls

### Parser
- 17+ verb synonyms (LOOK/L, TAKE/GET/PICK UP, etc.)
- Direct and indirect objects
- Preposition handling (in, on, with, etc.)
- Object resolution via synonyms

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=zil_interpreter --cov-report=html

# Run specific test file
pytest tests/engine/test_evaluator.py -v
```

### Code Quality

```bash
# Format code
black zil_interpreter tests

# Type checking
mypy zil_interpreter
```

## Test Coverage

**76 tests covering:**
- Parser: 21 tests (lexer, grammar, AST, transformer, loader)
- World: 11 tests (objects, world state)
- Engine: 26 tests (evaluator, executor, parser, engine)
- Runtime: 5 tests (output buffer)
- CLI: 5 tests (REPL)
- Loader: 1 test (integration)
- Import: 1 test (basic imports)

**100% pass rate, <1s execution time**

## Documentation

- **Architecture**: `docs/plans/2025-11-23-zil-interpreter-design.md`
- **Implementation Summary**: `docs/IMPLEMENTATION_SUMMARY.md`
- **Task Plans**: `docs/plans/*.md` (5 detailed implementation plans)

## Resources

- [Original Zork I Source Code](https://github.com/historicalsource/zork1)
- [ZIL Language Documentation](http://www.xlisp.org/zil.pdf)
- [ZILF Compiler](http://zilf.io) - User-maintained ZIL compiler

## License

See LICENSE file for details.

## Acknowledgments

Built with Claude Code using Test-Driven Development methodology.
