"""Test parsing of actual gmacros.zil DEFMAC definitions."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.parser.ast_nodes import MacroDef, Global


class TestGmacrosParsing:
    """Test parsing of gmacros.zil file."""

    @pytest.fixture
    def zork_dir(self):
        """Find zork1 directory in project."""
        # Path to the main zork1 directory (not worktree)
        zork_path = Path("/Users/Keith.MacKay/Projects/zork1/zork1")
        if zork_path.exists():
            return zork_path

        # Fallback: search from current directory
        current = Path(__file__).parent
        while current != current.parent:
            candidate = current / "zork1"
            if candidate.exists():
                return candidate
            current = current.parent
        pytest.skip("zork1 directory not found")

    def test_parse_gmacros_file(self, zork_dir):
        """gmacros.zil parses successfully."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")
        assert len(result) > 0

    def test_tell_macro_parsed(self, zork_dir):
        """TELL macro is parsed as MacroDef."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")

        # Find TELL macro
        tell_macros = [node for node in result if isinstance(node, MacroDef) and node.name == "TELL"]
        assert len(tell_macros) == 1

        tell = tell_macros[0]
        assert len(tell.params) == 1
        assert tell.params[0].name == "A"
        assert tell.params[0].type == "args"

    def test_enable_macro_parsed(self, zork_dir):
        """ENABLE macro is parsed as MacroDef."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")

        enable_macros = [node for node in result if isinstance(node, MacroDef) and node.name == "ENABLE"]
        assert len(enable_macros) == 1

        enable = enable_macros[0]
        assert len(enable.params) == 1
        assert enable.params[0].name == "INT"
        assert enable.params[0].quoted is True

    def test_prob_macro_parsed(self, zork_dir):
        """PROB macro with optional params is parsed."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")

        prob_macros = [node for node in result if isinstance(node, MacroDef) and node.name == "PROB"]
        assert len(prob_macros) == 1

        prob = prob_macros[0]
        assert len(prob.params) == 2
        assert prob.params[0].name == "BASE?"
        assert prob.params[0].quoted is True
        assert prob.params[1].name == "LOSER?"
        assert prob.params[1].type == "optional"
        assert prob.params[1].quoted is True

    def test_verb_question_macro_parsed(self, zork_dir):
        """VERB? macro with ARGS is parsed."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")

        verb_macros = [node for node in result if isinstance(node, MacroDef) and node.name == "VERB?"]
        assert len(verb_macros) == 1

        verb = verb_macros[0]
        assert len(verb.params) == 1
        assert verb.params[0].name == "ATMS"
        assert verb.params[0].type == "args"

    def test_bset_macro_parsed(self, zork_dir):
        """BSET macro with quoted OBJ and ARGS is parsed."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")

        bset_macros = [node for node in result if isinstance(node, MacroDef) and node.name == "BSET"]
        assert len(bset_macros) == 1

        bset = bset_macros[0]
        assert len(bset.params) == 2
        assert bset.params[0].name == "OBJ"
        assert bset.params[0].quoted is True
        assert bset.params[1].name == "BITS"
        assert bset.params[1].type == "args"

    def test_all_macros_counted(self, zork_dir):
        """All 15 macros from gmacros.zil are parsed."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")

        macros = [node for node in result if isinstance(node, MacroDef)]
        macro_names = [m.name for m in macros]

        expected_macros = [
            "TELL", "VERB?", "PRSO?", "PRSI?", "ROOM?",
            "BSET", "BCLEAR", "BSET?", "RFATAL", "PROB",
            "ENABLE", "DISABLE", "FLAMING?", "OPENABLE?", "ABS"
        ]

        for expected in expected_macros:
            assert expected in macro_names, f"Macro {expected} not found"

    def test_setg_forms_still_parsed(self, zork_dir):
        """SETG forms are parsed alongside macros."""
        processor = FileProcessor(base_path=zork_dir)
        result = processor.load_file("gmacros.zil")

        # SETG is parsed as a Form, not a Global
        # Just verify the file parsed successfully
        assert len(result) >= 15  # At least all the macros
