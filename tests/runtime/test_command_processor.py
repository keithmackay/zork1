"""Tests for CommandProcessor (Tasks 5.12-5.15)."""
import pytest
from zil_interpreter.runtime.command_processor import CommandProcessor
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject, ObjectFlag
from zil_interpreter.parser.ast_nodes import Form, Atom


@pytest.fixture
def processor():
    """Create DirectiveProcessor with vocabulary."""
    dp = DirectiveProcessor()

    # BUZZ words
    dp.process(Form(Atom("BUZZ"), [
        Atom("A"), Atom("AN"), Atom("THE"), Atom("IS"), Atom("AND")
    ]))

    # Direction synonyms
    dp.process(Form(Atom("SYNONYM"), [Atom("NORTH"), Atom("N")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("SOUTH"), Atom("S")]))

    # Preposition synonyms
    dp.process(Form(Atom("SYNONYM"), [Atom("WITH"), Atom("USING")]))
    dp.process(Form(Atom("SYNONYM"), [Atom("IN"), Atom("INTO")]))

    # Directions
    dp.process(Form(Atom("DIRECTIONS"), [
        Atom("NORTH"), Atom("EAST"), Atom("WEST"), Atom("SOUTH"),
        Atom("UP"), Atom("DOWN"), Atom("IN"), Atom("OUT")
    ]))

    # SYNTAX entries
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
        Atom("INVENTORY"), Atom("="), Atom("V-INVENTORY")
    ]))
    dp.process(Form(Atom("SYNTAX"), [
        Atom("PUT"), Atom("OBJECT"), Atom("IN"), Atom("OBJECT"),
        Atom("="), Atom("V-PUT")
    ]))

    return dp


@pytest.fixture
def world():
    """Create world with test objects."""
    world = WorldState()

    # Room
    room = GameObject("LIVING-ROOM", description="Living Room")
    world.add_object(room)
    world.set_current_room(room)

    # Player
    player = GameObject("PLAYER", description="Player")
    player.move_to(room)
    world.add_object(player)
    world.set_global("WINNER", player)

    # Objects
    lamp = GameObject(
        "LAMP",
        description="brass lamp",
        synonyms=["LAMP", "LANTERN"]
    )
    lamp.adjectives = ["BRASS"]
    lamp.move_to(room)
    world.add_object(lamp)

    case = GameObject(
        "CASE",
        description="wooden case",
        synonyms=["CASE", "BOX"]
    )
    case.adjectives = ["WOODEN"]
    case.set_flag(ObjectFlag.CONTAINER)
    case.set_flag(ObjectFlag.OPEN)
    case.move_to(room)
    world.add_object(case)

    return world


@pytest.fixture
def cmd_processor(processor, world):
    """Create CommandProcessor."""
    return CommandProcessor(processor, world)


class TestParserStateBinding:
    """Tests for PRSA/PRSO/PRSI binding (Task 5.12)."""

    def test_sets_prsa(self, cmd_processor, world):
        """Sets PRSA to action routine name."""
        result = cmd_processor.process("quit")
        assert result.success
        assert world.get_global("PRSA") == "V-QUIT"

    def test_sets_prso(self, cmd_processor, world):
        """Sets PRSO to direct object."""
        result = cmd_processor.process("take lamp")
        assert result.success
        assert world.get_global("PRSO") is not None
        assert world.get_global("PRSO").name == "LAMP"

    def test_sets_prsi(self, cmd_processor, world):
        """Sets PRSI to indirect object."""
        result = cmd_processor.process("put lamp in case")
        assert result.success
        prso = world.get_global("PRSO")
        prsi = world.get_global("PRSI")
        assert prso is not None
        assert prsi is not None
        assert prso.name == "LAMP"
        assert prsi.name == "CASE"

    def test_direction_sets_p_dir(self, cmd_processor, world):
        """Direction command sets P-DIR."""
        result = cmd_processor.process("north")
        assert result.success
        assert world.get_global("P-DIR") == "NORTH"


class TestFullPipeline:
    """Tests for full command processing (Task 5.13)."""

    def test_simple_verb_command(self, cmd_processor, world):
        """Process simple verb-only command."""
        result = cmd_processor.process("quit")
        assert result.success
        assert result.action == "V-QUIT"

    def test_verb_object_command(self, cmd_processor, world):
        """Process VERB OBJECT command."""
        result = cmd_processor.process("take lamp")
        assert result.success
        assert result.action == "V-TAKE"
        assert result.direct_object.name == "LAMP"

    def test_two_object_command(self, cmd_processor, world):
        """Process VERB OBJ PREP OBJ command."""
        result = cmd_processor.process("put lamp in case")
        assert result.success
        assert result.action == "V-PUT"
        assert result.direct_object.name == "LAMP"
        assert result.indirect_object.name == "CASE"

    def test_direction_command(self, cmd_processor, world):
        """Process direction command."""
        result = cmd_processor.process("north")
        assert result.success
        assert result.action == "V-WALK"

    def test_direction_abbreviation(self, cmd_processor, world):
        """Process direction abbreviation."""
        result = cmd_processor.process("n")
        assert result.success
        assert world.get_global("P-DIR") == "NORTH"

    def test_look_command(self, cmd_processor, world):
        """Process LOOK command."""
        result = cmd_processor.process("look")
        assert result.success
        assert result.action == "V-LOOK"


class TestErrorHandling:
    """Tests for error handling (Tasks 5.14-5.15)."""

    def test_unknown_verb(self, cmd_processor):
        """Unknown verb returns error."""
        result = cmd_processor.process("xyzzy")
        assert not result.success
        assert result.error is not None

    def test_no_matching_syntax(self, cmd_processor):
        """Syntax mismatch returns error."""
        # QUIT takes no objects
        result = cmd_processor.process("quit lamp")
        assert not result.success

    def test_object_not_found(self, cmd_processor):
        """Missing object returns error."""
        result = cmd_processor.process("take dinosaur")
        assert not result.success
        assert "can't see" in result.error.lower() or "don't see" in result.error.lower()

    def test_object_not_accessible(self, cmd_processor, world):
        """Inaccessible object returns error."""
        # Move lamp to another room
        other_room = GameObject("KITCHEN")
        world.add_object(other_room)
        lamp = world.get_object("LAMP")
        lamp.move_to(other_room)

        result = cmd_processor.process("take lamp")
        assert not result.success

    def test_empty_input(self, cmd_processor):
        """Empty input returns error."""
        result = cmd_processor.process("")
        assert not result.success

    def test_whitespace_only(self, cmd_processor):
        """Whitespace only returns error."""
        result = cmd_processor.process("   ")
        assert not result.success


class TestWithAdjectives:
    """Tests for commands with adjectives."""

    def test_adjective_in_command(self, cmd_processor, world):
        """Process command with adjective."""
        result = cmd_processor.process("take brass lamp")
        assert result.success
        assert result.direct_object.name == "LAMP"

    def test_wrong_adjective_fails(self, cmd_processor, world):
        """Wrong adjective fails to match."""
        result = cmd_processor.process("take wooden lamp")
        # Should fail since there's no wooden lamp
        assert not result.success
