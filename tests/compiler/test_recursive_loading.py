"""Tests for recursive file loading."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestRecursiveLoading:
    """Tests for following INSERT-FILE directives."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def _get_global_name(self, node) -> str:
        """Extract GLOBAL name from Form node."""
        if isinstance(node, Form) and isinstance(node.operator, Atom):
            if node.operator.value == 'GLOBAL' and node.args and isinstance(node.args[0], Atom):
                return node.args[0].value
        return ''

    def test_follow_insert_file(self, processor, tmp_path):
        """INSERT-FILE loads the referenced file."""
        (tmp_path / "main.zil").write_text('''
        <GLOBAL MAIN 1>
        <INSERT-FILE "other" T>
        ''')
        (tmp_path / "other.zil").write_text('<GLOBAL OTHER 2>')

        result = processor.load_all("main.zil")
        # Both globals should be present
        global_names = [self._get_global_name(n) for n in result if self._get_global_name(n)]
        assert len(global_names) >= 2
        assert 'MAIN' in global_names
        assert 'OTHER' in global_names

    def test_deep_nesting(self, processor, tmp_path):
        """Three levels of INSERT-FILE nesting."""
        (tmp_path / "a.zil").write_text('<INSERT-FILE "b" T>')
        (tmp_path / "b.zil").write_text('<INSERT-FILE "c" T>')
        (tmp_path / "c.zil").write_text('<GLOBAL DEEP 3>')

        result = processor.load_all("a.zil")
        global_names = [self._get_global_name(n) for n in result if self._get_global_name(n)]
        assert 'DEEP' in global_names

    def test_preserves_order(self, processor, tmp_path):
        """Forms appear in correct order."""
        (tmp_path / "main.zil").write_text('''
        <GLOBAL FIRST 1>
        <INSERT-FILE "other" T>
        <GLOBAL LAST 3>
        ''')
        (tmp_path / "other.zil").write_text('<GLOBAL MIDDLE 2>')

        result = processor.load_all("main.zil")
        global_names = [self._get_global_name(n) for n in result if self._get_global_name(n)]
        assert global_names.index('FIRST') < global_names.index('MIDDLE') < global_names.index('LAST')
