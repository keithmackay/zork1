"""Enhanced CLI for ZIL interpreter with Bun UI support."""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.game_engine import GameEngine
from zil_interpreter.loader.world_loader import WorldLoader


class GameCLI:
    """Command-line interface for ZIL games."""

    def __init__(self, game_file: Path, json_mode: bool = False):
        """Initialize CLI.

        Args:
            game_file: Path to ZIL game file
            json_mode: If True, output JSON for programmatic consumption
        """
        self.game_file = game_file
        self.json_mode = json_mode
        self.world: Optional[WorldState] = None
        self.engine: Optional[GameEngine] = None
        self.output_buffer = OutputBuffer()
        self.is_running = False

    def load_game(self) -> bool:
        """Load the game file.

        Returns:
            True if successful
        """
        try:
            loader = WorldLoader()
            # Pass CLI's output buffer to loader - ensures shared instance
            self.world, executor = loader.load_world(self.game_file, self.output_buffer)

            if not self.world:
                self._error("Failed to load game world")
                return False

            # Create game engine with the SAME output buffer
            self.engine = GameEngine(self.world, self.output_buffer)
            self.engine.executor = executor

            if not self.json_mode:
                print(f"Loaded: {self.game_file.name}")
                print(f"Objects: {len(self.world.objects)}")
                print(f"Routines: {len(executor.routines)}")
                print()

            return True

        except Exception as e:
            self._error(f"Failed to load game: {e}")
            return False

    def run(self) -> None:
        """Run the CLI loop."""
        if not self.load_game():
            sys.exit(1)

        self.is_running = True

        # Display initial room
        self._display_initial_state()

        # Main loop
        while self.is_running:
            try:
                # Read command
                if not self.json_mode:
                    command = input("> ").strip()
                else:
                    command = sys.stdin.readline().strip()

                if not command:
                    continue

                # Process command
                self._process_command(command)

            except (EOFError, KeyboardInterrupt):
                if not self.json_mode:
                    print("\nGoodbye!")
                break
            except Exception as e:
                self._error(f"Unexpected error: {e}")
                if self.json_mode:
                    break

    def _display_initial_state(self) -> None:
        """Display initial game state."""
        if not self.world:
            return

        # Get initial room description
        current_room = self.world.get_current_room()
        output = ""

        # Try to execute look command to get initial game description
        # Do this even if current_room is None, as the game might have custom initialization
        try:
            result = self.engine.execute_command("look")
            output = self.output_buffer.flush()
        except Exception:
            # If look fails, try using room description if available
            if current_room and hasattr(current_room, 'description'):
                output = current_room.description

        if self.json_mode:
            self._json_output({
                "type": "init",
                "output": output if output else "Welcome! Type 'look' to begin.",
                "room": current_room.name if current_room and hasattr(current_room, 'name') else "unknown",
            })
        else:
            if output:
                print(output)
            else:
                print("Welcome! Type 'look' to begin.")
            print()

    def _process_command(self, command: str) -> None:
        """Process a user command.

        Args:
            command: User input
        """
        # Check for quit commands
        if command.lower() in ("quit", "exit", "q"):
            self.is_running = False
            if not self.json_mode:
                print("Goodbye!")
            return

        # Execute command through game engine
        try:
            self.engine.execute_command(command)
            output = self.output_buffer.flush()

            # Check for special conditions
            is_dead = self._check_death(output)
            is_complete = self._check_completion(output)

            # Output results
            if self.json_mode:
                self._json_output({
                    "type": "response",
                    "command": command,
                    "output": output,
                    "is_dead": is_dead,
                    "is_complete": is_complete,
                })
            else:
                if output:
                    print(output)

                if is_dead:
                    print("\n*** YOU HAVE DIED ***\n")
                    self.is_running = False
                elif is_complete:
                    print("\n*** CONGRATULATIONS! YOU WIN! ***\n")
                    self.is_running = False

        except Exception as e:
            self._error(f"Error executing command: {e}")

    def _check_death(self, output: str) -> bool:
        """Check if output indicates death.

        Args:
            output: Game output

        Returns:
            True if player died
        """
        death_phrases = [
            "you are dead",
            "you have died",
            "*** you have died ***",
            "game over",
            "you're dead",
        ]

        lower_output = output.lower()
        return any(phrase in lower_output for phrase in death_phrases)

    def _check_completion(self, output: str) -> bool:
        """Check if output indicates game completion.

        Args:
            output: Game output

        Returns:
            True if game is complete
        """
        completion_phrases = [
            "you have won",
            "congratulations",
            "you are victorious",
            "you have completed",
            "you win",
        ]

        lower_output = output.lower()
        return any(phrase in lower_output for phrase in completion_phrases)

    def _json_output(self, data: Dict[str, Any]) -> None:
        """Output data as JSON.

        Args:
            data: Data to output
        """
        print(json.dumps(data), flush=True)

    def _error(self, message: str) -> None:
        """Output error message.

        Args:
            message: Error message
        """
        if self.json_mode:
            self._json_output({
                "type": "error",
                "message": message,
            })
        else:
            print(f"Error: {message}", file=sys.stderr)


def interactive_menu() -> None:
    """Show interactive menu to select a game."""
    print("=" * 60)
    print("ZIL Interpreter")
    print("=" * 60)
    print()

    # Look for Zork games in current directory and parent
    zork_files = []
    base_path = Path.cwd()

    # Check for zork1.zil, zork2.zil, zork3.zil in current directory
    for zork_num in [1, 2, 3]:
        zork_path = base_path / f"zork{zork_num}" / f"zork{zork_num}.zil"
        if zork_path.exists():
            zork_files.append((f"Zork {zork_num}", zork_path))

    # Also check parent directory
    parent_path = base_path.parent
    for zork_num in [1, 2, 3]:
        zork_path = parent_path / f"zork{zork_num}" / f"zork{zork_num}.zil"
        if zork_path.exists() and (f"Zork {zork_num}", zork_path) not in zork_files:
            zork_files.append((f"Zork {zork_num}", zork_path))

    if not zork_files:
        print("No Zork game files found.")
        print("Expected location: ./zork1/zork1.zil, ./zork2/zork2.zil, etc.")
        print()
        print("Usage: python -m zil_interpreter <path-to-zil-file>")
        sys.exit(1)

    print("Available Games:")
    for i, (name, path) in enumerate(zork_files, 1):
        print(f"  {i}. {name}")
    print(f"  {len(zork_files) + 1}. Exit")
    print()

    try:
        choice = input("Select game (1-{}): ".format(len(zork_files) + 1))
        choice_num = int(choice)

        if choice_num < 1 or choice_num > len(zork_files) + 1:
            print("Invalid choice")
            sys.exit(1)

        if choice_num == len(zork_files) + 1:
            print("Goodbye!")
            sys.exit(0)

        # Launch selected game
        _, game_path = zork_files[choice_num - 1]
        print()

        cli = GameCLI(game_path, json_mode=False)
        cli.run()

    except (ValueError, EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        sys.exit(0)


def main():
    """Main entry point for direct execution."""
    if len(sys.argv) > 1:
        game_file = Path(sys.argv[1])
        json_mode = "--json" in sys.argv

        if not game_file.exists():
            print(f"Error: Game file not found: {game_file}", file=sys.stderr)
            sys.exit(1)

        cli = GameCLI(game_file, json_mode=json_mode)
        cli.run()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
