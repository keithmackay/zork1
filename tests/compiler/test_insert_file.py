"""Tests for INSERT-FILE directive handling."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.parser.ast_nodes import InsertFile


class TestInsertFileDetection:
    """Tests for detecting INSERT-FILE directives."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_detect_insert_file_form(self, processor, tmp_path):
        """INSERT-FILE form is detected."""
        (tmp_path / "main.zil").write_text('<INSERT-FILE "other" T>')
        result = processor.load_file("main.zil")
        # Should contain InsertFile node
        assert any(isinstance(n, InsertFile) for n in result)

    def test_insert_file_extracts_filename(self, processor, tmp_path):
        """INSERT-FILE extracts target filename."""
        (tmp_path / "main.zil").write_text('<INSERT-FILE "GMACROS" T>')
        result = processor.load_file("main.zil")
        insert = next(n for n in result if isinstance(n, InsertFile))
        assert insert.filename == "GMACROS"

    def test_multiple_insert_files(self, processor, tmp_path):
        """Multiple INSERT-FILE directives detected."""
        content = '''
        <INSERT-FILE "A" T>
        <INSERT-FILE "B" T>
        <INSERT-FILE "C" T>
        '''
        (tmp_path / "main.zil").write_text(content)
        result = processor.load_file("main.zil")
        inserts = [n for n in result if isinstance(n, InsertFile)]
        assert len(inserts) == 3
