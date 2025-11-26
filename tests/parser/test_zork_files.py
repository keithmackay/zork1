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

    @pytest.mark.parametrize("filename", [
        "zork1.zil",
        "gmacros.zil",
        "gsyntax.zil",
        "gparser.zil",
        "gverbs.zil",
        "gglobals.zil",
        "gmain.zil",
        "gclock.zil",
        "1dungeon.zil",
        "1actions.zil",
    ])
    def test_parse_all_zork_files(self, parser, zork_dir, filename):
        """Attempt to parse all Zork I files completely."""
        filepath = zork_dir / filename
        if not filepath.exists():
            pytest.skip(f"zork1/{filename} not found at {filepath}")

        content = filepath.read_text()

        try:
            tree = parser.parse(content)
            assert tree is not None
            print(f"\n✓ {filename} parsed successfully ({len(content)} bytes)")
        except Exception as e:
            # Log detailed error information for debugging
            error_msg = str(e)
            print(f"\n✗ {filename} failed to parse:")
            print(f"  Error: {error_msg[:200]}")

            # Extract line number if available
            if "line" in error_msg.lower():
                print(f"  Full error: {error_msg}")

            # Re-raise to mark test as failed
            pytest.fail(f"{filename} parsing failed: {error_msg[:500]}")
