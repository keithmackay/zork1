"""REPL (Read-Eval-Print Loop) for ZIL interpreter."""

import sys
from typing import Optional
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.game_engine import GameEngine


class REPL:
    """Interactive REPL for playing ZIL games."""

    def __init__(self, world: WorldState):
        self.world = world
        self.output = OutputBuffer()
        self.engine = GameEngine(world, self.output)
        self.running = False

    def display_welcome(self) -> None:
        """Display welcome message."""
        print("=" * 60)
        print("ZIL Interpreter v0.1.0")
        print("Python interpreter for Zork Implementation Language")
        print("=" * 60)
        print()
        print("Commands: quit, exit, q - Exit the interpreter")
        print("          save <file> - Save game state")
        print("          restore <file> - Restore game state")
        print()

    def get_prompt(self) -> str:
        """Get the input prompt.

        Returns:
            Prompt string
        """
        return "> "

    def should_quit(self, command: str) -> bool:
        """Check if command is a quit command.

        Args:
            command: User input

        Returns:
            True if should quit
        """
        return command.strip().lower() in ("quit", "exit", "q")

    def run(self) -> None:
        """Run the main REPL loop."""
        self.running = True
        self.display_welcome()

        # Display initial room description if available
        current_room = self.world.get_current_room()
        if current_room and current_room.description:
            print(current_room.description)
            print()

        while self.running:
            try:
                command = input(self.get_prompt())

                if self.should_quit(command):
                    print("Goodbye!")
                    break

                # Process command (placeholder for now)
                self.process_command(command)

            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

    def process_command(self, command: str) -> None:
        """Process a user command.

        Args:
            command: User input
        """
        if not command.strip():
            return

        # Execute command through game engine
        self.engine.execute_command(command)

        # Display output
        output = self.output.flush()
        if output:
            print(output)


def main() -> None:
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage: zil <path-to-zil-file>")
        sys.exit(1)

    from pathlib import Path
    from zil_interpreter.loader.world_loader import WorldLoader

    zil_file = Path(sys.argv[1])
    if not zil_file.exists():
        print(f"Error: File not found: {zil_file}")
        sys.exit(1)

    # Create output buffer BEFORE loading world
    output = OutputBuffer()

    # Load game world with shared output buffer
    loader = WorldLoader()

    try:
        world, executor = loader.load_world(zil_file, output)
        print(f"Loaded: {zil_file}")
        print(f"Routines: {len(executor.routines)}")
        print(f"Objects: {len(world.objects)}")
        print()
    except Exception as e:
        print(f"Error loading game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Create REPL with loaded world
    repl = REPL(world)
    repl.engine.executor = executor  # Use loaded executor
    repl.output = output  # Use shared output buffer
    repl.engine.output = output  # Ensure engine uses same buffer
    repl.run()


if __name__ == "__main__":
    main()
