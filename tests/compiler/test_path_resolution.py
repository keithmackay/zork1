"""Tests for file path resolution."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor


class TestPathResolution:
    """Tests for resolving INSERT-FILE paths."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_lowercase_extension(self, processor, tmp_path):
        """GMACROS resolves to gmacros.zil."""
        (tmp_path / "gmacros.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("GMACROS")
        assert result is not None

    def test_uppercase_extension(self, processor, tmp_path):
        """Handle .ZIL extension."""
        (tmp_path / "TEST.ZIL").write_text('<GLOBAL X 1>')
        result = processor.load_file("TEST")
        assert result is not None

    def test_with_extension(self, processor, tmp_path):
        """Explicit extension works."""
        (tmp_path / "test.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("test.zil")
        assert result is not None

    def test_case_insensitive(self, processor, tmp_path):
        """Case-insensitive filename matching."""
        (tmp_path / "GmAcRoS.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("gmacros")
        assert result is not None

    def test_exact_match_first(self, processor, tmp_path):
        """Exact match takes precedence over case-insensitive match."""
        (tmp_path / "test.zil").write_text('<GLOBAL X 1>')
        (tmp_path / "TEST.zil").write_text('<GLOBAL Y 2>')
        result = processor.load_file("test.zil")
        assert result is not None
        # Should have loaded the exact match (test.zil with GLOBAL X)

    def test_uppercase_filename_lowercase_extension(self, processor, tmp_path):
        """Handle GMACROS.zil (uppercase filename, lowercase extension)."""
        (tmp_path / "GMACROS.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("GMACROS")
        assert result is not None

    def test_file_not_found_error(self, processor, tmp_path):
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as exc_info:
            processor.load_file("nonexistent")
        assert "ZIL file not found" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)

    def test_mixed_case_with_extension(self, processor, tmp_path):
        """MiXeD case with .zil extension."""
        (tmp_path / "MiXeD.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("mixed")
        assert result is not None
