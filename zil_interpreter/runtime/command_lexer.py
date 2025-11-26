"""Command lexer for player input tokenization."""
import re
from typing import List, Set
from .command_types import Token, TokenType
from ..compiler.directive_processor import DirectiveProcessor


# Standard prepositions
PREPOSITIONS: Set[str] = {
    "IN", "INTO", "ON", "ONTO", "WITH", "USING", "TO", "FROM",
    "AT", "FOR", "UNDER", "THROUGH", "THRU", "ABOUT", "OVER",
    "BEHIND", "BESIDE", "BETWEEN", "OFF", "OUT", "UP", "DOWN"
}


class CommandLexer:
    """Tokenize player input using compiled vocabulary tables."""

    def __init__(self, processor: DirectiveProcessor):
        """Initialize lexer with directive processor.

        Args:
            processor: DirectiveProcessor with vocabulary tables
        """
        self._processor = processor

    def tokenize(self, input_text: str) -> List[Token]:
        """Tokenize input string.

        1. Split on whitespace
        2. Strip punctuation
        3. Filter BUZZ words
        4. Apply SYNONYM mappings
        5. Classify token types

        Args:
            input_text: Player input string

        Returns:
            List of Token objects
        """
        if not input_text or not input_text.strip():
            return []

        # Split on whitespace and strip punctuation
        words = self._split_and_clean(input_text)

        # Process each word
        tokens = []
        is_first = True

        for word in words:
            # Skip empty words
            if not word:
                continue

            # Normalize to uppercase
            word = word.upper()

            # Filter BUZZ words
            if self._processor.is_buzz_word(word):
                continue

            # Apply SYNONYM mapping
            word = self._processor.get_canonical(word)

            # Classify token type
            token_type = self._classify_token(word, is_first)

            tokens.append(Token(word, token_type))
            is_first = False

        return tokens

    def _split_and_clean(self, input_text: str) -> List[str]:
        """Split input and clean punctuation.

        Args:
            input_text: Raw input string

        Returns:
            List of cleaned words
        """
        # Remove common punctuation
        cleaned = re.sub(r'[.,!?"\']', ' ', input_text)

        # Split on whitespace
        return cleaned.split()

    def _classify_token(self, word: str, is_first: bool) -> TokenType:
        """Classify a token by type.

        Args:
            word: The word to classify (uppercase)
            is_first: Whether this is the first non-buzz word

        Returns:
            TokenType for this word
        """
        # Check if it's a direction (only at start of command)
        # Words like IN/OUT are both directions and prepositions
        if is_first and self._processor.is_direction(word):
            return TokenType.DIRECTION

        # Check if it's a preposition (when not first word)
        if not is_first and word in PREPOSITIONS:
            return TokenType.PREPOSITION

        # Check if it has SYNTAX entries (is a verb)
        if is_first and len(self._processor.syntax_table.lookup(word)) > 0:
            return TokenType.VERB

        # Direction-only words like NORTH/SOUTH when not first
        if self._processor.is_direction(word):
            return TokenType.DIRECTION

        # Default to UNKNOWN (parser will resolve to noun/adjective)
        return TokenType.UNKNOWN
