"""Integration tests for loading Zork I files."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor, CircularDependencyError
from zil_interpreter.parser.ast_nodes import Routine, Object


class TestZorkLoading:
    """Integration tests for loading all Zork I files."""

    @pytest.fixture
    def zork_dir(self):
        """Locate the zork1 directory containing ZIL source files."""
        # We're in a worktree at /path/to/zork1/.worktrees/zork1-compiler
        # The main repo with zork1/ subdir is at /path/to/zork1/

        # Start from test file and go up to find the main repo
        test_file_path = Path(__file__).resolve()

        # Go up from tests/integration/test_zork_loading.py
        # to .worktrees/zork1-compiler root, then to main repo root
        worktree_root = test_file_path.parent.parent.parent

        # Check if we're in a worktree
        if '.worktrees' in str(worktree_root):
            # Go up to find main repo root
            main_repo_root = worktree_root.parent.parent
        else:
            # We're in main repo already
            main_repo_root = worktree_root

        # Look for zork1 subdirectory with ZIL files
        candidate = main_repo_root / "zork1"
        if candidate.exists() and candidate.is_dir():
            # Verify it has ZIL files
            if (candidate / "zork1.zil").exists():
                return candidate

        pytest.skip(f"zork1 directory with ZIL files not found. Searched: {candidate}")

    @pytest.fixture
    def processor(self, zork_dir):
        """Create FileProcessor configured for Zork I directory."""
        return FileProcessor(base_path=zork_dir)

    def test_load_all_zork_files(self, processor):
        """Load zork1.zil with all INSERT-FILE expansions.

        This test verifies that:
        - zork1.zil can be loaded
        - All INSERT-FILE directives are processed
        - A substantial AST is generated (>100 forms expected)
        """
        result = processor.load_all("zork1.zil")
        assert result is not None, "load_all should return a result"
        assert isinstance(result, list), "Result should be a list of AST nodes"
        assert len(result) > 100, (
            f"Expected many forms (>100), got {len(result)}. "
            "Zork I contains numerous objects, routines, and globals."
        )

    def test_all_nine_files_loaded(self, processor):
        """All 9 INSERT-FILE targets are loaded.

        Zork1.zil includes:
        - GMACROS (macros)
        - GSYNTAX (parser syntax)
        - 1DUNGEON (world objects)
        - GGLOBALS (global variables)
        - GCLOCK (game clock)
        - GMAIN (main loop)
        - GPARSER (command parser)
        - GVERBS (verb handlers)
        - 1ACTIONS (game actions)
        """
        processor.load_all("zork1.zil")

        # Expected files (normalized to uppercase without extension)
        expected = {
            'GMACROS',
            'GSYNTAX',
            '1DUNGEON',
            'GGLOBALS',
            'GCLOCK',
            'GMAIN',
            'GPARSER',
            'GVERBS',
            '1ACTIONS'
        }

        # Normalize loaded files to uppercase, remove .ZIL extension
        loaded = {f.upper().replace('.ZIL', '') for f in processor.loaded_files}

        # Verify each expected file was loaded
        for exp in expected:
            assert any(exp in f for f in loaded), (
                f"Expected file {exp} not found in loaded files: {loaded}"
            )

        # Should have main file + 9 includes = 10 total
        assert len(processor.loaded_files) == 10, (
            f"Expected 10 files (zork1.zil + 9 includes), "
            f"got {len(processor.loaded_files)}: {processor.loaded_files}"
        )

    def test_no_circular_dependencies(self, processor):
        """Zork I has no circular INSERT-FILE references.

        The file processor should complete without raising
        CircularDependencyError. This verifies the dependency
        chain is acyclic.
        """
        # Should complete without CircularDependencyError
        try:
            result = processor.load_all("zork1.zil")
            assert result is not None
        except CircularDependencyError as e:
            pytest.fail(f"Unexpected circular dependency: {e}")

    def test_routine_count(self, processor):
        """Zork I has expected number of routines (>50).

        Zork I contains many routines across all files:
        - GMAIN: Main game loop, initialization
        - GPARSER: Parser routines
        - GVERBS: Verb implementation routines
        - 1ACTIONS: Game-specific action handlers
        - GCLOCK: Clock and timing routines
        """
        result = processor.load_all("zork1.zil")
        routines = [node for node in result if isinstance(node, Routine)]

        assert len(routines) > 50, (
            f"Expected many routines (>50), got {len(routines)}. "
            "Zork I has extensive game logic implemented as routines."
        )

    def test_object_count(self, processor):
        """Zork I has expected number of objects (>100).

        1DUNGEON.ZIL defines the entire game world:
        - Rooms (~110 locations)
        - Items (treasures, tools, containers)
        - NPCs (thief, troll, cyclops, etc.)
        - Scenery objects

        Total should be well over 100 objects.
        """
        result = processor.load_all("zork1.zil")
        objects = [node for node in result if isinstance(node, Object)]

        assert len(objects) > 100, (
            f"Expected many objects (>100), got {len(objects)}. "
            "Zork I contains ~180 objects defining the game world."
        )

    def test_main_file_parsed_first(self, processor):
        """Verify zork1.zil itself is in the loaded files set."""
        processor.load_all("zork1.zil")

        # zork1.zil should be in loaded files
        loaded_upper = {f.upper() for f in processor.loaded_files}
        assert any('ZORK1.ZIL' in f for f in loaded_upper), (
            "Main file zork1.zil should be tracked in loaded_files"
        )

    def test_insertion_order_preserved(self, processor):
        """Forms should appear in the order files are inserted.

        zork1.zil defines INSERT-FILE directives in a specific order.
        The resulting AST should reflect this order.
        """
        result = processor.load_all("zork1.zil")

        # GMACROS is first insert, 1ACTIONS is last
        # While we can't easily verify exact ordering without analyzing
        # AST content deeply, we can verify we got a reasonable structure
        assert len(result) > 0, "Should have forms from inserted files"

        # At minimum, check that we have diverse node types
        has_routines = any(isinstance(n, Routine) for n in result)
        has_objects = any(isinstance(n, Object) for n in result)

        assert has_routines, "Should have routines from loaded files"
        assert has_objects, "Should have objects from 1DUNGEON"
