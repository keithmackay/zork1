"""Tests for circular reference detection."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor, CircularDependencyError
from zil_interpreter.parser.ast_nodes import Form, Atom, Global


class TestCycleDetection:
    """Tests for detecting circular INSERT-FILE chains."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def _get_global_name(self, node) -> str:
        """Extract GLOBAL name from Form or Global node."""
        # Handle new Global AST node
        if isinstance(node, Global):
            return node.name
        # Handle old-style Form node (for backward compatibility)
        if isinstance(node, Form) and isinstance(node.operator, Atom):
            if node.operator.value == 'GLOBAL' and node.args and isinstance(node.args[0], Atom):
                return node.args[0].value
        return ''

    def test_direct_cycle(self, processor, tmp_path):
        """File including itself raises error."""
        (tmp_path / "self.zil").write_text('<INSERT-FILE "self" T>')

        with pytest.raises(CircularDependencyError) as exc_info:
            processor.load_all("self.zil")

        # Error message should show the cycle
        assert "Circular" in str(exc_info.value)

    def test_indirect_cycle(self, processor, tmp_path):
        """A → B → A raises error."""
        (tmp_path / "a.zil").write_text('<INSERT-FILE "b" T>')
        (tmp_path / "b.zil").write_text('<INSERT-FILE "a" T>')

        with pytest.raises(CircularDependencyError) as exc_info:
            processor.load_all("a.zil")

        # Error message should show the cycle
        assert "Circular" in str(exc_info.value)

    def test_diamond_ok(self, processor, tmp_path):
        """Diamond pattern (A→B,C; B→D; C→D) is OK."""
        (tmp_path / "a.zil").write_text('''
        <INSERT-FILE "b" T>
        <INSERT-FILE "c" T>
        ''')
        (tmp_path / "b.zil").write_text('<INSERT-FILE "d" T>')
        (tmp_path / "c.zil").write_text('<INSERT-FILE "d" T>')
        (tmp_path / "d.zil").write_text('<GLOBAL SHARED 1>')

        # Should not raise (d included twice is OK)
        result = processor.load_all("a.zil")
        assert result is not None

    def test_no_duplicate_loading(self, processor, tmp_path):
        """Same file included twice is loaded only once."""
        (tmp_path / "main.zil").write_text('''
        <INSERT-FILE "common" T>
        <INSERT-FILE "common" T>
        ''')
        (tmp_path / "common.zil").write_text('<GLOBAL X 1>')

        result = processor.load_all("main.zil")
        # X should appear only once
        global_names = [self._get_global_name(n) for n in result if self._get_global_name(n)]
        x_count = global_names.count('X')
        assert x_count == 1

    def test_three_cycle(self, processor, tmp_path):
        """A → B → C → A raises error."""
        (tmp_path / "a.zil").write_text('<INSERT-FILE "b" T>')
        (tmp_path / "b.zil").write_text('<INSERT-FILE "c" T>')
        (tmp_path / "c.zil").write_text('<INSERT-FILE "a" T>')

        with pytest.raises(CircularDependencyError) as exc_info:
            processor.load_all("a.zil")

        # Error message should show the cycle
        assert "Circular" in str(exc_info.value)

    def test_complex_diamond_no_cycle(self, processor, tmp_path):
        """Complex diamond with multiple paths to same files is OK."""
        (tmp_path / "main.zil").write_text('''
        <INSERT-FILE "left" T>
        <INSERT-FILE "right" T>
        ''')
        (tmp_path / "left.zil").write_text('''
        <INSERT-FILE "shared" T>
        <GLOBAL LEFT 1>
        ''')
        (tmp_path / "right.zil").write_text('''
        <INSERT-FILE "shared" T>
        <GLOBAL RIGHT 2>
        ''')
        (tmp_path / "shared.zil").write_text('<GLOBAL SHARED 3>')

        # Should not raise - shared loaded only once
        result = processor.load_all("main.zil")
        assert result is not None

        global_names = [self._get_global_name(n) for n in result if self._get_global_name(n)]
        assert global_names.count('SHARED') == 1
        assert 'LEFT' in global_names
        assert 'RIGHT' in global_names
