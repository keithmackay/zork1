# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a historical source code repository for **Zork I: The Great Underground Empire** (1980), an interactive fiction game by Infocom. The code is written in **ZIL (Zork Implementation Language)**, a dialect of MDL (Muddle), which is itself a LISP variant created at MIT.

**Important Context:**
- This is **historical/archival code** from Infocom's shutdown, meant for education and research
- There is no official compiler available - only the community-maintained [ZILF](http://zilf.io) compiler
- The code represents a snapshot from Infocom's development system and may differ from production releases
- This was developed on a TOPS20 mainframe using the ZILCH compiler

## File Structure and Architecture

### Main Entry Point
- `zork1.zil` - Main compilation file that orchestrates the entire game build via `<INSERT-FILE>` directives

### Core Game Files (prefix "g" = generic/shared, "1" = Zork I specific)
- `gmacros.zil` - ZIL macro definitions (TELL, etc.) used throughout the codebase
- `gsyntax.zil` - Parser syntax definitions and command grammar
- `gparser.zil` - Text parsing engine (handles player input interpretation)
- `gverbs.zil` - Generic verb implementations (TAKE, DROP, OPEN, etc.)
- `gglobals.zil` - Global variable definitions
- `gmain.zil` - Main game loop and core routines
- `gclock.zil` - Game clock/timing system

### Zork I Specific Files
- `1dungeon.zil` - Object definitions, room descriptions, and game world structure
- `1actions.zil` - Game-specific action handlers and room functions

### Build Artifacts
- `COMPILED/zork1.z3` - Compiled Z-Machine story file (version 3)
- `zork1.zip` - Legacy compiled file (from original Infocom system)
- `parser.cmp` - Compiled parser component
- `zork1.errors` - Compilation error log
- `zork1.record` - Build record/log

## Code Architecture

### Compilation Flow
The game is built by processing `zork1.zil`, which sequentially includes:
1. Macros (gmacros.zil) - Build system for TELL and other constructs
2. Syntax (gsyntax.zil) - Command grammar definitions
3. World (1dungeon.zil) - Objects, rooms, and game state
4. Globals (gglobals.zil) - Global variables
5. Systems (gclock.zil, gmain.zil, gparser.zil, gverbs.zil)
6. Game Logic (1actions.zil) - Zork I specific handlers

### ZIL Language Patterns
- `<ROUTINE NAME (ARGS) ...>` - Function definitions
- `<OBJECT NAME (properties...)>` - Game object declarations
- `<GLOBAL VAR value>` - Global variable declarations
- `<INSERT-FILE "name" T>` - Include other source files
- `<TELL "text">` - Output text to player
- `<VERB? ACTION>` - Check current verb in parser
- `<FSET OBJ FLAG>` / `<FCLEAR OBJ FLAG>` - Set/clear object flags

### Object System
Objects use property-based architecture with flags (OPENBIT, NDESCBIT, etc.) and can have:
- DESC - Description text
- SYNONYM - Words that refer to this object
- ADJECTIVE - Descriptive words for parser
- ACTION - Function handler for interactions
- IN - Container/location

### Parser Architecture
The parser (`gparser.zil`) uses:
- Global state: PRSA (action), PRSO (direct object), PRSI (indirect object)
- Clause copying via P-CCTBL table
- Direction handling via DIRECTIONS declaration
- Syntax table matching for command interpretation

## Development Notes

**This is archival code** - modifications should preserve historical accuracy. The repository is for:
- Educational study of interactive fiction design
- Research into 1980s game development practices
- Historical preservation of Infocom's techniques

**No Active Development Environment:**
- Original ZILCH compiler is lost
- ZILF can compile with minor modifications
- Z-Machine interpreters (Frotz, etc.) can run compiled .z3 files

## File Naming Conventions
- Prefix "g" = Generic/shared across Zork trilogy
- Prefix "1" = Zork I specific
- Suffix ".zil" = ZIL source code
- Suffix ".z3" = Z-Machine v3 compiled story file
