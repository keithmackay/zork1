"""Tests for game initialization — ensures no duplicate room description on start."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.engine.game_engine import GameEngine

# Path to Zork I relative to main repo root
_WORKTREE_ROOT = Path(__file__).resolve().parent.parent
if ".worktrees" in str(_WORKTREE_ROOT):
    _MAIN_REPO = _WORKTREE_ROOT.parent.parent
else:
    _MAIN_REPO = _WORKTREE_ROOT
ZORK1_PATH = _MAIN_REPO / "zork1" / "zork1.zil"


class TestGameInitNoDuplicateUnit:
    """Unit tests for _display_initial_state() — no Zork I load needed."""

    def _make_cli(self, init_output: str):
        """Build a minimal GameCLI with pre-seeded _init_output."""
        from zil_interpreter.cli.game_cli import GameCLI

        cli = GameCLI.__new__(GameCLI)
        cli.game_file = Path("dummy.zil")
        cli.json_mode = False
        cli.output_buffer = OutputBuffer()
        cli.is_running = False
        cli._init_output = init_output

        # Minimal world stub
        world = MagicMock(spec=WorldState)
        room = MagicMock()
        room.name = "West of House"
        world.get_current_room.return_value = room
        cli.world = world

        # Engine stub (execute_command should NOT be called if _init_output is set)
        engine = MagicMock(spec=GameEngine)
        cli.engine = engine

        return cli

    def test_init_output_used_directly_when_set(self, capsys):
        """When GO produces output, _display_initial_state uses it without re-running look."""
        cli = self._make_cli("West of House\nThis is the start.\n")
        cli._display_initial_state()

        # Engine.execute_command must NOT be called (no second look)
        cli.engine.execute_command.assert_not_called()

        out = capsys.readouterr().out
        assert "West of House" in out

    def test_look_fallback_when_init_output_empty(self, capsys):
        """When GO produces no output, _display_initial_state falls back to execute_command."""
        cli = self._make_cli("")
        cli.output_buffer.write("West of House (via look)\n")  # simulate look output
        cli.engine.execute_command.return_value = None

        cli._display_initial_state()

        cli.engine.execute_command.assert_called_once_with("look")

    def test_no_double_look_when_go_succeeds(self, capsys):
        """GO output must not be printed twice."""
        description = "West of House\nYou are standing in an open field.\n"
        cli = self._make_cli(description)
        cli._display_initial_state()

        out = capsys.readouterr().out
        # The description text must appear exactly once
        assert out.count("West of House") == 1


@pytest.mark.slow
@pytest.mark.timeout(120)
@pytest.mark.skipif(not ZORK1_PATH.exists(), reason="Zork I source not found")
class TestZorkNumber:
    """ZORK-NUMBER global is set correctly for each game at load time."""

    def test_zork1_zork_number(self):
        """ZORK-NUMBER should be 1 for Zork I."""
        from zil_interpreter.loader.world_loader import WorldLoader

        buf = OutputBuffer()
        loader = WorldLoader()
        world, _ = loader.load_world(ZORK1_PATH, buf)
        assert world.get_global("ZORK-NUMBER") == 1


@pytest.mark.slow
@pytest.mark.timeout(120)
@pytest.mark.skipif(not ZORK1_PATH.exists(), reason="Zork I source not found")
class TestGameInitZork1:
    """Integration test: load Zork I and check the initial room is shown exactly once."""

    def test_no_duplicate_room_on_init(self):
        """Room description should appear exactly once on game start."""
        from zil_interpreter.loader.world_loader import WorldLoader
        from zil_interpreter.cli.game_cli import GameCLI

        buf = OutputBuffer()
        loader = WorldLoader()
        world, executor = loader.load_world(ZORK1_PATH, buf)
        assert world is not None, "World failed to load"

        engine = GameEngine(world, buf)
        engine.executor = executor

        # Simulate what GameCLI._initialize_game does
        if executor and "GO" in executor.routines:
            try:
                executor.call_routine("GO", [])
            except Exception:
                pass

        init_output = buf.flush()

        # Room title should appear at most once
        count = init_output.lower().count("west of house")
        assert count <= 1, (
            f"'West of House' appeared {count} times in init output — "
            f"duplicate room description bug.\nFull output:\n{init_output}"
        )
        # And it should appear at least once (sanity check)
        assert count >= 1, (
            f"'West of House' did not appear in init output at all.\n"
            f"Full output:\n{init_output}"
        )
