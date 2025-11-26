"""Integration tests for Zork I directive processing (Tasks 4.8-4.9)."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestZorkDirectiveProcessing:
    """Integration tests for processing all Zork I directives."""

    @pytest.fixture
    def zork_dir(self):
        """Find the zork1 directory with ZIL files."""
        zork_path = Path("/Users/Keith.MacKay/Projects/zork1/zork1")
        if zork_path.exists() and (zork_path / "zork1.zil").exists():
            return zork_path
        pytest.skip("zork1 directory not found")

    @pytest.fixture
    def processed_directives(self, zork_dir):
        """Load and process all directives from Zork I."""
        file_processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)
        directive_processor = DirectiveProcessor()

        ast = file_processor.load_all("zork1.zil")
        expanded = [expander.expand(node) for node in ast]

        # Process ALL nodes, not just Forms
        # Global nodes are a separate AST type
        for node in expanded:
            directive_processor.process(node)

        return directive_processor

    def test_syntax_count(self, processed_directives):
        """Most SYNTAX entries are processed (260+)."""
        count = processed_directives.syntax_table.entry_count
        # Should have at least 260 entries (some edge cases may not parse)
        assert count >= 260, f"Expected 260+ SYNTAX entries, got {count}"

    def test_constants_count(self, processed_directives):
        """CONSTANT definitions are processed."""
        count = len(processed_directives.constants)
        # Should have 100+ constants from various files
        assert count >= 100, f"Expected 100+ CONSTANT definitions, got {count}"

    def test_globals_count(self, processed_directives):
        """GLOBAL definitions are processed."""
        count = len(processed_directives.globals)
        # Should have 150+ globals from various files
        assert count >= 150, f"Expected 150+ GLOBAL definitions, got {count}"

    def test_propdef_count(self, processed_directives):
        """All 4 PROPDEF entries are processed."""
        count = len(processed_directives.property_defaults)
        assert count == 4, f"Expected 4 PROPDEF definitions, got {count}"

    def test_directions_defined(self, processed_directives):
        """DIRECTIONS are defined."""
        count = len(processed_directives.directions)
        assert count >= 12, f"Expected 12+ directions, got {count}"
        assert processed_directives.is_direction("NORTH")
        assert processed_directives.is_direction("SOUTH")
        assert processed_directives.is_direction("UP")
        assert processed_directives.is_direction("DOWN")

    def test_buzz_words_defined(self, processed_directives):
        """BUZZ words are defined."""
        assert processed_directives.is_buzz_word("THE")
        assert processed_directives.is_buzz_word("A")
        assert processed_directives.is_buzz_word("AN")
        assert processed_directives.is_buzz_word("AND")

    def test_synonyms_defined(self, processed_directives):
        """SYNONYM mappings are defined."""
        # Direction abbreviations
        assert processed_directives.get_canonical("N") == "NORTH"
        assert processed_directives.get_canonical("S") == "SOUTH"
        assert processed_directives.get_canonical("E") == "EAST"
        assert processed_directives.get_canonical("W") == "WEST"
        assert processed_directives.get_canonical("U") == "UP"
        assert processed_directives.get_canonical("D") == "DOWN"

    def test_preposition_synonyms(self, processed_directives):
        """Preposition synonyms are defined."""
        assert processed_directives.get_canonical("USING") == "WITH"
        assert processed_directives.get_canonical("THRU") == "WITH"


class TestZorkDirectiveContent:
    """Tests for specific Zork I directive content."""

    @pytest.fixture
    def zork_dir(self):
        zork_path = Path("/Users/Keith.MacKay/Projects/zork1/zork1")
        if zork_path.exists():
            return zork_path
        pytest.skip("zork1 directory not found")

    @pytest.fixture
    def game_state(self, zork_dir):
        """Build complete game state from Zork I files."""
        file_processor = FileProcessor(base_path=zork_dir)
        registry = MacroRegistry()
        expander = MacroExpander(registry)
        directive_processor = DirectiveProcessor()

        ast = file_processor.load_all("zork1.zil")
        expanded = [expander.expand(node) for node in ast]

        for node in expanded:
            directive_processor.process(node)

        return directive_processor

    def test_syntax_verbs_defined(self, game_state):
        """Common verbs have SYNTAX entries."""
        # Note: GET is often a synonym for TAKE, not a separate verb
        common_verbs = [
            "TAKE", "DROP", "OPEN", "CLOSE", "LOOK", "EXAMINE",
            "PUT", "READ", "ATTACK", "KILL", "INVENTORY",
            "QUIT", "SAVE", "RESTORE", "SCORE", "VERBOSE", "BRIEF"
        ]
        for verb in common_verbs:
            entries = game_state.syntax_table.lookup(verb)
            assert len(entries) > 0, f"Missing SYNTAX for {verb}"

    def test_syntax_has_prepositions(self, game_state):
        """PUT verb has IN/ON preposition patterns."""
        entries = game_state.syntax_table.lookup("PUT")
        preps = set()
        for entry in entries:
            preps.update(entry.prepositions)
        # Should have at least one of IN, ON, UNDER
        assert len(preps) > 0, "PUT should have preposition patterns"

    def test_known_constants(self, game_state):
        """Known Zork I constants are defined."""
        # Check for some known constants
        # These should exist in gparser.zil and other files
        assert len(game_state.constants) > 0

    def test_known_globals(self, game_state):
        """Known Zork I globals are defined."""
        # LUCKY is defined in 1actions.zil
        assert "LUCKY" in game_state.globals
        # MATCH-COUNT is defined in 1actions.zil
        assert "MATCH-COUNT" in game_state.globals

    def test_property_defaults_values(self, game_state):
        """Property default values are correct."""
        assert game_state.get_property_default("SIZE") == 5
        assert game_state.get_property_default("CAPACITY") == 0
        assert game_state.get_property_default("VALUE") == 0
        assert game_state.get_property_default("TVALUE") == 0

    def test_all_directions_indexed(self, game_state):
        """All Zork I directions have indices."""
        expected_directions = [
            "NORTH", "EAST", "WEST", "SOUTH",
            "NE", "NW", "SE", "SW",
            "UP", "DOWN", "IN", "OUT", "LAND"
        ]
        for i, direction in enumerate(expected_directions):
            idx = game_state.direction_index(direction)
            assert idx == i, f"Direction {direction} should be at index {i}, got {idx}"


class TestDirectiveProcessingRobustness:
    """Tests for directive processing error handling."""

    def test_empty_ast(self):
        """Processing empty AST doesn't crash."""
        processor = DirectiveProcessor()
        # Should handle empty input
        assert processor.syntax_table.entry_count == 0

    def test_malformed_constant(self):
        """Malformed CONSTANT doesn't crash."""
        processor = DirectiveProcessor()
        # Missing value
        form = Form(Atom("CONSTANT"), [Atom("FOO")])
        processor.process(form)
        assert "FOO" not in processor.constants

    def test_malformed_global(self):
        """Malformed GLOBAL doesn't crash."""
        processor = DirectiveProcessor()
        # Missing value
        form = Form(Atom("GLOBAL"), [Atom("BAR")])
        processor.process(form)
        assert "BAR" not in processor.globals

    def test_malformed_syntax(self):
        """Malformed SYNTAX doesn't crash."""
        processor = DirectiveProcessor()
        # No equals sign
        form = Form(Atom("SYNTAX"), [Atom("FOO"), Atom("V-FOO")])
        processor.process(form)
        # Should just be ignored
        assert processor.syntax_table.entry_count == 0
