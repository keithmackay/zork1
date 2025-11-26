"""Tests for expanding macros in complete files."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Routine, Atom


class TestFileExpansion:
    """Tests for macro expansion across files."""

    @pytest.fixture
    def zork_dir(self):
        """Find the zork1 directory with ZIL files."""
        # Known path to zork1 ZIL files
        zork_path = Path("/Users/Keith.MacKay/Projects/zork1/zork1")
        if zork_path.exists() and (zork_path / "gclock.zil").exists():
            return zork_path

        # Try to find from test file location
        current = Path(__file__).parent
        while current != current.parent:
            # Check main repo zork1 subdirectory
            candidate = current / "zork1"
            if candidate.exists() and (candidate / "gclock.zil").exists():
                return candidate
            current = current.parent

        pytest.skip("zork1 directory not found")

    def test_expand_routine_with_tell(self, zork_dir):
        """Routine containing TELL is expanded."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        # Load and expand a file with TELL usage
        ast = processor.load_file("gclock.zil")
        expanded = [expander.expand(node) for node in ast]

        # Find routines and verify TELL is expanded
        routines = [n for n in expanded if isinstance(n, Routine)]
        assert len(routines) > 0

        # Check that no TELL forms remain at the top level of routine bodies
        for routine in routines:
            for form in routine.body:
                if isinstance(form, Form) and isinstance(form.operator, Atom):
                    # TELL should be expanded to PROG
                    assert form.operator.value.upper() != "TELL", \
                        f"Unexpanded TELL found in routine {routine.name}"

    def test_no_unexpanded_macros_in_gclock(self, zork_dir):
        """After expansion, no known macro calls remain in gclock.zil."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        ast = processor.load_file("gclock.zil")
        expanded = [expander.expand(node) for node in ast]

        macro_names = {"TELL", "VERB?", "PRSO?", "PRSI?", "ROOM?",
                       "BSET", "BCLEAR", "BSET?", "ENABLE", "DISABLE",
                       "FLAMING?", "OPENABLE?", "ABS", "PROB", "RFATAL"}

        def check_no_macros(node, path=""):
            if isinstance(node, Form):
                if isinstance(node.operator, Atom):
                    name = node.operator.value.upper()
                    assert name not in macro_names, \
                        f"Unexpanded macro {name} found at {path}"
                for i, arg in enumerate(node.args):
                    check_no_macros(arg, f"{path}.args[{i}]")
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    check_no_macros(item, f"{path}[{i}]")
            elif isinstance(node, Routine):
                for i, form in enumerate(node.body):
                    check_no_macros(form, f"routine {node.name}.body[{i}]")

        for i, node in enumerate(expanded):
            check_no_macros(node, f"top[{i}]")

    def test_no_unexpanded_macros_in_gverbs(self, zork_dir):
        """After expansion, no known macro calls remain in gverbs.zil."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        ast = processor.load_file("gverbs.zil")
        expanded = [expander.expand(node) for node in ast]

        macro_names = {"TELL", "VERB?", "PRSO?", "PRSI?", "ROOM?",
                       "BSET", "BCLEAR", "BSET?", "ENABLE", "DISABLE",
                       "FLAMING?", "OPENABLE?", "ABS", "PROB", "RFATAL"}

        def check_no_macros(node, path=""):
            if isinstance(node, Form):
                if isinstance(node.operator, Atom):
                    name = node.operator.value.upper()
                    assert name not in macro_names, \
                        f"Unexpanded macro {name} found at {path}"
                for i, arg in enumerate(node.args):
                    check_no_macros(arg, f"{path}.args[{i}]")
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    check_no_macros(item, f"{path}[{i}]")
            elif isinstance(node, Routine):
                for i, form in enumerate(node.body):
                    check_no_macros(form, f"routine {node.name}.body[{i}]")

        for i, node in enumerate(expanded):
            check_no_macros(node, f"top[{i}]")

    def test_macro_expansion_count(self, zork_dir):
        """Expansion processes significant number of macros."""
        processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)

        ast = processor.load_file("gverbs.zil")

        # Count TELL forms before expansion
        tell_count_before = 0
        def count_tells(node):
            nonlocal tell_count_before
            if isinstance(node, Form):
                if isinstance(node.operator, Atom) and node.operator.value.upper() == "TELL":
                    tell_count_before += 1
                for arg in node.args:
                    count_tells(arg)
            elif isinstance(node, list):
                for item in node:
                    count_tells(item)
            elif isinstance(node, Routine):
                for form in node.body:
                    count_tells(form)

        for node in ast:
            count_tells(node)

        # Should have found some TELL macro calls
        assert tell_count_before > 0, "Expected to find TELL macro calls before expansion"

        # After expansion, count should be 0
        expanded = [expander.expand(node) for node in ast]
        tell_count_after = 0
        def count_tells_after(node):
            nonlocal tell_count_after
            if isinstance(node, Form):
                if isinstance(node.operator, Atom) and node.operator.value.upper() == "TELL":
                    tell_count_after += 1
                for arg in node.args:
                    count_tells_after(arg)
            elif isinstance(node, list):
                for item in node:
                    count_tells_after(item)
            elif isinstance(node, Routine):
                for form in node.body:
                    count_tells_after(form)

        for node in expanded:
            count_tells_after(node)

        assert tell_count_after == 0, f"Found {tell_count_after} unexpanded TELL calls"
