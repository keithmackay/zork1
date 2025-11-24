# Zork Terminal UI - Architecture

## Overview

The Zork Terminal UI is a Bun-based TypeScript application that provides an interactive terminal interface for playing Zork through a Python ZIL interpreter. The architecture follows clean separation of concerns with distinct layers for game engine integration, UI presentation, and state management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Terminal User                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   index.ts                               │
│              (ZorkTerminal Class)                        │
│  - Main orchestrator                                     │
│  - Game loop management                                  │
│  - Menu navigation                                       │
│  - Death/completion handling                             │
└─┬────────────────┬────────────────┬─────────────────────┘
  │                │                │
  ▼                ▼                ▼
┌────────────┐ ┌───────────┐ ┌──────────────┐
│   ui.ts    │ │game-      │ │save-         │
│            │ │engine.ts  │ │manager.ts    │
│ TerminalUI │ │GameEngine │ │SaveManager   │
│            │ │           │ │              │
│ - ANSI     │ │ - Python  │ │ - JSON       │
│   colors   │ │   process │ │   save files │
│ - readline │ │   spawn   │ │ - Load/list  │
│ - Prompts  │ │ - I/O     │ │   saves      │
│ - Menus    │ │   handling│ │              │
└────────────┘ └─────┬─────┘ └──────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   Python Subprocess  │
          │ (ZIL Interpreter)    │
          │                      │
          │  - Parse ZIL code    │
          │  - Execute commands  │
          │  - Game state        │
          └──────────────────────┘
```

## Core Components

### 1. ZorkTerminal (index.ts)

**Responsibilities**:
- Application lifecycle management
- Main menu and navigation
- Game loop orchestration
- State coordination between components
- Death and completion handling

**Key Methods**:
- `initialize()` - Setup save manager and UI
- `showMainMenu()` - Display and handle main menu
- `startNewGame()` - Initialize new game session
- `gameLoop()` - Main input/output loop
- `handleSave()` / `handleLoad()` - Save/load coordination
- `handleDeath()` / `handleCompletion()` - End-game scenarios

**State Management**:
```typescript
interface GameState {
  history: string[];       // All commands executed
  lastCommand: string;     // Most recent command
  timestamp: number;       // State timestamp
  gameName: string;        // Game identifier
}
```

### 2. GameEngine (game-engine.ts)

**Responsibilities**:
- Python interpreter subprocess management
- Command transmission to ZIL interpreter
- Output parsing and buffering
- Death/completion detection

**Key Methods**:
- `start()` - Spawn Python interpreter process
- `sendCommand(command)` - Send command and await response
- `readOutput()` - Non-blocking output reading
- `checkDeath(output)` / `checkCompletion(output)` - State detection
- `stop()` - Clean subprocess termination

**Process Communication**:
```typescript
// Spawn Python interpreter
spawn({
  cmd: ["python3", "-u", "-m", "zil_interpreter.cli.repl", zil_file],
  stdout: "pipe",
  stdin: "pipe",
  stderr: "pipe",
  cwd: project_root
})
```

### 3. TerminalUI (ui.ts)

**Responsibilities**:
- Terminal rendering and formatting
- User input collection
- ANSI color management
- Menus and prompts

**Key Methods**:
- `printBanner()` - Display application header
- `printOutput(text)` - Format game output
- `prompt(message)` - Get user input with readline
- `printMenu(options)` - Display numbered menus
- `confirm(message)` - Yes/no confirmation

**Color Scheme**:
- Cyan: Prompts and headers
- Green: Game output and success messages
- Yellow: Info and warnings
- Red: Errors and death messages
- Dim: Separators

### 4. SaveManager (save-manager.ts)

**Responsibilities**:
- Save file management (JSON)
- Save/load operations
- Save listing and metadata
- Filename sanitization

**Key Methods**:
- `saveGame(name, state)` - Persist game state
- `loadGame(name)` - Restore game state
- `listSaves()` - Get all saved games with metadata
- `deleteSave(name)` - Remove save file
- `sanitizeFilename(name)` - Clean save names

**Save File Format**:
```json
{
  "name": "save_name",
  "timestamp": 1234567890,
  "state": {
    "history": ["command1", "command2"],
    "lastCommand": "command2",
    "timestamp": 1234567890,
    "gameName": "zork1"
  }
}
```

### 5. Types (types.ts)

**Responsibilities**:
- TypeScript type definitions
- Interface contracts
- Type safety across components

**Key Types**:
```typescript
interface GameState {
  history: string[];
  lastCommand: string;
  timestamp: number;
  gameName: string;
}

interface SavedGame {
  name: string;
  timestamp: number;
  state: GameState;
}

interface GameEngineResponse {
  output: string;
  isDead: boolean;
  isComplete: boolean;
  error?: string;
}
```

## Data Flow

### Starting New Game
```
User → Main Menu → ZorkTerminal.startNewGame()
  → GameEngine.start() → Spawn Python process
  → Display welcome message
  → Enter gameLoop()
