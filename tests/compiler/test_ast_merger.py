"""Tests for AST merger."""
import pytest
from zil_interpreter.compiler.ast_merger import ASTMerger
from zil_interpreter.parser.ast_nodes import Global, Routine, Object


class TestASTMerger:
    """Tests for merging multiple file ASTs."""

    @pytest.fixture
    def merger(self):
        return ASTMerger()

    def test_merge_globals(self, merger):
        """Merge globals from multiple files."""
        ast1 = [Global('A', 1)]
        ast2 = [Global('B', 2)]
        result = merger.merge([ast1, ast2])
        names = [n.name for n in result if isinstance(n, Global)]
        assert 'A' in names
        assert 'B' in names

    def test_merge_preserves_order(self, merger):
        """Merged AST preserves file order."""
        ast1 = [Global('FIRST', 1)]
        ast2 = [Global('SECOND', 2)]
        result = merger.merge([ast1, ast2])
        names = [n.name for n in result if isinstance(n, Global)]
        assert names.index('FIRST') < names.index('SECOND')

    def test_merge_mixed_types(self, merger):
        """Merge handles different node types."""
        ast1 = [Global('G', 1), Routine('R', [], [])]
        ast2 = [Object('O', {})]
        result = merger.merge([ast1, ast2])
        assert len(result) == 3

    def test_empty_merge(self, merger):
        """Merging empty list returns empty."""
        assert merger.merge([]) == []

    def test_single_file_merge(self, merger):
        """Single file returns its AST."""
        ast = [Global('X', 1)]
        result = merger.merge([ast])
        assert result == ast
