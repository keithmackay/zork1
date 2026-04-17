"""Integration tests for loading Zork III."""
import pytest
from pathlib import Path
from zil_interpreter.loader.world_loader import WorldLoader
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
def zork3_world():
    path = _zork3_path()
    if not path.exists():
        pytest.skip(f"Zork III not found at {path}")
    buf = OutputBuffer()
    loader = WorldLoader()
    world, executor = loader.load_world(path, buf)
    return world, executor, buf


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_loads_without_error(zork3_world):
    world, executor, buf = zork3_world
    assert world is not None
    assert executor is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_zork_number_is_3(zork3_world):
    world, _, _ = zork3_world
    zork_num = world.get_global("ZORK-NUMBER")
    assert zork_num == 3


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_endless_stair_room_exists(zork3_world):
    world, _, _ = zork3_world
    # The start room ZORK2-STAIR (DESC "Endless Stair") should exist in the world
    stair = world.get_object("ZORK2-STAIR")
    assert stair is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_lamp_present(zork3_world):
    world, _, _ = zork3_world
    lamp = world.get_object("LAMP")
    assert lamp is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_sword_present(zork3_world):
    world, _, _ = zork3_world
    sword = world.get_object("SWORD")
    assert sword is not None


@pytest.mark.slow
@pytest.mark.timeout(60)
def test_zork3_has_objects(zork3_world):
    world, _, _ = zork3_world
    assert len(world.objects) > 50
