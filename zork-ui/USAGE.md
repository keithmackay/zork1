# Zork Terminal UI - Usage Guide

## Quick Start

1. **Start the game**:
   ```bash
   cd zork-ui
   ./start.sh
   ```

2. **Main Menu Options**:
   - **1. Start New Game** - Begin fresh adventure
   - **2. Load Saved Game** - Continue from save
   - **3. List Saves** - View all saved games
   - **4. Exit** - Quit application

## Playing the Game

### Basic Commands

Zork understands natural language commands:

- **Movement**: `north`, `south`, `east`, `west`, `up`, `down`, `enter`, `exit`
- **Short forms**: `n`, `s`, `e`, `w`, `u`, `d`
- **Interaction**: `take lamp`, `open door`, `examine mailbox`, `read leaflet`
- **Inventory**: `inventory` or `i`
- **Look**: `look` or `l` - describe current location

### Special UI Commands

These commands control the terminal UI (not the game):

- **save** - Save current game state
- **load** - Load a saved game (shows list)
- **quit** or **exit** - Return to main menu

### Examples

```
> look
West of House
You are standing in an open field west of a white house, with a boarded
front door.
There is a small mailbox here.

> examine mailbox
The small mailbox is closed.

> open mailbox
Opening the small mailbox reveals a leaflet.

> take leaflet
Taken.

> read leaflet
Welcome to Zork!

> save
Enter save name: west_house_start
Game saved as "west_house_start"

> north
North of House
You are facing the north side of a white house. There is no door here,
and all the windows are boarded up. To the north a narrow path winds
through the trees.
```

## Save/Load System

### Saving Games

1. Type `save` during gameplay
2. Enter a descriptive name (e.g., "west_house_start", "dungeon_entrance")
3. Game state is saved instantly

### Loading Games

**During Gameplay**:
1. Type `load`
2. Select save from numbered list
3. Game state restores

**From Main Menu**:
1. Choose "Load Saved Game"
2. Select save from list
3. Continue playing

### Save File Details

- **Location**: `saves/` directory
- **Format**: JSON (human-readable)
- **Contents**: Command history, timestamp, game state
- **Naming**: Automatically sanitized (spaces → underscores)

## Death and Completion

### If You Die

You'll see options:
1. **Restart Game** - Start over
2. **Load Saved Game** - Restore from save
3. **Return to Main Menu**

### If You Complete the Game

Congratulations! Options:
1. **Start New Game** - Play again
2. **Load Different Save** - Try different path
3. **Return to Main Menu**

## Tips for Playing

### Navigation
- Draw a map as you explore
- Note which directions connect rooms
- Some areas require specific items to access

### Puzzle Solving
- Examine everything (`examine object`)
- Try different combinations
- Some puzzles have multiple solutions
- Read in-game texts carefully

### Inventory Management
- You can only carry limited items
- Some items are needed for specific puzzles
- Drop items you don't immediately need
- Come back for them later

### Save Strategy
- Save before entering new areas
- Save before attempting dangerous actions
- Use descriptive save names
- Keep multiple saves for different paths

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `look` / `l` | Describe current room |
| `inventory` / `i` | List items you're carrying |
| `north`, `south`, etc. | Move in direction |
| `take <item>` | Pick up item |
| `drop <item>` | Drop item from inventory |
| `open <object>` | Open container/door |
| `close <object>` | Close container/door |
| `examine <object>` | Look at object closely |
| `read <object>` | Read text on object |
| `turn on <object>` | Activate object |
| `turn off <object>` | Deactivate object |
| `attack <object>` | Combat action |
| `wait` | Pass time |

## Troubleshooting

### Game Not Starting
- Verify Python interpreter is available
- Check you're in the correct directory
- Run `./test-ui.sh` to diagnose issues

### Commands Not Working
- Try simpler phrasing
- Use two-word commands: `<verb> <noun>`
- Check spelling
- Use `help` if game provides it

### Save/Load Issues
- Ensure `saves/` directory exists
- Check file permissions
- Save names are automatically sanitized
- Maximum 50 characters per save name

### Performance Issues
- Close other terminal applications
- Restart the terminal UI
- Check system resources

## Advanced Features

### Command History
- Every command is saved with game state
- Loading a game replays all commands
- Restores exact game state
- Invisible to player (automatic)

### Multiple Save Slots
- Unlimited save files
- Each save independent
- Named saves (not numbered)
- Timestamp tracking

### State Restoration
When loading:
1. Fresh game engine starts
2. All previous commands replay
3. Game state exactly restored
4. Continue from where you left off

## Getting Help

### In-Game
- Many Zork commands have built-in hints
- Try `help` if available
- Experiment with different commands

### Technical Issues
- Check README.md for setup
- Run test suite: `./test-ui.sh`
- Verify dependencies installed

### Community Resources
- Original Zork documentation
- Interactive fiction guides
- Infocom game maps (spoilers!)

---

**Remember**: Zork is about exploration and experimentation. Don't be afraid to try different approaches!

Enjoy your adventure in the Great Underground Empire!
