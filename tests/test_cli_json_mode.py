"""Test CLI JSON mode for programmatic interaction."""

import json
import subprocess
from pathlib import Path


def test_cli_json_mode():
    """Test that CLI JSON mode works correctly."""
    # Use simple_game.zil test fixture
    game_file = Path(__file__).parent / "fixtures" / "simple_game.zil"

    # Start CLI in JSON mode
    proc = subprocess.Popen(
        ["python3", "-m", "zil_interpreter", str(game_file), "--json"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # Read initial state
        line = proc.stdout.readline()
        assert line, "Should receive initial output"

        response = json.loads(line)
        assert response["type"] == "init", f"Expected init, got {response['type']}"
        assert "output" in response

        # Send look command
        proc.stdin.write("look\n")
        proc.stdin.flush()

        line = proc.stdout.readline()
        response = json.loads(line)
        assert response["type"] == "response"
        assert response["command"] == "look"
        assert not response["is_dead"]
        assert not response["is_complete"]

        # Send quit command
        proc.stdin.write("quit\n")
        proc.stdin.flush()

        # Wait for process to exit
        proc.wait(timeout=5)

        print("CLI JSON mode test passed!")

    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=2)


if __name__ == "__main__":
    test_cli_json_mode()
