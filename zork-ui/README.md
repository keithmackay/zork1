# Zork Terminal UI

A terminal-based interface for playing Zork using the ZIL interpreter.

## Features

- Interactive terminal gameplay
- Save/Load game state with custom names
- Restart or load after death/completion
- Colorized output
- Game history tracking

## Installation

1. Install Bun:
```bash
curl -fsSL https://bun.sh/install | bash
```

2. Install dependencies:
```bash
cd zork-ui
bun install
```

## Usage

### Quick Start

The easiest way to start the game:
```bash
./start.sh
```

### Alternative Methods

Using npm script:
```bash
bun start
```

Or run directly:
```bash
bun run src/index.ts
```

### Development Mode (auto-reload)

```bash
bun run dev
```

### In-Game Commands

- **Regular commands**: Type any Zork command (e.g., "look", "take lamp", "go north")
- **save**: Save current game state
- **load**: Load a saved game
- **quit/exit**: Return to main menu

### Main Menu Options

1. **Start New Game**: Begin a fresh game
2. **Load Saved Game**: Continue from a saved state
3. **List Saves**: View all saved games
4. **Exit**: Quit the application

## Saved Games

Saved games are stored in the `saves/` directory as JSON files. Each save includes:
- Game history (all commands)
- Timestamp
- Game state

## Requirements

- Bun runtime
- Python 3.10+ (for ZIL interpreter)
- ZIL interpreter installed in parent directory

## Testing the UI

Test these scenarios:
1. **Start new game** → Play for a few turns → **Save** → **Quit**
2. **Load saved game** → Verify state is restored
3. **Trigger death** → Choose restart or load
4. **Complete game** → Choose new game or load

## Troubleshooting

If the game doesn't start:
- Verify Python ZIL interpreter is installed: `python3 -m zil_interpreter.cli`
- Check that you're running from the project root
- Ensure saves/ directory exists

## Project Structure

```
zork-ui/
├── package.json          # Bun project configuration
├── tsconfig.json         # TypeScript configuration
├── src/
│   ├── index.ts          # Main entry point
│   ├── game-engine.ts    # Python interpreter interface
│   ├── ui.ts             # Terminal UI logic
│   ├── save-manager.ts   # Save/load functionality
│   └── types.ts          # TypeScript types
├── saves/                # Saved games directory
└── README.md
```

## Development

Run in watch mode (auto-reload on changes):
```bash
bun run dev
```

## Notes

- The UI uses ANSI colors for better readability
- Save files are stored as JSON for easy debugging
- Game state is restored by replaying command history
- The Python interpreter runs as a subprocess
