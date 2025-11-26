"""Tests for CommandLexer (Tasks 5.2-5.5)."""
import pytest
from zil_interpreter.runtime.command_lexer import CommandLexer
from zil_interpreter.runtime.command_types import TokenType
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom


@pytest.fixture
def processor():
    """Create DirectiveProcessor with basic vocabulary."""
    dp = DirectiveProcessor()

    # Add BUZZ words
    dp.process(Form(Atom("BUZZ"), [
        Atom("A"), Atom("AN"), Atom("THE"), Atom("IS"),
        Atom("AND"), Atom("OF"), Atom("THEN")
    ]))

    # Add direction synonyms
    dp.process(Form(Atom("SYNONYM"), [Atom("NORTH"), Atom("N")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("SOUTH"), Atom("S")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("EAST"), Atom("E")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("WEST"), Atom("W")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("UP"), Atom("U")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("DOWN"), Atom("D")]))

    # Add preposition synonyms
    dp.process(Form(Atom("SYNONYM"), [Atom("WITH"), Atom("USING"), Atom("THRU")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("IN"), Atom("INSIDE"), Atom("INTO")]))

    # Add directions
    dp.process(Form(Atom("DIRECTIONS"), [
        Atom("NORTH"), Atom("EAST"), Atom("WEST"), Atom("SOUTH"),
        Atom("NE"), Atom("NW"), Atom("SE"), Atom("SW"),
        Atom("UP"), Atom("DOWN"), Atom("IN"), Atom("OUT")
    ]))

    # Add some SYNTAX entries for verb identification
    dp.process(Form(Atom("SYNTAX"), [
        Atom("TAKE"), Atom("OBJECT"), Atom("="), Atom("V-TAKE")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("QUIT"), Atom("="), Atom("V-QUIT")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("PUT"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
        Atom("="), Atom("V-PUT")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("DROP"), Atom("OBJECT"), Atom("="), Atom("V-DROP")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("LOOK"), Atom("="), Atom("V-LOOK")
    ]))

    return dp


@pytest.fixture
def lexer(processor):
    """Create CommandLexer with processor."""
    return CommandLexer(processor)


class TestBasicTokenization:
    """Tests for basic tokenization (Task 5.2)."""

    def test_tokenize_single_word(self, lexer):
        """Tokenize single word."""
        tokens = lexer.tokenize("take")
        assert len(tokens) == 1
        assert tokens[0].word == "TAKE"

    def test_tokenize_multiple_words(self, lexer):
        """Tokenize multiple words."""
        tokens = lexer.tokenize("take brass lamp")
        assert len(tokens) == 3
        assert [t.word for t in tokens] == ["TAKE", "BRASS", "LAMP"]

    def test_handles_extra_whitespace(self, lexer):
        """Handle extra whitespace between words."""
        tokens = lexer.tokenize("take   lamp")
        assert len(tokens) == 2
        assert [t.word for t in tokens] == ["TAKE", "LAMP"]

    def test_strips_punctuation(self, lexer):
        """Strip trailing punctuation."""
        tokens = lexer.tokenize("take lamp.")
        assert tokens[-1].word == "LAMP"

    def test_handles_comma(self, lexer):
        """Handle commas in input."""
        tokens = lexer.tokenize("take lamp, then drop it")
        # Should remove commas
        assert "," not in [t.word for t in tokens]

    def test_normalizes_to_uppercase(self, lexer):
        """Convert all tokens to uppercase."""
        tokens = lexer.tokenize("Take LAMP")
        assert all(t.word == t.word.upper() for t in tokens)

    def test_empty_input(self, lexer):
        """Empty input returns empty list."""
        tokens = lexer.tokenize("")
        assert tokens == []

    def test_whitespace_only(self, lexer):
        """Whitespace only returns empty list."""
        tokens = lexer.tokenize("   ")
        assert tokens == []


class TestBuzzWordFiltering:
    """Tests for BUZZ word filtering (Task 5.3)."""

    def test_filters_the(self, lexer):
        """Filter 'the' from input."""
        tokens = lexer.tokenize("take the lamp")
        words = [t.word for t in tokens]
        assert "THE" not in words
        assert "TAKE" in words
        assert "LAMP" in words

    def test_filters_a_and_an(self, lexer):
        """Filter 'a' and 'an' from input."""
        tokens = lexer.tokenize("take a lamp and an apple")
        words = [t.word for t in tokens]
        assert "A" not in words
        assert "AN" not in words

    def test_filters_multiple_buzz_words(self, lexer):
        """Filter all BUZZ words."""
        tokens = lexer.tokenize("put the brass lamp in the wooden case")
        words = [t.word for t in tokens]
        assert words == ["PUT", "BRASS", "LAMP", "IN", "WOODEN", "CASE"]

    def test_preserves_non_buzz_words(self, lexer):
        """Preserve words not in BUZZ list."""
        tokens = lexer.tokenize("quit")
        assert len(tokens) == 1
        assert tokens[0].word == "QUIT"


class TestSynonymResolution:
    """Tests for SYNONYM resolution (Task 5.4)."""

    def test_resolves_direction_n(self, lexer):
        """Resolve N to NORTH."""
        tokens = lexer.tokenize("n")
        assert tokens[0].word == "NORTH"

    def test_resolves_direction_s(self, lexer):
        """Resolve S to SOUTH."""
        tokens = lexer.tokenize("s")
        assert tokens[0].word == "SOUTH"

    def test_resolves_preposition_using(self, lexer):
        """Resolve USING to WITH."""
        tokens = lexer.tokenize("cut rope using knife")
        words = [t.word for t in tokens]
        assert "WITH" in words
        assert "USING" not in words

    def test_resolves_preposition_into(self, lexer):
        """Resolve INTO to IN."""
        tokens = lexer.tokenize("put lamp into case")
        words = [t.word for t in tokens]
        assert "IN" in words
        assert "INTO" not in words

    def test_preserves_unknown_words(self, lexer):
        """Unknown words stay unchanged."""
        tokens = lexer.tokenize("xyzzy")
        assert tokens[0].word == "XYZZY"

    def test_synonym_resolution_case_insensitive(self, lexer):
        """Synonym resolution is case-insensitive."""
        tokens = lexer.tokenize("N")
        assert tokens[0].word == "NORTH"


class TestTokenTypeClassification:
    """Tests for token type classification (Task 5.5)."""

    def test_identifies_direction(self, lexer):
        """Identify direction tokens."""
        tokens = lexer.tokenize("north")
        assert tokens[0].type == TokenType.DIRECTION

    def test_identifies_verb(self, lexer):
        """Identify verb tokens (has SYNTAX entry)."""
        tokens = lexer.tokenize("take lamp")
        assert tokens[0].type == TokenType.VERB

    def test_identifies_preposition_in(self, lexer):
        """Identify IN as preposition."""
        tokens = lexer.tokenize("put lamp in case")
        # Find the IN token
        in_token = next(t for t in tokens if t.word == "IN")
        assert in_token.type == TokenType.PREPOSITION

    def test_identifies_preposition_with(self, lexer):
        """Identify WITH as preposition."""
        tokens = lexer.tokenize("cut rope with knife")
        with_token = next(t for t in tokens if t.word == "WITH")
        assert with_token.type == TokenType.PREPOSITION

    def test_non_verb_first_word(self, lexer):
        """Non-verb first word is UNKNOWN or NOUN."""
        tokens = lexer.tokenize("lamp")
        # Single word that's not a verb/direction
        assert tokens[0].type in (TokenType.UNKNOWN, TokenType.NOUN)

    def test_direction_only_command(self, lexer):
        """Direction alone has DIRECTION type."""
        tokens = lexer.tokenize("south")
        assert tokens[0].type == TokenType.DIRECTION

    def test_adjective_before_noun(self, lexer):
        """Words between verb and known object are adjectives/nouns."""
        tokens = lexer.tokenize("take brass lamp")
        # BRASS should be ADJECTIVE or UNKNOWN (parser will figure it out)
        assert tokens[1].type in (TokenType.ADJECTIVE, TokenType.UNKNOWN, TokenType.NOUN)


class TestComplexInputs:
    """Tests for complex command inputs."""

    def test_full_two_object_command(self, lexer):
        """Parse full PUT X IN Y command."""
        tokens = lexer.tokenize("put the brass lamp in the wooden case")
        words = [t.word for t in tokens]
        assert words == ["PUT", "BRASS", "LAMP", "IN", "WOODEN", "CASE"]

    def test_direction_abbreviation_in_command(self, lexer):
        """Direction abbreviation resolved in longer command."""
        tokens = lexer.tokenize("go n")
        words = [t.word for t in tokens]
        assert "NORTH" in words

    def test_multiple_buzz_and_synonyms(self, lexer):
        """Combine BUZZ filtering and SYNONYM resolution."""
        tokens = lexer.tokenize("using the n lamp")
        words = [t.word for t in tokens]
        # USING -> WITH, THE filtered, N -> NORTH
        assert "WITH" in words
        assert "THE" not in words
        assert "NORTH" in words
