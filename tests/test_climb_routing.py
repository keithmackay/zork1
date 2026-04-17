"""Tests for CLIMB verb routing — plain 'climb' should map to V-CLIMB-UP."""

import pytest
from zil_interpreter.engine.command_parser import CommandParser
from zil_interpreter.world.world_state import WorldState
from unittest.mock import MagicMock


class TestClimbRouting:
    """Verify CLIMB verb mappings in CommandParser.VERBS."""

    def test_climb_plain_maps_to_climb_up(self):
        """Plain 'climb' must map to CLIMB-UP, not CLIMB-FOO or V-CLIMB."""
        verbs = CommandParser.VERBS
        assert "CLIMB-UP" in verbs, "CLIMB-UP must be in VERBS table"
        assert "climb" in verbs["CLIMB-UP"], (
            "Plain 'climb' must be in CLIMB-UP synonyms so it routes to V-CLIMB-UP"
        )

    def test_no_climb_foo_key(self):
        """CLIMB-FOO (routes to nonexistent V-CLIMB-FOO) must not exist."""
        verbs = CommandParser.VERBS
        assert "CLIMB-FOO" not in verbs, (
            "CLIMB-FOO is a placeholder that maps to nonexistent V-CLIMB-FOO and must be removed"
        )

    def test_climb_up_phrase_still_works(self):
        """'climb up' phrase must still map to CLIMB-UP."""
        verbs = CommandParser.VERBS
        assert "climb up" in verbs["CLIMB-UP"]

    def test_climb_down_still_works(self):
        """'climb down' must still map to CLIMB-DOWN."""
        verbs = CommandParser.VERBS
        assert "CLIMB-DOWN" in verbs
        assert "climb down" in verbs["CLIMB-DOWN"]

    def test_climb_on_still_works(self):
        """'climb on' / 'sit on' must still map to CLIMB-ON."""
        verbs = CommandParser.VERBS
        assert "CLIMB-ON" in verbs
        assert "climb on" in verbs["CLIMB-ON"]

    def test_parse_climb_returns_climb_up(self):
        """CommandParser.parse('climb') should return verb CLIMB-UP."""
        world = MagicMock(spec=WorldState)
        world.find_object_by_word.return_value = None
        parser = CommandParser(world)
        result = parser.parse("climb")
        assert result is not None, "parse('climb') returned None"
        assert result["verb"] == "CLIMB-UP", (
            f"Expected verb CLIMB-UP, got {result['verb']!r}"
        )
