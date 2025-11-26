"""Integration tests for parsing Zork I ZIL files."""
import pytest
from pathlib import Path
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestZorkFileParsing:
    """Integration tests parsing actual Zork I files."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    @pytest.fixture
    def zork_dir(self):
        # Find zork1 directory - it's in the parent repo, not the worktree
        worktree_root = Path(__file__).parent.parent.parent
        # Go up to parent repo
        parent_repo = worktree_root.parent.parent
        return parent_repo / "zork1"

    def test_parse_gmacros_header(self, parser, zork_dir):
        """Parser handles gmacros.zil header."""
        gmacros = zork_dir / "gmacros.zil"
        if not gmacros.exists():
            pytest.skip(f"zork1/gmacros.zil not found at {gmacros}")

        content = gmacros.read_text()
        # Parse header comment + first 3 SETG forms (complete expressions)
        lines = content.split('\n')
        header = '\n'.join(lines[:8])  # Lines 1-8: header string + 3 SETG forms + blank line
        tree = parser.parse(header)
        assert tree is not None

    def test_parse_gglobals_header(self, parser, zork_dir):
        """Parser handles gglobals.zil header."""
        gglobals = zork_dir / "gglobals.zil"
        if not gglobals.exists():
            pytest.skip(f"zork1/gglobals.zil not found at {gglobals}")

        content = gglobals.read_text()
        # Parse header comments + first complete OBJECT (GLOBAL-OBJECTS)
        lines = content.split('\n')
        header = '\n'.join(lines[:11])  # Lines 1-11: 2 header strings + first OBJECT + blank line
        tree = parser.parse(header)
        assert tree is not None
