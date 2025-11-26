"""Tests for ZIL file processor."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor


class TestFileProcessor:
    """Tests for file loading and processing."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_load_single_file(self, processor, tmp_path):
        """Load a single ZIL file."""
        (tmp_path / "test.zil").write_text('<GLOBAL FOO 1>')
        result = processor.load_file("test.zil")
        assert result is not None
        assert len(result) == 1

    def test_file_not_found(self, processor):
        """Missing file raises error."""
        with pytest.raises(FileNotFoundError):
            processor.load_file("nonexistent.zil")

    def test_base_path_resolution(self, tmp_path):
        """Files resolved relative to base path."""
        subdir = tmp_path / "src"
        subdir.mkdir()
        (subdir / "game.zil").write_text('<GLOBAL X 1>')

        processor = FileProcessor(base_path=subdir)
        result = processor.load_file("game.zil")
        assert result is not None
