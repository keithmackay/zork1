"""Tests for CommandParser (Tasks 5.6-5.7)."""
import pytest
from zil_interpreter.runtime.command_parser import CommandParser
from zil_interpreter.runtime.command_lexer import CommandLexer
from zil_interpreter.runtime.command_types import Token, TokenType, NounPhrase
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom


@pytest.fixture
def processor():
    """Create DirectiveProcessor with vocabulary."""
    dp = DirectiveProcessor()

    # Add BUZZ words
    dp.process(Form(Atom("BUZZ"), [
        Atom("A"), Atom("AN"), Atom("THE"), Atom("IS"), Atom("AND")
    ]))

    # Add direction synonyms
    dp.process(Form(Atom("SYNONYM"), [Atom("NORTH"), Atom("N")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("SOUTH"), Atom("S")]))

    # Add preposition synonyms
    dp.process(Form(Atom("SYNONYM"), [Atom("WITH"), Atom("USING")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("IN"), Atom("INTO")]))

    # Add directions
    dp.process(Form(Atom("DIRECTIONS"), [
        Atom("NORTH"), Atom("EAST"), Atom("WEST"), Atom("SOUTH"),
        Atom("UP"), Atom("DOWN"), Atom("IN"), Atom("OUT")
    ]))

    # Add SYNTAX entries
    dp.process(Form(Atom("SYNTAX"), [
        Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("DROP"), Atom("OBJECT"), Atom("="), Atom("V-DROP")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("QUIT"), Atom("="), Atom("V-QUIT")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("LOOK"), Atom("="), Atom("V-LOOK")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("PUT"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
        Atom("="), Atom("V-PUT")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("CUT"), Atom("OBJECT"), Atom("WITH"), Atom("OBJECT"),
        Atom("="), Atom("V-CUT")
    ]))

    return dp


@pytest.fixture
def lexer(processor):
    """Create CommandLexer."""
    return CommandLexer(processor)


@pytest.fixture
def parser(processor):
    """Create CommandParser."""
    return CommandParser(processor)


class TestBasicParsing:
    """Tests for basic command parsing (Task 5.6)."""

    def test_parse_verb_only(self, parser, lexer):
        """Parse verb-only command."""
        tokens = lexer.tokenize("quit")
        cmd = parser.parse(tokens)
        assert cmd.verb == "QUIT"
        assert len(cmd.noun_phrases) == 0
        assert cmd.preposition is None

    def test_parse_verb_object(self, parser, lexer):
        """Parse VERB OBJECT command."""
        tokens = lexer.tokenize("take lamp")
        cmd = parser.parse(tokens)
        assert cmd.verb == "TAKE"
        assert len(cmd.noun_phrases) == 1
        assert cmd.noun_phrases[0].noun == "LAMP"

    def test_parse_direction_alone(self, parser, lexer):
        """Parse direction as movement command."""
        tokens = lexer.tokenize("north")
        cmd = parser.parse(tokens)
        assert cmd.verb == "WALK"
        assert cmd.direction == "NORTH"

    def test_parse_direction_abbreviation(self, parser, lexer):
        """Parse direction abbreviation."""
        tokens = lexer.tokenize("n")
        cmd = parser.parse(tokens)
        assert cmd.verb == "WALK"
        assert cmd.direction == "NORTH"

    def test_parse_look(self, parser, lexer):
        """Parse LOOK command."""
        tokens = lexer.tokenize("look")
        cmd = parser.parse(tokens)
        assert cmd.verb == "LOOK"
        assert cmd.object_count == 0


class TestNounPhraseExtraction:
    """Tests for noun phrase extraction (Task 5.7)."""

    def test_parse_adjective_noun(self, parser, lexer):
        """Parse adjective + noun."""
        tokens = lexer.tokenize("take brass lamp")
        cmd = parser.parse(tokens)
        assert len(cmd.noun_phrases) == 1
        assert cmd.noun_phrases[0].adjectives == ["BRASS"]
        assert cmd.noun_phrases[0].noun == "LAMP"

    def test_parse_multiple_adjectives(self, parser, lexer):
        """Parse multiple adjectives before noun."""
        tokens = lexer.tokenize("take small brass lamp")
        cmd = parser.parse(tokens)
        assert cmd.noun_phrases[0].adjectives == ["SMALL", "BRASS"]
        assert cmd.noun_phrases[0].noun == "LAMP"

    def test_parse_preposition_separates_objects(self, parser, lexer):
        """Preposition separates two noun phrases."""
        tokens = lexer.tokenize("put lamp in case")
        cmd = parser.parse(tokens)
        assert len(cmd.noun_phrases) == 2
        assert cmd.noun_phrases[0].noun == "LAMP"
        assert cmd.preposition == "IN"
        assert cmd.noun_phrases[1].noun == "CASE"

    def test_parse_with_preposition(self, parser, lexer):
        """Parse command with WITH preposition."""
        tokens = lexer.tokenize("cut rope with knife")
        cmd = parser.parse(tokens)
        assert len(cmd.noun_phrases) == 2
        assert cmd.noun_phrases[0].noun == "ROPE"
        assert cmd.preposition == "WITH"
        assert cmd.noun_phrases[1].noun == "KNIFE"

    def test_parse_full_command_with_adjectives(self, parser, lexer):
        """Parse full command with adjectives on both objects."""
        tokens = lexer.tokenize("put brass lamp in wooden case")
        cmd = parser.parse(tokens)
        assert cmd.noun_phrases[0].adjectives == ["BRASS"]
        assert cmd.noun_phrases[0].noun == "LAMP"
        assert cmd.noun_phrases[1].adjectives == ["WOODEN"]
        assert cmd.noun_phrases[1].noun == "CASE"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_tokens(self, parser):
        """Empty token list returns None."""
        cmd = parser.parse([])
        assert cmd is None

    def test_noun_only_no_verb(self, parser):
        """Noun without verb returns partial parse."""
        tokens = [Token("LAMP", TokenType.UNKNOWN)]
        cmd = parser.parse(tokens)
        # Should have noun but no verb
        assert cmd is not None
        assert cmd.verb is None or len(cmd.noun_phrases) > 0

    def test_unknown_word_as_noun(self, parser, lexer):
        """Unknown words become nouns."""
        tokens = lexer.tokenize("take xyzzy")
        cmd = parser.parse(tokens)
        assert cmd.noun_phrases[0].noun == "XYZZY"

    def test_multiple_prepositions(self, parser, lexer):
        """Only first preposition used (for now)."""
        # This is edge case - real parser would handle differently
        tokens = lexer.tokenize("put lamp in case on table")
        cmd = parser.parse(tokens)
        # Should have first preposition
        assert cmd.preposition == "IN"


class TestObjectCount:
    """Tests for object_count property."""

    def test_zero_objects(self, parser, lexer):
        """Verb-only has 0 objects."""
        tokens = lexer.tokenize("quit")
        cmd = parser.parse(tokens)
        assert cmd.object_count == 0

    def test_one_object(self, parser, lexer):
        """TAKE X has 1 object."""
        tokens = lexer.tokenize("take lamp")
        cmd = parser.parse(tokens)
        assert cmd.object_count == 1

    def test_two_objects(self, parser, lexer):
        """PUT X IN Y has 2 objects."""
        tokens = lexer.tokenize("put lamp in case")
        cmd = parser.parse(tokens)
        assert cmd.object_count == 2
