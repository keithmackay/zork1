"""Integration tests for loading Zork II."""
import pytest
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer


def _zork2_path():
    """Resolve Zork II path from worktree location.

    The worktree is at <projects>/zork1/.worktrees/<branch>/
    Resolving symlinks, the test file is under <projects>/zork1/...
    So we go up to <projects>/zork1 (repo root) then up once more to <projects>.
    """
    # __file__ resolves to <projects>/zork1/.../test_zork2_loading.py
    # Go up: tests/zork2 -> tests -> worktree root -> zork1 repo root -> projects
    worktree_root = Path(__file__).resolve().parent.parent.parent
    # worktree_root may be in .worktrees/<branch> subdir; repo root is 2 levels up from there
    # or it could be the repo root directly. Check for .worktrees in path.
    if ".worktrees" in str(worktree_root):
        repo_root = worktree_root.parent.parent
    else:
        repo_root = worktree_root
    projects_dir = repo_root.parent
    return projects_dir / "zork2/zork2/zork2.zil"


@pytest.fixture(scope="module")
def zork2_world():
    path = _zork2_path()
    if not path.exists():
        pytest.skip(f"Zork II not found at {path}")
    buf = OutputBuffer()
    loader = WorldLoader()
    world, executor = loader.load_world(path, buf)
    return world, executor, buf


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork2_loads_without_error(zork2_world):
    world, executor, buf = zork2_world
    assert world is not None
    assert executor is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork2_zork_number_is_2(zork2_world):
    world, _, _ = zork2_world
    zork_num = world.get_global("ZORK-NUMBER")
    assert zork_num == 2


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork2_inside_barrow_object_exists(zork2_world):
    world, _, _ = zork2_world
    # The start room INSIDE-BARROW should exist in the world
    barrow = world.get_object("INSIDE-BARROW")
    assert barrow is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork2_sword_present(zork2_world):
    world, _, _ = zork2_world
    sword = world.get_object("SWORD")
    assert sword is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork2_lamp_present(zork2_world):
    world, _, _ = zork2_world
    # In Zork II the object is named LAMP (synonyms include LANTERN)
    lamp = world.get_object("LAMP")
    assert lamp is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork2_has_objects(zork2_world):
    world, _, _ = zork2_world
    assert len(world.objects) > 100
