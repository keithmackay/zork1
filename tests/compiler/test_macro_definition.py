"""Tests for DEFMAC parsing and AST representation."""
import pytest
from zil_interpreter.parser.ast_nodes import MacroDef, MacroParam
from zil_interpreter.compiler.file_processor import FileProcessor


class TestMacroDefinition:
    """Tests for parsing DEFMAC forms."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_simple_macro_definition(self, processor, tmp_path):
        """Simple macro creates MacroDef node."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC ENABLE (\'INT) <FORM PUT .INT ,C-ENABLED? 1>>'
        )
        result = processor.load_file("test.zil")
        assert len(result) == 1
        assert isinstance(result[0], MacroDef)
        assert result[0].name == "ENABLE"

    def test_macro_with_args(self, processor, tmp_path):
        """ARGS parameter captures remaining arguments."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC VERB? ("ARGS" ATMS) <MULTIFROB PRSA .ATMS>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert macro.name == "VERB?"
        assert any(p.type == "args" for p in macro.params)

    def test_macro_with_optional(self, processor, tmp_path):
        """Optional parameters parsed correctly."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC PROB (\'BASE? "OPTIONAL" \'LOSER?) <FORM G? .BASE? 5>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert len(macro.params) == 2
        assert macro.params[1].type == "optional"

    def test_macro_quoted_param(self, processor, tmp_path):
        """Quoted parameters are detected."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC ENABLE (\'INT) <FORM PUT .INT ,C-ENABLED? 1>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert macro.params[0].quoted is True
        assert macro.params[0].name == "INT"

    def test_macro_unquoted_param(self, processor, tmp_path):
        """Unquoted parameters not marked as quoted."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC TEST (X Y) <FORM PRINT .X>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert macro.params[0].quoted is False
        assert macro.params[0].name == "X"

    def test_macro_body_preserved(self, processor, tmp_path):
        """Macro body is preserved."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC TEST (X) <FORM PRINT .X>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert macro.body is not None

    def test_macro_aux_params(self, processor, tmp_path):
        """AUX parameters are parsed."""
        (tmp_path / "test.zil").write_text(
            '<DEFMAC TEST ("AUX" X Y) <FORM PRINT 1>>'
        )
        result = processor.load_file("test.zil")
        macro = result[0]
        assert any(p.type == "aux" for p in macro.params)
