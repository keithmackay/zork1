"""Integration tests for Zork I macro expansion."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Routine, Form, Atom


class TestZorkMacroExpansion:
    """Integration tests for complete Zork I macro expansion."""

    @pytest.fixture
    def zork_dir(self):
        """Find the zork1 directory with ZIL files."""
        # Known path to zork1 ZIL files
        zork_path = Path("/Users/Keith.MacKay/Projects/zork1/zork1")
        if zork_path.exists() and (zork_path / "zork1.zil").exists():
            return zork_path

        # Try to find from test file location
        current = Path(__file__).parent
        while current != current.parent:
            candidate = current / "zork1"
            if candidate.exists() and (candidate / "zork1.zil").exists():
                return candidate
            current = current.parent

        pytest.skip("zork1 directory not found")

    @pytest.fixture
    def expanded_ast(self, zork_dir):
        """Load and expand all Zork I files."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        ast = processor.load_all("zork1.zil")
        return [expander.expand(node) for node in ast]

    def test_all_files_expand(self, expanded_ast):
        """All Zork I files expand without error."""
        # Should have many nodes from all files
        assert len(expanded_ast) > 100

    def test_tell_count(self, expanded_ast):
        """All TELL macros are expanded."""
        tell_count = 0
        prog_count = 0

        def count_forms(node):
            nonlocal tell_count, prog_count
            if isinstance(node, Form):
                if isinstance(node.operator, Atom):
                    if node.operator.value.upper() == "TELL":
                        tell_count += 1
                    elif node.operator.value.upper() == "PROG":
                        prog_count += 1
                for arg in node.args:
                    count_forms(arg)
            elif isinstance(node, Routine):
                for form in node.body:
                    count_forms(form)
            elif isinstance(node, list):
                for item in node:
                    count_forms(item)

        for node in expanded_ast:
            count_forms(node)

        assert tell_count == 0, f"All TELL macros should be expanded, found {tell_count}"
        assert prog_count > 500, f"Many PROG forms expected from TELL expansion, found {prog_count}"

    def test_routine_bodies_expanded(self, expanded_ast):
        """Routine bodies have macros expanded."""
        routines = [n for n in expanded_ast if isinstance(n, Routine)]
        assert len(routines) > 50, f"Expected 50+ routines, found {len(routines)}"

        macro_names = {"TELL", "VERB?", "PRSO?", "PRSI?", "ROOM?",
                       "BSET", "BCLEAR", "BSET?", "ENABLE", "DISABLE",
                       "FLAMING?", "OPENABLE?", "ABS", "PROB", "RFATAL"}

        def check_no_macros(node, routine_name):
            if isinstance(node, Form):
                if isinstance(node.operator, Atom):
                    name = node.operator.value.upper()
                    assert name not in macro_names, \
                        f"Unexpanded macro {name} in routine {routine_name}"
                for arg in node.args:
                    check_no_macros(arg, routine_name)
            elif isinstance(node, list):
                for item in node:
                    check_no_macros(item, routine_name)

        for routine in routines:
            for form in routine.body:
                check_no_macros(form, routine.name)

    def test_no_unexpanded_macros_anywhere(self, expanded_ast):
        """No macro calls remain anywhere in the AST."""
        macro_names = {"TELL", "VERB?", "PRSO?", "PRSI?", "ROOM?",
                       "BSET", "BCLEAR", "BSET?", "ENABLE", "DISABLE",
                       "FLAMING?", "OPENABLE?", "ABS", "PROB", "RFATAL"}

        def check_node(node, path=""):
            if isinstance(node, Form):
                if isinstance(node.operator, Atom):
                    name = node.operator.value.upper()
                    assert name not in macro_names, \
                        f"Unexpanded macro {name} at {path}"
                for i, arg in enumerate(node.args):
                    check_node(arg, f"{path}.args[{i}]")
            elif isinstance(node, Routine):
                for i, form in enumerate(node.body):
                    check_node(form, f"routine {node.name}.body[{i}]")
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    check_node(item, f"{path}[{i}]")

        for i, node in enumerate(expanded_ast):
            check_node(node, f"ast[{i}]")

    def test_printi_forms_created(self, expanded_ast):
        """TELL expansion creates PRINTI forms."""
        printi_count = 0

        def count_printi(node):
            nonlocal printi_count
            if isinstance(node, Form):
                if isinstance(node.operator, Atom) and node.operator.value.upper() == "PRINTI":
                    printi_count += 1
                for arg in node.args:
                    count_printi(arg)
            elif isinstance(node, Routine):
                for form in node.body:
                    count_printi(form)
            elif isinstance(node, list):
                for item in node:
                    count_printi(item)

        for node in expanded_ast:
            count_printi(node)

        # Many PRINTI forms should be created from string arguments in TELL
        assert printi_count > 200, f"Expected 200+ PRINTI forms, found {printi_count}"
