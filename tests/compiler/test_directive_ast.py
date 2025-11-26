"""Tests for directive AST dataclasses."""
import pytest
from zil_interpreter.compiler.directives import (
    ConstantDef, GlobalDef, PropDef, DirectionsDef,
    SynonymDef, BuzzDef, SyntaxDef, ObjectConstraint
)


class TestDirectiveDataclasses:
    """Tests for directive AST representation."""

    def test_constant_def(self):
        """CONSTANT creates ConstantDef."""
        const = ConstantDef(name="M-ENTER", value=2)
        assert const.name == "M-ENTER"
        assert const.value == 2

    def test_constant_def_string_value(self):
        """CONSTANT can have string value."""
        const = ConstantDef(name="REESSION", value="0")
        assert const.name == "REESSION"
        assert const.value == "0"

    def test_global_def(self):
        """GLOBAL creates GlobalDef."""
        glob = GlobalDef(name="LUCKY", initial_value=True)
        assert glob.name == "LUCKY"
        assert glob.initial_value is True

    def test_global_def_number(self):
        """GLOBAL can have number value."""
        glob = GlobalDef(name="MATCH-COUNT", initial_value=6)
        assert glob.initial_value == 6

    def test_global_def_false(self):
        """GLOBAL can have false value."""
        glob = GlobalDef(name="RUG-MOVED", initial_value=False)
        assert glob.initial_value is False

    def test_propdef(self):
        """PROPDEF creates PropDef."""
        prop = PropDef(name="SIZE", default=5)
        assert prop.name == "SIZE"
        assert prop.default == 5

    def test_propdef_zero(self):
        """PROPDEF can have zero default."""
        prop = PropDef(name="CAPACITY", default=0)
        assert prop.default == 0

    def test_directions_def(self):
        """DIRECTIONS creates DirectionsDef."""
        dirs = DirectionsDef(directions=["NORTH", "SOUTH", "EAST", "WEST"])
        assert "NORTH" in dirs.directions
        assert len(dirs.directions) == 4

    def test_directions_def_all_zork(self):
        """DIRECTIONS can hold all Zork directions."""
        dirs = DirectionsDef(directions=[
            "NORTH", "EAST", "WEST", "SOUTH",
            "NE", "NW", "SE", "SW",
            "UP", "DOWN", "IN", "OUT", "LAND"
        ])
        assert len(dirs.directions) == 13

    def test_synonym_def(self):
        """SYNONYM creates SynonymDef."""
        syn = SynonymDef(primary="WITH", aliases=["USING", "THROUGH"])
        assert syn.primary == "WITH"
        assert "USING" in syn.aliases
        assert len(syn.aliases) == 2

    def test_synonym_def_direction(self):
        """SYNONYM works for direction abbreviations."""
        syn = SynonymDef(primary="NORTH", aliases=["N"])
        assert syn.primary == "NORTH"
        assert "N" in syn.aliases

    def test_buzz_def(self):
        """BUZZ creates BuzzDef."""
        buzz = BuzzDef(words=["A", "AN", "THE"])
        assert "THE" in buzz.words
        assert len(buzz.words) == 3

    def test_buzz_def_multiple(self):
        """BUZZ can hold many words."""
        buzz = BuzzDef(words=["A", "AN", "THE", "IS", "AND", "OF", "THEN"])
        assert len(buzz.words) == 7

    def test_object_constraint(self):
        """ObjectConstraint holds constraint info."""
        constraint = ObjectConstraint(
            position=1,
            constraints=["TAKEABLE", "HELD"]
        )
        assert constraint.position == 1
        assert "TAKEABLE" in constraint.constraints

    def test_object_constraint_empty(self):
        """ObjectConstraint can have no constraints."""
        constraint = ObjectConstraint(position=1)
        assert constraint.position == 1
        assert constraint.constraints == []

    def test_syntax_def_simple(self):
        """Simple SYNTAX creates SyntaxDef."""
        syntax = SyntaxDef(
            verb="QUIT",
            action="V-QUIT"
        )
        assert syntax.verb == "QUIT"
        assert syntax.action == "V-QUIT"
        assert syntax.objects == []
        assert syntax.prepositions == []
        assert syntax.preaction is None

    def test_syntax_def_with_object(self):
        """SYNTAX with OBJECT creates SyntaxDef."""
        syntax = SyntaxDef(
            verb="TAKE",
            action="V-TAKE",
            objects=[ObjectConstraint(position=1, constraints=["TAKEABLE"])],
            preaction="PRE-TAKE"
        )
        assert len(syntax.objects) == 1
        assert syntax.preaction == "PRE-TAKE"

    def test_syntax_def_with_two_objects(self):
        """SYNTAX with two OBJECTs and preposition."""
        syntax = SyntaxDef(
            verb="PUT",
            action="V-PUT",
            objects=[
                ObjectConstraint(position=1, constraints=["HELD"]),
                ObjectConstraint(position=2)
            ],
            prepositions=["IN"],
            preaction="PRE-PUT"
        )
        assert len(syntax.objects) == 2
        assert "IN" in syntax.prepositions
        assert syntax.preaction == "PRE-PUT"

    def test_syntax_def_multiple_prepositions(self):
        """SYNTAX can have multiple preposition options."""
        syntax = SyntaxDef(
            verb="DROP",
            action="V-DROP",
            objects=[ObjectConstraint(position=1)],
            prepositions=["IN", "ON", "DOWN"]
        )
        assert len(syntax.prepositions) == 3
