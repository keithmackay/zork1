# Zork Terminal UI - Quick Start

## Installation (One-Time Setup)

```bash
# Navigate to zork-ui directory
cd /Users/Keith.MacKay/Projects/zork1/zork-ui

# Install dependencies (if not already done)
bun install

# Verify everything works
./test-ui.sh
```

## Starting the Game

```bash
# From zork-ui directory
./start.sh

# OR
bun start

# OR
bun run src/index.ts
```

## Common Game Commands

| Command | Action |
|---------|--------|
| `north`, `n` | Move north |
| `south`, `s` | Move south |
| `east`, `e` | Move east |
| `west`, `w` | Move west |
| `look`, `l` | Look around |
| `inventory`, `i` | Check inventory |
| `take <item>` | Pick up item |
| `drop <item>` | Drop item |
| `open <object>` | Open object |
| `examine <object>` | Examine closely |
| `read <object>` | Read text |

## UI Commands (Control the Terminal Interface)

| Command | Action |
|---------|--------|
| `save` | Save current game |
| `load` | Load saved game |
| `quit` or `exit` | Return to main menu |

## Quick Play Session Example

```
> ./start.sh

Main Menu:
  1. Start New Game
  2. Load Saved Game
  3. List Saves
  4. Exit

> 1

[Game starts...]

> look
West of House
You are standing west of a white house...

> open mailbox
Opening the mailbox reveals a leaflet.

> take leaflet
Taken.

> save
Enter save name: mailbox_start
Game saved!

> north
North of House...

> quit
Are you sure? (y/n): y

[Back to main menu]
```

## File Locations

- **Application**: `/Users/Keith.MacKay/Projects/zork1/zork-ui/`
- **Saves**: `/Users/Keith.MacKay/Projects/zork1/zork-ui/saves/`
- **Source**: `/Users/Keith.MacKay/Projects/zork1/zork-ui/src/`

## Troubleshooting

### Game won't start?
```bash
# Run diagnostics
./test-ui.sh

# Check Python interpreter
python3 -m zil_interpreter.cli.repl --help

# Reinstall dependencies
bun install
```

### Save not working?
```bash
# Check saves directory exists
ls -la saves/

# Create if missing
mkdir -p saves
```

### Commands not recognized?
- Try simpler phrasing: `take lamp` not `pick up the brass lamp`
- Use two words: `<verb> <noun>`
- Check spelling

## Tips

1. **Save often** - Before risky actions
2. **Use descriptive save names** - "before_troll" not "save1"
3. **Draw a map** - Track where you've been
4. **Examine everything** - Clues are everywhere
5. **Keep multiple saves** - Different paths to explore

## Getting Help

- **Full Guide**: See `USAGE.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Technical Details**: See `README.md`

## Development Mode

```bash
# Auto-reload on code changes
bun run dev

# Run tests
./test-ui.sh

# Check TypeScript
bun build src/index.ts --outdir=./test-build
```

---

**That's it!** You're ready to explore the Great Underground Empire!

Run `./start.sh` and begin your adventure.
