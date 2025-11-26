"""Tests for command parsing data types (Task 5.1)."""
import pytest
from zil_interpreter.runtime.command_types import (
    Token, TokenType, NounPhrase, ParsedCommand, CommandResult
)


class TestTokenType:
    """Tests for TokenType enum."""

    def test_token_types_exist(self):
        """All required token types exist."""
        assert TokenType.VERB
        assert TokenType.NOUN
        assert TokenType.ADJECTIVE
        assert TokenType.PREPOSITION
        assert TokenType.DIRECTION
        assert TokenType.UNKNOWN


class TestToken:
    """Tests for Token dataclass."""

    def test_token_basic(self):
        """Token stores word and type."""
        token = Token("LAMP", TokenType.NOUN)
        assert token.word == "LAMP"
        assert token.type == TokenType.NOUN

    def test_token_defaults_to_unknown(self):
        """Token defaults to UNKNOWN type."""
        token = Token("XYZZY")
        assert token.type == TokenType.UNKNOWN

    def test_token_equality(self):
        """Tokens with same word and type are equal."""
        t1 = Token("LAMP", TokenType.NOUN)
        t2 = Token("LAMP", TokenType.NOUN)
        assert t1 == t2

    def test_token_repr(self):
        """Token has readable repr."""
        token = Token("TAKE", TokenType.VERB)
        assert "TAKE" in repr(token)


class TestNounPhrase:
    """Tests for NounPhrase dataclass."""

    def test_noun_phrase_basic(self):
        """NounPhrase stores noun."""
        np = NounPhrase(noun="LAMP")
        assert np.noun == "LAMP"
        assert np.adjectives == []

    def test_noun_phrase_with_adjective(self):
        """NounPhrase stores adjectives."""
        np = NounPhrase(adjectives=["BRASS"], noun="LAMP")
        assert np.adjectives == ["BRASS"]
        assert np.noun == "LAMP"

    def test_noun_phrase_multiple_adjectives(self):
        """NounPhrase stores multiple adjectives."""
        np = NounPhrase(adjectives=["SMALL", "BRASS"], noun="LAMP")
        assert np.adjectives == ["SMALL", "BRASS"]

    def test_noun_phrase_equality(self):
        """NounPhrases with same content are equal."""
        np1 = NounPhrase(adjectives=["BRASS"], noun="LAMP")
        np2 = NounPhrase(adjectives=["BRASS"], noun="LAMP")
        assert np1 == np2


class TestParsedCommand:
    """Tests for ParsedCommand dataclass."""

    def test_parsed_command_verb_only(self):
        """ParsedCommand with just verb."""
        cmd = ParsedCommand(verb="QUIT")
        assert cmd.verb == "QUIT"
        assert cmd.noun_phrases == []
        assert cmd.preposition is None
        assert cmd.direction is None

    def test_parsed_command_with_object(self):
        """ParsedCommand with one noun phrase."""
        np = NounPhrase(noun="LAMP")
        cmd = ParsedCommand(verb="TAKE", noun_phrases=[np])
        assert cmd.verb == "TAKE"
        assert len(cmd.noun_phrases) == 1
        assert cmd.noun_phrases[0].noun == "LAMP"

    def test_parsed_command_with_preposition(self):
        """ParsedCommand with preposition and two objects."""
        np1 = NounPhrase(noun="LAMP")
        np2 = NounPhrase(noun="CASE")
        cmd = ParsedCommand(verb="PUT", noun_phrases=[np1, np2], preposition="IN")
        assert cmd.verb == "PUT"
        assert len(cmd.noun_phrases) == 2
        assert cmd.preposition == "IN"

    def test_parsed_command_direction(self):
        """ParsedCommand for direction movement."""
        cmd = ParsedCommand(verb="WALK", direction="NORTH")
        assert cmd.verb == "WALK"
        assert cmd.direction == "NORTH"

    def test_parsed_command_object_count(self):
        """object_count property works."""
        cmd = ParsedCommand(verb="QUIT")
        assert cmd.object_count == 0

        np = NounPhrase(noun="LAMP")
        cmd = ParsedCommand(verb="TAKE", noun_phrases=[np])
        assert cmd.object_count == 1


class TestCommandResult:
    """Tests for CommandResult dataclass."""

    def test_command_result_success(self):
        """CommandResult for successful command."""
        result = CommandResult(success=True, action="V-TAKE")
        assert result.success
        assert result.action == "V-TAKE"
        assert result.error is None

    def test_command_result_failure(self):
        """CommandResult for failed command."""
        result = CommandResult(success=False, error="I don't understand that.")
        assert not result.success
        assert result.error == "I don't understand that."
        assert result.action is None

    def test_command_result_with_objects(self):
        """CommandResult stores resolved objects."""
        result = CommandResult(
            success=True,
            action="V-TAKE",
            direct_object="LAMP",
            indirect_object="CASE"
        )
        assert result.direct_object == "LAMP"
        assert result.indirect_object == "CASE"
