"""Integration tests for Zork III command execution."""
import pytest
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.engine.game_engine import GameEngine
from zil_interpreter.runtime.output_buffer import OutputBuffer


def _zork3_path():
    """Resolve Zork III path from worktree location."""
    worktree_root = Path(__file__).resolve().parent.parent.parent
    if ".worktrees" in str(worktree_root):
        repo_root = worktree_root.parent.parent
    else:
        repo_root = worktree_root
    return repo_root.parent / "zork3/zork3/zork3.zil"


@pytest.fixture(scope="module")
def zork3_engine():
    path = _zork3_path()
    if not path.exists():
        pytest.skip(f"Zork III not found at {path}")
    buf = OutputBuffer()
    loader = WorldLoader()
    world, executor = loader.load_world(path, buf)
    engine = GameEngine(world, buf)
    engine.executor = executor
    return engine, buf


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_look_does_not_crash(zork3_engine):
    """Verify look command executes without raising an exception."""
    engine, buf = zork3_engine
    buf.clear()
    # Should not raise
    engine.execute_command("look")


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_inventory_does_not_crash(zork3_engine):
    """Verify inventory command executes without raising an exception."""
    engine, buf = zork3_engine
    buf.clear()
    # Should not raise
    engine.execute_command("inventory")