```

### Processing Command
```
User types command → ZorkTerminal.gameLoop()
  → GameEngine.sendCommand(command)
  → Write to Python stdin
  → Read from Python stdout
  → Check for death/completion
  → TerminalUI.printOutput(response)
  → Update GameState.history
```

### Saving Game
```
User types "save" → ZorkTerminal.handleSave()
  → TerminalUI.promptSaveName()
  → SaveManager.saveGame(name, gameState)
  → Write JSON to saves/
  → TerminalUI.printSuccess()
```

### Loading Game
```
User selects load → SaveManager.listSaves()
  → Display saves list
  → User selects save
  → SaveManager.loadGame(name)
  → GameEngine.stop() (if running)
  → GameEngine.start() (fresh process)
  → Replay all commands from history
  → Continue gameLoop()
```

### Death Handling
```
GameEngine detects death phrase
  → ZorkTerminal.handleDeath()
  → Display death menu
  → User chooses: restart / load / menu
  → Execute choice
```

## State Restoration

The save/load system uses **command replay** for state restoration:

1. **Save**: Store all commands executed (history array)
2. **Load**:
   - Start fresh Python interpreter
   - Replay each command from history
   - Game reaches exact same state
   - Continue from there

This approach ensures:
- Perfect state fidelity
- No need to serialize Python state
- Works with any ZIL interpreter
- Simple and reliable

## Error Handling

### GameEngine Errors
- Process spawn failures → Return to main menu
- Timeout on output read → Empty response
- Process crashes → Stop and restart

### SaveManager Errors
- File read/write errors → Error message to user
- Invalid JSON → Skip corrupted saves
- Directory creation → Automatic retry

### UI Errors
- Invalid menu selections → Re-prompt
- Empty commands → Silently ignore
- Interrupted input (Ctrl+C) → Graceful exit

## Performance Considerations

### Output Reading
- Non-blocking reads with timeout (200ms)
- Chunked reading to avoid blocking
- Buffer aggregation before display

### Command Processing
- 50ms delay after sending command
- Allows Python interpreter to process
- Balances responsiveness vs CPU usage

### Save/Load
- Async file operations
- JSON streaming for large saves
- Lazy loading of save list

## Security Considerations

### Filename Sanitization
```typescript
sanitizeFilename(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "_")
    .substring(0, 50);
}
```

### Path Safety
- All paths use absolute paths
- No user-controlled path traversal
- Save directory restricted

### Process Isolation
- Python subprocess sandboxed
- No shell expansion in spawn
- Clean termination on exit

## Testing Strategy

### Unit Tests (potential)
- SaveManager file operations
- Filename sanitization
- State serialization/deserialization

### Integration Tests
- test-ui.sh validates:
  - Dependencies installed
  - File structure correct
  - TypeScript compilation
  - Python interpreter accessible
  - End-to-end game launch

### Manual Testing
- New game → Play → Save → Quit → Load
- Death handling → Options work
- Menu navigation → All paths
- Edge cases (empty input, long names)

## Future Enhancements

### Potential Features
1. **Transcript Recording**: Save full game transcript as text
2. **Undo System**: Step back commands (if supported by interpreter)
3. **Hints System**: In-game hints without spoiling
4. **Map Visualization**: ASCII art map generation
5. **Statistics**: Track play time, commands, deaths
6. **Multiple Game Support**: Switch between different ZIL games
7. **Cloud Saves**: Sync saves across devices
8. **Replay Mode**: Watch saved game as "video"

### Architectural Improvements
1. **Plugin System**: Extensible UI components
2. **Event System**: Pub/sub for state changes
3. **Configuration**: User preferences file
4. **Logging**: Structured logging for debugging
5. **Testing**: Comprehensive test suite
6. **CI/CD**: Automated testing and deployment

## Dependencies

### Runtime
- **Bun**: JavaScript runtime (replaces Node.js)
- **Python 3.10+**: ZIL interpreter
- **zil_interpreter**: Python package

### Development
- **@types/node**: Node.js type definitions
- **bun-types**: Bun runtime types
- **TypeScript**: Type checking (via Bun)

## Build Process

Bun handles:
- TypeScript compilation (JIT)
- Module resolution
- Process spawning
- File system operations
- No build step required (run directly)

## Deployment

### Local Installation
```bash
cd zork-ui
bun install
./start.sh
```

### Distribution
- Package as single executable: `bun build --compile`
- Docker container with Bun + Python
- Portable archive with dependencies

---

## Design Principles

1. **Separation of Concerns**: Each component has single responsibility
2. **Type Safety**: Full TypeScript coverage
3. **Error Recovery**: Graceful degradation
4. **User Experience**: Clear prompts, helpful messages
5. **Maintainability**: Clean code, well-documented
6. **Extensibility**: Easy to add features
7. **Performance**: Responsive, no blocking operations

This architecture provides a solid foundation for a production-quality terminal UI for interactive fiction games.
