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


def test_routine_with_arguments():
    """Test that ROUTINE with arguments parses correctly."""
    from zil_interpreter.parser.ast_nodes import Atom
    from lark import Lark
    from zil_interpreter.parser.grammar import ZIL_GRAMMAR
    from zil_interpreter.parser.transformer import ZILTransformer

    # Create inline ZIL code with a routine that has arguments
    zil_code = '<ROUTINE FOO (X Y) <TELL "test">>'

    # Parse the code
    parser = Lark(ZIL_GRAMMAR, start='start', parser='lalr')
    transformer = ZILTransformer()
    tree = parser.parse(zil_code)
    ast = transformer.transform(tree)

    # Process through loader - wrap in list since transformer returns single Form
    loader = ZILLoader()
    processed = loader._process_top_level([ast])

    # Verify the routine was parsed correctly
    assert len(processed) == 1
    routine = processed[0]
    assert isinstance(routine, Routine)
    assert routine.name == "FOO"

    # Key assertion: args should be extracted as strings, not Atom objects
    assert isinstance(routine.args, list)
    assert len(routine.args) == 2
    assert routine.args[0] == "X"
    assert routine.args[1] == "Y"
    # Verify they are strings, not Atom objects
    assert isinstance(routine.args[0], str)
    assert isinstance(routine.args[1], str)
