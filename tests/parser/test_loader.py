import pytest
from pathlib import Path
from zil_interpreter.parser.loader import ZILLoader
from zil_interpreter.parser.ast_nodes import Global, Routine, String


def test_load_simple_file():
    """Test loading a simple ZIL file."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "simple.zil"
    loader = ZILLoader()
    ast = loader.load_file(fixture_path)

    assert len(ast) >= 2  # At least GLOBAL and ROUTINE

    # Find the global definition
    globals_found = [node for node in ast if isinstance(node, Global)]
    assert len(globals_found) == 1
    assert globals_found[0].name == "TEST-VAR"

    # Find the routine definition
    routines_found = [node for node in ast if isinstance(node, Routine)]
    assert len(routines_found) == 1
    assert routines_found[0].name == "TEST-ROUTINE"


def test_loader_handles_comments():
    """Test that loader ignores comments."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "simple.zil"
    loader = ZILLoader()
    ast = loader.load_file(fixture_path)

    # Comments should not appear in AST
    comment_nodes = [node for node in ast if isinstance(node, str) and node.startswith(';')]
    assert len(comment_nodes) == 0


def test_loader_nonexistent_file():
    """Test that loader raises error for nonexistent file."""
    loader = ZILLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_file(Path("nonexistent.zil"))
