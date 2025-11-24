# ZIL Interpreter CLI Module

This document describes the Python CLI module for the ZIL interpreter, which provides both interactive and programmatic interfaces for playing ZIL games.

## Overview

The CLI module provides two modes of operation:

1. **Interactive Mode**: A human-friendly REPL for playing games
2. **JSON Mode**: A machine-readable interface for programmatic interaction (used by the Bun UI)

## Installation

The CLI is part of the `zil_interpreter` package. No additional installation is required beyond the main package dependencies.

## Usage

### Command Line Interface

```bash
# Interactive menu (auto-detects Zork games)
python3 -m zil_interpreter

# Run specific game file
python3 -m zil_interpreter path/to/game.zil

# Run with JSON output for programmatic use
python3 -m zil_interpreter path/to/game.zil --json
```

### Interactive Mode

Interactive mode provides a user-friendly interface for playing games:

```bash
$ python3 -m zil_interpreter tests/fixtures/simple_game.zil
Loaded: simple_game.zil
Objects: 2
Routines: 3

> look
You are in a small room.

> quit
Goodbye!
```

### JSON Mode

JSON mode outputs structured data for programmatic consumption:

```bash
$ echo "look" | python3 -m zil_interpreter tests/fixtures/simple_game.zil --json
{"type": "init", "output": "Game loaded.", "room": "ROOM"}
{"type": "response", "command": "look", "output": "You are in a small room.\n", "is_dead": false, "is_complete": false}
```

## JSON Protocol

### Message Types

#### 1. Init Message
Sent when the game first loads:

```json
{
  "type": "init",
  "output": "Welcome message or initial room description",
  "room": "ROOM-NAME"
}
```

#### 2. Response Message
Sent after each command:

```json
{
  "type": "response",
  "command": "look",
  "output": "Game output text",
  "is_dead": false,
  "is_complete": false
}
```

#### 3. Error Message
Sent when an error occurs:

```json
{
  "type": "error",
  "message": "Error description"
}
```

### Death and Completion Detection

The CLI automatically detects death and game completion conditions:

**Death Phrases:**
- "you are dead"
- "you have died"
- "*** you have died ***"
- "game over"
- "you're dead"

**Completion Phrases:**
- "you have won"
- "congratulations"
- "you are victorious"
- "you have completed"
- "you win"

When detected, `is_dead` or `is_complete` flags are set to `true` in the response.

## Architecture

### File Structure

```
zil_interpreter/
├── __main__.py           # Entry point for python -m zil_interpreter
└── cli/
    ├── __init__.py
    ├── game_cli.py       # Main CLI implementation
    └── repl.py           # Legacy REPL (deprecated)
```

### Key Components

#### `__main__.py`
- Entry point for module execution
- Routes to interactive menu or direct game execution
- Handles command-line arguments

#### `game_cli.py`
- `GameCLI`: Main CLI class with dual-mode support
- `interactive_menu()`: Game selection interface
- JSON/text output handling
- Death/completion detection

### GameCLI Class

```python
class GameCLI:
    def __init__(self, game_file: Path, json_mode: bool = False)
    def load_game(self) -> bool
    def run(self) -> None
    def _display_initial_state(self) -> None
    def _process_command(self, command: str) -> None
    def _check_death(self, output: str) -> bool
    def _check_completion(self, output: str) -> bool
```

## Integration with Bun UI

The Bun terminal UI uses the JSON mode for seamless integration:

### TypeScript Integration

```typescript
import { spawn, type Subprocess } from "bun";

export class GameEngine {
  private process: Subprocess | null = null;

  async start(): Promise<string> {
    this.process = spawn({
      cmd: ["python3", "-m", "zil_interpreter", gamePath, "--json"],
      stdout: "pipe",
      stdin: "pipe",
      stderr: "pipe",
    });

    const response = await this.readJsonResponse();
    return response.output || "";
  }

  async sendCommand(command: string): Promise<GameEngineResponse> {
    // Send command
    const writer = this.process.stdin.getWriter();
    await writer.write(new TextEncoder().encode(`${command}\n`));
    writer.releaseLock();

    // Read JSON response
    const response = await this.readJsonResponse();
    return {
      output: response.output || "",
      isDead: response.is_dead || false,
      isComplete: response.is_complete || false,
    };
  }
}
```

## Known Limitations

### ZIL Parser Limitations

The current ZIL parser has some limitations:

1. **Top-level string literals**: Files starting with string literals (like `zork1.zil`) are not supported
2. **Complex macros**: Some advanced ZIL macro constructs may not parse correctly
3. **File inclusion**: `<INSERT-FILE>` directives are not fully implemented

### Workarounds

For testing and development, use simplified ZIL files like `tests/fixtures/simple_game.zil` that avoid these limitations.

## Testing

### Manual Testing

```bash
# Test interactive mode
python3 -m zil_interpreter tests/fixtures/simple_game.zil

# Test JSON mode
echo -e "look\ninventory\nquit" | python3 -m zil_interpreter tests/fixtures/simple_game.zil --json
```

### Automated Testing

```python
import subprocess
import json

proc = subprocess.Popen(
    ["python3", "-m", "zil_interpreter", "game.zil", "--json"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Read init message
response = json.loads(proc.stdout.readline())
assert response["type"] == "init"

# Send command
proc.stdin.write("look\n")
proc.stdin.flush()

# Read response
response = json.loads(proc.stdout.readline())
assert response["type"] == "response"
assert response["command"] == "look"
```

## Future Enhancements

### Planned Features

1. **Save/Load Support**: Implement game state serialization
2. **Transcript Recording**: Automatic session logging
3. **Debug Mode**: Detailed execution tracing
4. **Multi-game Support**: Better handling of game selection
5. **Parser Improvements**: Support for complex ZIL constructs

### Parser Roadmap

1. Support top-level string literals
2. Implement `<INSERT-FILE>` directive
3. Add macro expansion support
4. Improve error messages and diagnostics

## Contributing

When contributing to the CLI module:

1. Maintain backward compatibility with JSON protocol
2. Add tests for new features
3. Update this documentation
4. Follow existing code style and patterns

## See Also

- [Bun UI Documentation](../zork-ui/README.md)
- [ZIL Parser Documentation](PARSER.md)
- [Game Engine Documentation](GAME_ENGINE.md)
