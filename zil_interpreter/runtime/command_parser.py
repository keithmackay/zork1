"""Command parser for structured command extraction."""
from typing import List, Optional
from .command_types import Token, TokenType, NounPhrase, ParsedCommand
from ..compiler.directive_processor import DirectiveProcessor


class CommandParser:
    """Parse token stream into structured ParsedCommand."""

    def __init__(self, processor: DirectiveProcessor):
        """Initialize parser with directive processor.

        Args:
            processor: DirectiveProcessor with vocabulary tables
        """
        self._processor = processor

    def parse(self, tokens: List[Token]) -> Optional[ParsedCommand]:
        """Parse token stream into ParsedCommand.

        Args:
            tokens: List of Token objects from lexer

        Returns:
            ParsedCommand or None if empty
        """
        if not tokens:
            return None

        # Check for direction-only command
        if len(tokens) == 1 and tokens[0].type == TokenType.DIRECTION:
            return ParsedCommand(
                verb="WALK",
                direction=tokens[0].word
            )

        # Extract verb
        verb = None
        start_idx = 0

        if tokens[0].type == TokenType.VERB:
            verb = tokens[0].word
            start_idx = 1
        elif tokens[0].type == TokenType.DIRECTION:
            # Direction at start is movement
            return ParsedCommand(
                verb="WALK",
                direction=tokens[0].word
            )

        # Parse remaining tokens for noun phrases
        noun_phrases, preposition = self._extract_noun_phrases(tokens[start_idx:])

        return ParsedCommand(
            verb=verb,
            noun_phrases=noun_phrases,
            preposition=preposition
        )

    def _extract_noun_phrases(
        self,
        tokens: List[Token]
    ) -> tuple[List[NounPhrase], Optional[str]]:
        """Extract noun phrases from token stream.

        Args:
            tokens: Tokens after verb

        Returns:
            Tuple of (noun_phrases, preposition)
        """
        noun_phrases = []
        preposition = None
        current_adjectives: List[str] = []

        for token in tokens:
            if token.type == TokenType.PREPOSITION:
                # Save current phrase if any
                if current_adjectives:
                    # Last adjective is actually the noun
                    noun = current_adjectives.pop()
                    noun_phrases.append(NounPhrase(
                        noun=noun,
                        adjectives=current_adjectives.copy()
                    ))
                    current_adjectives = []

                # Record first preposition
                if preposition is None:
                    preposition = token.word

            elif token.type == TokenType.DIRECTION:
                # Direction as object (e.g., "go north")
                if current_adjectives:
                    noun = current_adjectives.pop()
                    noun_phrases.append(NounPhrase(
                        noun=noun,
                        adjectives=current_adjectives.copy()
                    ))
                    current_adjectives = []
                noun_phrases.append(NounPhrase(noun=token.word))

            else:
                # Accumulate as potential adjective/noun
                current_adjectives.append(token.word)

        # Finish any remaining phrase
        if current_adjectives:
            noun = current_adjectives.pop()
            noun_phrases.append(NounPhrase(
                noun=noun,
                adjectives=current_adjectives.copy()
            ))

        return noun_phrases, preposition
