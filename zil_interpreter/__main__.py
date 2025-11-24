"""Main entry point for ZIL interpreter CLI."""

import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    # Check if we have a game file argument
    if len(sys.argv) > 1:
        # Run with specific game file
        from zil_interpreter.cli.game_cli import GameCLI

        game_file = Path(sys.argv[1])
        json_mode = "--json" in sys.argv

        if not game_file.exists():
            print(f"Error: Game file not found: {game_file}", file=sys.stderr)
            sys.exit(1)

        cli = GameCLI(game_file, json_mode=json_mode)
        cli.run()
    else:
        # Interactive mode - show menu
        from zil_interpreter.cli.game_cli import interactive_menu
        interactive_menu()


if __name__ == "__main__":
    main()
