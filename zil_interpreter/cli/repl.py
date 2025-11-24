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

    # TODO: Load ZIL file and initialize world
    print(f"Loading: {sys.argv[1]}")
    print("Note: File loading not yet implemented")

    world = WorldState()
    repl = REPL(world)
    repl.run()


if __name__ == "__main__":
    main()
