"""Tests for SYNTAX table building (Task 4.7)."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.compiler.syntax_table import SyntaxTable, parse_syntax_entry
from zil_interpreter.compiler.directives import SyntaxDef, ObjectConstraint
from zil_interpreter.parser.ast_nodes import Form, Atom


class TestSyntaxTableBuilder:
    """Tests for SYNTAX directive processing and table building."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_syntax_simple(self, processor):
        """Process simple SYNTAX without objects."""
        # <SYNTAX QUIT = V-QUIT>
        form = Form(Atom("SYNTAX"), [
            Atom("QUIT"), Atom("="), Atom("V-QUIT")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("QUIT")
        assert len(entries) == 1
        assert entries[0].action == "V-QUIT"
        assert entries[0].object_count == 0

    def test_syntax_with_object(self, processor):
        """Process SYNTAX with single OBJECT."""
        # <SYNTAX TAKE OBJECT = V-TAKE>
        form = Form(Atom("SYNTAX"), [
            Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("TAKE")
        assert len(entries) == 1
        assert entries[0].object_count == 1

    def test_syntax_with_preaction(self, processor):
        """Process SYNTAX with preaction."""
        # <SYNTAX TAKE OBJECT = V-TAKE PRE-TAKE>
        form = Form(Atom("SYNTAX"), [
            Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE"), Atom("PRE-TAKE")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("TAKE")
        assert entries[0].preaction == "PRE-TAKE"

    def test_syntax_with_constraints(self, processor):
        """Process SYNTAX with object constraints."""
        # <SYNTAX TAKE OBJECT (TAKEABLE) = V-TAKE>
        form = Form(Atom("SYNTAX"), [
            Atom("TAKE"), Atom("OBJECT"),
            [Atom("TAKEABLE")],
            Atom("="), Atom("V-TAKE")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("TAKE")
        assert "TAKEABLE" in entries[0].constraints[0]

    def test_syntax_with_preposition(self, processor):
        """Process SYNTAX with preposition and two objects."""
        # <SYNTAX PUT OBJECT IN OBJECT = V-PUT>
        form = Form(Atom("SYNTAX"), [
            Atom("PUT"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
            Atom("="), Atom("V-PUT")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("PUT")
        assert len(entries) == 1
        assert entries[0].object_count == 2
        assert "IN" in entries[0].prepositions

    def test_syntax_with_two_objects_and_preaction(self, processor):
        """Process SYNTAX with two objects and preaction."""
        # <SYNTAX PUT OBJECT IN OBJECT = V-PUT PRE-PUT>
        form = Form(Atom("SYNTAX"), [
            Atom("PUT"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
            Atom("="), Atom("V-PUT"), Atom("PRE-PUT")
        ])
        processor.process(form)
        entries = processor.syntax_table.lookup("PUT")
        assert entries[0].preaction == "PRE-PUT"

    def test_syntax_multiple_patterns(self, processor):
        """Same verb can have multiple SYNTAX patterns."""
        # Multiple DROP patterns
        processor.process(Form(Atom("SYNTAX"), [
            Atom("DROP"), Atom("OBJECT"), Atom("="), Atom("V-DROP")
        ]))
        processor.process(Form(Atom("SYNTAX"), [
            Atom("DROP"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
            Atom("="), Atom("V-PUT"), Atom("PRE-PUT")
        ]))
        entries = processor.syntax_table.lookup("DROP")
        assert len(entries) == 2

    def test_syntax_count(self, processor):
        """Entry count increments correctly."""
        processor.process(Form(Atom("SYNTAX"), [
            Atom("QUIT"), Atom("="), Atom("V-QUIT")
        ]))
        processor.process(Form(Atom("SYNTAX"), [
            Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE")
        ]))
        processor.process(Form(Atom("SYNTAX"), [
            Atom("DROP"), Atom("OBJECT"), Atom("="), Atom("V-DROP")
        ]))
        assert processor.syntax_table.entry_count == 3

    def test_syntax_case_insensitive_lookup(self, processor):
        """SYNTAX lookup is case-insensitive."""
        processor.process(Form(Atom("SYNTAX"), [
            Atom("QUIT"), Atom("="), Atom("V-QUIT")
        ]))
        assert len(processor.syntax_table.lookup("quit")) == 1
        assert len(processor.syntax_table.lookup("QUIT")) == 1


class TestSyntaxTableLookup:
    """Tests for SYNTAX table matching."""

    def test_match_simple(self):
        """Match simple verb-only command."""
        table = SyntaxTable()
        table.add_entry("QUIT", [], [], "V-QUIT", None)
        match = table.match("QUIT", 0, None)
        assert match is not None
        assert match.action == "V-QUIT"

    def test_match_with_object(self):
        """Match command with one object."""
        table = SyntaxTable()
        table.add_entry("TAKE", [1], [], "V-TAKE", None)
        match = table.match("TAKE", 1, None)
        assert match is not None
        assert match.action == "V-TAKE"

    def test_match_with_two_objects(self):
        """Match command with two objects."""
        table = SyntaxTable()
        table.add_entry("PUT", [1, 2], ["IN"], "V-PUT", "PRE-PUT")
        match = table.match("PUT", 2, "IN")
        assert match is not None
        assert match.preaction == "PRE-PUT"

    def test_no_match_verb(self):
        """Return None when verb doesn't match."""
        table = SyntaxTable()
        table.add_entry("QUIT", [], [], "V-QUIT", None)
        assert table.match("INVALID", 0, None) is None

    def test_no_match_object_count(self):
        """Return None when object count doesn't match."""
        table = SyntaxTable()
        table.add_entry("TAKE", [1], [], "V-TAKE", None)
        assert table.match("TAKE", 0, None) is None
        assert table.match("TAKE", 2, None) is None

    def test_no_match_preposition(self):
        """Return None when preposition doesn't match."""
        table = SyntaxTable()
        table.add_entry("PUT", [1, 2], ["IN"], "V-PUT", None)
        assert table.match("PUT", 2, "ON") is None

    def test_match_case_insensitive(self):
        """Match is case-insensitive."""
        table = SyntaxTable()
        table.add_entry("TAKE", [1], [], "V-TAKE", None)
        assert table.match("take", 1, None) is not None
        assert table.match("TAKE", 1, None) is not None

    def test_match_preposition_case_insensitive(self):
        """Preposition match is case-insensitive."""
        table = SyntaxTable()
        table.add_entry("PUT", [1, 2], ["IN"], "V-PUT", None)
        assert table.match("PUT", 2, "in") is not None


class TestParseSyntaxEntry:
    """Tests for parse_syntax_entry function."""

    def test_parse_simple(self):
        """Parse simple verb-only syntax."""
        # <SYNTAX QUIT = V-QUIT>
        args = [Atom("QUIT"), Atom("="), Atom("V-QUIT")]
        result = parse_syntax_entry(args)
        assert result is not None
        assert result.verb == "QUIT"
        assert result.action == "V-QUIT"
        assert len(result.objects) == 0

    def test_parse_with_object(self):
        """Parse syntax with object."""
        # <SYNTAX TAKE OBJECT = V-TAKE>
        args = [Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE")]
        result = parse_syntax_entry(args)
        assert result is not None
        assert len(result.objects) == 1
        assert result.objects[0].position == 1

    def test_parse_with_preaction(self):
        """Parse syntax with preaction."""
        # <SYNTAX TAKE OBJECT = V-TAKE PRE-TAKE>
        args = [Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE"), Atom("PRE-TAKE")]
        result = parse_syntax_entry(args)
        assert result is not None
        assert result.preaction == "PRE-TAKE"

    def test_parse_with_constraints(self):
        """Parse syntax with object constraints."""
        # <SYNTAX TAKE OBJECT (TAKEABLE HELD) = V-TAKE>
        args = [Atom("TAKE"), Atom("OBJECT"), [Atom("TAKEABLE"), Atom("HELD")], Atom("="), Atom("V-TAKE")]
        result = parse_syntax_entry(args)
        assert result is not None
        assert "TAKEABLE" in result.objects[0].constraints
        assert "HELD" in result.objects[0].constraints

    def test_parse_with_preposition(self):
        """Parse syntax with preposition."""
        # <SYNTAX PUT OBJECT IN OBJECT = V-PUT>
        args = [Atom("PUT"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"), Atom("="), Atom("V-PUT")]
        result = parse_syntax_entry(args)
        assert result is not None
        assert len(result.objects) == 2
        assert "IN" in result.prepositions

    def test_parse_empty_args(self):
        """Empty args return None."""
        assert parse_syntax_entry([]) is None

    def test_parse_no_equals(self):
        """No equals sign returns None."""
        args = [Atom("QUIT"), Atom("V-QUIT")]
        assert parse_syntax_entry(args) is None

    def test_parse_real_zork_syntax(self):
        """Parse real Zork syntax patterns."""
        # <SYNTAX CUT OBJECT WITH OBJECT (FIND WEAPONBIT) (CARRIED HELD) = V-CUT>
        args = [
            Atom("CUT"), Atom("OBJECT"), Atom("WITH"), Atom("OBJECT"),
            [Atom("FIND"), Atom("WEAPONBIT")],
            [Atom("CARRIED"), Atom("HELD")],
            Atom("="), Atom("V-CUT")
        ]
        result = parse_syntax_entry(args)
        assert result is not None
        assert result.verb == "CUT"
        assert len(result.objects) == 2
        assert "WITH" in result.prepositions


class TestSyntaxDefDataclass:
    """Tests for SyntaxDef dataclass."""

    def test_create_simple(self):
        """Create simple SyntaxDef."""
        syntax = SyntaxDef(verb="QUIT", action="V-QUIT")
        assert syntax.verb == "QUIT"
        assert syntax.action == "V-QUIT"
        assert syntax.objects == []
        assert syntax.prepositions == []
        assert syntax.preaction is None

    def test_create_with_all_fields(self):
        """Create SyntaxDef with all fields."""
        syntax = SyntaxDef(
            verb="PUT",
            action="V-PUT",
            objects=[
                ObjectConstraint(position=1, constraints=["HELD"]),
                ObjectConstraint(position=2, constraints=["CONTBIT"])
            ],
            prepositions=["IN", "INTO"],
            preaction="PRE-PUT"
        )
        assert syntax.verb == "PUT"
        assert len(syntax.objects) == 2
        assert len(syntax.prepositions) == 2
        assert syntax.preaction == "PRE-PUT"
