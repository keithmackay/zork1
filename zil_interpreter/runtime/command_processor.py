"""Command processor - orchestrates full command parsing pipeline."""
from typing import Optional
from .command_types import CommandResult, NounPhrase
from .command_lexer import CommandLexer
from .command_parser import CommandParser
from .object_resolver import ObjectResolver, DisambiguationNeeded
from ..compiler.directive_processor import DirectiveProcessor
from ..world.world_state import WorldState
from ..world.game_object import GameObject


class CommandProcessor:
    """Process player commands through full parsing pipeline."""

    def __init__(self, processor: DirectiveProcessor, world: WorldState):
        """Initialize command processor.

        Args:
            processor: DirectiveProcessor with vocabulary tables
            world: WorldState with game objects
        """
        self._processor = processor
        self._world = world
        self._lexer = CommandLexer(processor)
        self._parser = CommandParser(processor)
        self._resolver = ObjectResolver(world)

    def process(self, input_text: str) -> CommandResult:
        """Process a player command.

        Args:
            input_text: Raw player input

        Returns:
            CommandResult with success/failure and resolved objects
        """
        # Handle empty input
        if not input_text or not input_text.strip():
            return CommandResult(
                success=False,
                error="I beg your pardon?"
            )

        # Tokenize
        tokens = self._lexer.tokenize(input_text)

        if not tokens:
            return CommandResult(
                success=False,
                error="I beg your pardon?"
            )

        # Parse
        parsed = self._parser.parse(tokens)

        if parsed is None:
            return CommandResult(
                success=False,
                error="I don't understand that."
            )

        # Handle direction command
        if parsed.direction:
            return self._handle_direction(parsed.direction)

        # No verb found
        if not parsed.verb:
            return CommandResult(
                success=False,
                error="I don't understand that sentence."
            )

        # Match syntax
        syntax_entry = self._processor.syntax_table.match(
            parsed.verb,
            parsed.object_count,
            parsed.preposition
        )

        if syntax_entry is None:
            return CommandResult(
                success=False,
                error=f"I don't understand how to use '{parsed.verb.lower()}' that way."
            )

        # Resolve objects
        current_room = self._world.get_current_room()
        direct_object = None
        indirect_object = None

        try:
            if len(parsed.noun_phrases) >= 1:
                direct_object = self._resolver.resolve(
                    parsed.noun_phrases[0],
                    current_room
                )
                if direct_object is None:
                    noun = parsed.noun_phrases[0].noun.lower()
                    return CommandResult(
                        success=False,
                        error=f"I don't see any {noun} here."
                    )

            if len(parsed.noun_phrases) >= 2:
                indirect_object = self._resolver.resolve(
                    parsed.noun_phrases[1],
                    current_room
                )
                if indirect_object is None:
                    noun = parsed.noun_phrases[1].noun.lower()
                    return CommandResult(
                        success=False,
                        error=f"I don't see any {noun} here."
                    )

        except DisambiguationNeeded as e:
            names = [c.description or c.name for c in e.candidates]
            return CommandResult(
                success=False,
                error=f"Which do you mean: {', '.join(names)}?"
            )

        # Set parser state
        self._world.set_global("PRSA", syntax_entry.action)
        self._world.set_global("PRSO", direct_object)
        self._world.set_global("PRSI", indirect_object)

        return CommandResult(
            success=True,
            action=syntax_entry.action,
            direct_object=direct_object,
            indirect_object=indirect_object
        )

    def _handle_direction(self, direction: str) -> CommandResult:
        """Handle direction movement command.

        Args:
            direction: Direction name (NORTH, SOUTH, etc.)

        Returns:
            CommandResult for movement
        """
        self._world.set_global("PRSA", "V-WALK")
        self._world.set_global("P-DIR", direction)
        self._world.set_global("PRSO", None)
        self._world.set_global("PRSI", None)

        return CommandResult(
            success=True,
            action="V-WALK"
        )
