# CLI Quick Start Guide

Quick reference for using the ZIL Interpreter CLI module.

## Basic Usage

### Interactive Play

```bash
# Auto-detect and select game
python3 -m zil_interpreter

# Play specific game
python3 -m zil_interpreter zork1/zork1.zil
```

### Programmatic Use (JSON Mode)

```bash
# Single command
echo "look" | python3 -m zil_interpreter game.zil --json

# Multiple commands
echo -e "look\ntake lamp\ninventory" | python3 -m zil_interpreter game.zil --json
```

## Quick Examples

### Example 1: Simple Interaction

```bash
$ python3 -m zil_interpreter tests/fixtures/simple_game.zil
Loaded: simple_game.zil
Objects: 2
Routines: 3

> look
You are in a small room.

> take lamp
Taken.

> inventory
You are carrying nothing.

> quit
Goodbye!
```

### Example 2: JSON Mode

```bash
$ echo "look" | python3 -m zil_interpreter tests/fixtures/simple_game.zil --json
{"type": "init", "output": "Game loaded.", "room": "ROOM"}
{"type": "response", "command": "look", "output": "You are in a small room.\n", "is_dead": false, "is_complete": false}
```

### Example 3: Bun UI Integration

```typescript
import { spawn } from "bun";

const proc = spawn({
  cmd: ["python3", "-m", "zil_interpreter", "game.zil", "--json"],
  stdout: "pipe",
  stdin: "pipe",
});

// Read JSON responses
const reader = proc.stdout.getReader();
// ... handle JSON protocol
```

## JSON Protocol Cheat Sheet

### Message Types

| Type | Description | When Sent |
|------|-------------|-----------|
| `init` | Initial game state | At startup |
| `response` | Command result | After each command |
| `error` | Error occurred | On failure |

### Response Fields

```typescript
{
  type: "response",
  command: string,     // The command that was executed
  output: string,      // Game text output
  is_dead: boolean,    // Player died
  is_complete: boolean // Game completed
}
```

## Common Patterns

### Pattern 1: Command-Response Loop

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

# Read init
init = json.loads(proc.stdout.readline())
print(init["output"])

# Game loop
while True:
    command = input("> ")
    proc.stdin.write(f"{command}\n")
    proc.stdin.flush()

    response = json.loads(proc.stdout.readline())
    print(response["output"])

    if response["is_dead"] or response["is_complete"]:
        break
```

### Pattern 2: Non-blocking Read

```typescript
async function readJsonResponse(): Promise<any> {
  const reader = proc.stdout.getReader();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    if (value) {
      buffer += new TextDecoder().decode(value);
      const newlineIndex = buffer.indexOf("\n");

      if (newlineIndex >= 0) {
        const line = buffer.substring(0, newlineIndex);
        return JSON.parse(line);
      }
    }
  }
}
```

### Pattern 3: Testing with pytest

```python
def test_game_command():
    proc = subprocess.Popen(
        ["python3", "-m", "zil_interpreter", "game.zil", "--json"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Skip init
    proc.stdout.readline()

    # Test command
    proc.stdin.write("look\n")
    proc.stdin.flush()

    response = json.loads(proc.stdout.readline())
    assert response["type"] == "response"
    assert "room" in response["output"].lower()

    proc.terminate()
```

## Troubleshooting

### Issue: Parser Error with zork1.zil

**Problem**: `No terminal matches '"' in the current parser context`

**Cause**: The original `zork1.zil` file contains top-level string literals that the current parser doesn't support.

**Solution**: Use simplified test fixtures for now:
```bash
python3 -m zil_interpreter tests/fixtures/simple_game.zil
```

### Issue: Process Hangs

**Problem**: CLI process doesn't respond

**Causes**:
1. Not in JSON mode but trying to read JSON
2. No newline sent with command
3. Process waiting for input

**Solutions**:
- Always use `--json` flag for programmatic use
- Send `\n` after each command
- Set `bufsize=1` for line buffering

### Issue: JSON Parse Error

**Problem**: `json.JSONDecodeError`

**Causes**:
1. Reading stderr instead of stdout
2. Incomplete line read
3. Non-JSON error messages

**Solutions**:
```python
# Always read complete lines
line = proc.stdout.readline()
if line:
    try:
        response = json.loads(line)
    except json.JSONDecodeError:
        print(f"Invalid JSON: {line}")
```

## Tips and Best Practices

### 1. Always Use Line Buffering

```python
proc = subprocess.Popen(
    [...],
    text=True,
    bufsize=1  # Line buffering
)
```

### 2. Flush After Writing

```python
proc.stdin.write(f"{command}\n")
proc.stdin.flush()  # Important!
```

### 3. Handle EOF Gracefully

```python
line = proc.stdout.readline()
if not line:
    # Process terminated
    break
```

### 4. Check Death/Completion

```python
if response["is_dead"]:
    print("Game Over!")
elif response["is_complete"]:
    print("You Won!")
```

### 5. Use TypeScript Types

```typescript
interface GameEngineResponse {
  output: string;
  isDead: boolean;
  isComplete: boolean;
}
```

## Advanced Usage

### Custom Death Detection

The CLI checks for standard phrases, but you can add custom detection:

```python
def is_special_ending(output: str) -> bool:
    special_phrases = [
        "the universe explodes",
        "you transcend reality"
    ]
    return any(phrase in output.lower() for phrase in special_phrases)
```

### Transcript Recording

```python
class TranscriptRecorder:
    def __init__(self, filename):
        self.file = open(filename, 'w')

    def record(self, command, response):
        self.file.write(f"> {command}\n")
        self.file.write(f"{response['output']}\n")
        self.file.flush()
```

### Session Management

```python
class GameSession:
    def __init__(self, game_file):
        self.history = []
        self.proc = subprocess.Popen([...])

    def send_command(self, cmd):
        self.history.append(cmd)
        # Send to process...

    def save_session(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.history, f)

    def replay_session(self, filename):
        with open(filename) as f:
            commands = json.load(f)
        for cmd in commands:
            self.send_command(cmd)
```

## See Also

- [Full CLI Documentation](CLI_MODULE.md)
- [JSON Protocol Specification](CLI_MODULE.md#json-protocol)
- [Bun UI Integration](../zork-ui/README.md)
