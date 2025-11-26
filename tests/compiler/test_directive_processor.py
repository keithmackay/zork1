"""Tests for DirectiveProcessor - Tasks 4.2-4.6."""
import pytest
from zil_interpreter.compiler.directive_processor import DirectiveProcessor
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String


class TestConstantProcessor:
    """Tests for CONSTANT directive processing (Task 4.2)."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_constant_number(self, processor):
        """Process CONSTANT with number value."""
        # <CONSTANT M-ENTER 2>
        form = Form(Atom("CONSTANT"), [Atom("M-ENTER"), Number(2)])
        processor.process(form)
        assert processor.constants["M-ENTER"] == 2

    def test_constant_string(self, processor):
        """Process CONSTANT with string value."""
        # <CONSTANT REESSION "0">
        form = Form(Atom("CONSTANT"), [Atom("REESSION"), String("0")])
        processor.process(form)
        assert processor.constants["REESSION"] == "0"

    def test_constant_atom_value(self, processor):
        """Process CONSTANT with atom value."""
        # <CONSTANT ZORK-NUMBER 1>
        form = Form(Atom("CONSTANT"), [Atom("ZORK-NUMBER"), Number(1)])
        processor.process(form)
        assert processor.constants["ZORK-NUMBER"] == 1

    def test_constant_case_insensitive(self, processor):
        """CONSTANT lookup is case-insensitive."""
        form = Form(Atom("CONSTANT"), [Atom("FOO"), Number(42)])
        processor.process(form)
        assert processor.get_constant("foo") == 42
        assert processor.get_constant("FOO") == 42

    def test_get_constant_unknown(self, processor):
        """Unknown constant returns None."""
        assert processor.get_constant("UNKNOWN") is None

    def test_multiple_constants(self, processor):
        """Process multiple CONSTANT definitions."""
        processor.process(Form(Atom("CONSTANT"), [Atom("A"), Number(1)]))
        processor.process(Form(Atom("CONSTANT"), [Atom("B"), Number(2)]))
        processor.process(Form(Atom("CONSTANT"), [Atom("C"), Number(3)]))
        assert len(processor.constants) == 3


class TestGlobalProcessor:
    """Tests for GLOBAL directive processing (Task 4.3)."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_global_with_number(self, processor):
        """Process GLOBAL with number value."""
        # <GLOBAL MATCH-COUNT 6>
        form = Form(Atom("GLOBAL"), [Atom("MATCH-COUNT"), Number(6)])
        processor.process(form)
        assert processor.globals["MATCH-COUNT"] == 6

    def test_global_with_false(self, processor):
        """Process GLOBAL with false (<>)."""
        # <GLOBAL RUG-MOVED <>>
        # Empty form represents false
        form = Form(Atom("GLOBAL"), [Atom("RUG-MOVED"), Form(Atom("<>"), [])])
        processor.process(form)
        assert processor.globals["RUG-MOVED"] is False

    def test_global_with_empty_form(self, processor):
        """Process GLOBAL with empty form as false."""
        # Another way to represent false
        empty_form = Form(Atom(""), [])
        form = Form(Atom("GLOBAL"), [Atom("FLAG"), empty_form])
        processor.process(form)
        assert processor.globals["FLAG"] is False

    def test_global_with_true(self, processor):
        """Process GLOBAL with T (true)."""
        # <GLOBAL LUCKY T>
        form = Form(Atom("GLOBAL"), [Atom("LUCKY"), Atom("T")])
        processor.process(form)
        assert processor.globals["LUCKY"] is True

    def test_global_with_table(self, processor):
        """Process GLOBAL with LTABLE value."""
        # <GLOBAL LOUD-RUNS <LTABLE 0 ROOM1 ROOM2>>
        ltable = Form(Atom("LTABLE"), [Number(0), Atom("ROOM1"), Atom("ROOM2")])
        form = Form(Atom("GLOBAL"), [Atom("LOUD-RUNS"), ltable])
        processor.process(form)
        # Store as form for later evaluation
        assert "LOUD-RUNS" in processor.globals

    def test_global_count(self, processor):
        """Process multiple GLOBAL definitions."""
        processor.process(Form(Atom("GLOBAL"), [Atom("A"), Number(1)]))
        processor.process(Form(Atom("GLOBAL"), [Atom("B"), Number(2)]))
        assert len(processor.globals) == 2

    def test_global_case_insensitive(self, processor):
        """GLOBAL lookup is case-insensitive."""
        form = Form(Atom("GLOBAL"), [Atom("FOO"), Number(42)])
        processor.process(form)
        assert processor.get_global("foo") == 42
        assert processor.get_global("FOO") == 42


class TestPropdefProcessor:
    """Tests for PROPDEF directive processing (Task 4.4)."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_propdef_size(self, processor):
        """Process PROPDEF SIZE 5."""
        form = Form(Atom("PROPDEF"), [Atom("SIZE"), Number(5)])
        processor.process(form)
        assert processor.property_defaults["SIZE"] == 5

    def test_propdef_capacity(self, processor):
        """Process PROPDEF CAPACITY 0."""
        form = Form(Atom("PROPDEF"), [Atom("CAPACITY"), Number(0)])
        processor.process(form)
        assert processor.property_defaults["CAPACITY"] == 0

    def test_all_zork_propdefs(self, processor):
        """Process all Zork I PROPDEFs."""
        processor.process(Form(Atom("PROPDEF"), [Atom("SIZE"), Number(5)]))
        processor.process(Form(Atom("PROPDEF"), [Atom("CAPACITY"), Number(0)]))
        processor.process(Form(Atom("PROPDEF"), [Atom("VALUE"), Number(0)]))
        processor.process(Form(Atom("PROPDEF"), [Atom("TVALUE"), Number(0)]))
        assert len(processor.property_defaults) == 4

    def test_get_property_default(self, processor):
        """Get default property value."""
        processor.process(Form(Atom("PROPDEF"), [Atom("SIZE"), Number(5)]))
        assert processor.get_property_default("SIZE") == 5
        assert processor.get_property_default("UNKNOWN") is None


class TestDirectionsProcessor:
    """Tests for DIRECTIONS directive processing (Task 4.5)."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_directions_basic(self, processor):
        """Process DIRECTIONS with all 13 Zork directions."""
        # <DIRECTIONS NORTH EAST WEST SOUTH NE NW SE SW UP DOWN IN OUT LAND>
        form = Form(Atom("DIRECTIONS"), [
            Atom("NORTH"), Atom("EAST"), Atom("WEST"), Atom("SOUTH"),
            Atom("NE"), Atom("NW"), Atom("SE"), Atom("SW"),
            Atom("UP"), Atom("DOWN"), Atom("IN"), Atom("OUT"), Atom("LAND")
        ])
        processor.process(form)
        assert len(processor.directions) == 13
        assert "NORTH" in processor.directions
        assert "LAND" in processor.directions

    def test_is_direction(self, processor):
        """Check if word is a direction."""
        form = Form(Atom("DIRECTIONS"), [Atom("NORTH"), Atom("SOUTH")])
        processor.process(form)
        assert processor.is_direction("NORTH")
        assert processor.is_direction("north")  # case-insensitive
        assert not processor.is_direction("TAKE")

    def test_direction_index(self, processor):
        """Get index of direction (for property lookup)."""
        form = Form(Atom("DIRECTIONS"), [
            Atom("NORTH"), Atom("EAST"), Atom("WEST"), Atom("SOUTH")
        ])
        processor.process(form)
        assert processor.direction_index("NORTH") == 0
        assert processor.direction_index("SOUTH") == 3
        assert processor.direction_index("UNKNOWN") == -1


class TestBuzzProcessor:
    """Tests for BUZZ (noise word) processing (Task 4.6)."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_buzz_words(self, processor):
        """Process BUZZ directive."""
        # <BUZZ A AN THE IS AND OF THEN>
        form = Form(Atom("BUZZ"), [
            Atom("A"), Atom("AN"), Atom("THE"), Atom("IS"),
            Atom("AND"), Atom("OF"), Atom("THEN")
        ])
        processor.process(form)
        assert processor.is_buzz_word("THE")
        assert processor.is_buzz_word("the")  # case-insensitive
        assert not processor.is_buzz_word("TAKE")

    def test_multiple_buzz(self, processor):
        """Process multiple BUZZ directives."""
        processor.process(Form(Atom("BUZZ"), [Atom("AGAIN"), Atom("G")]))
        processor.process(Form(Atom("BUZZ"), [Atom("A"), Atom("AN"), Atom("THE")]))
        assert len(processor.buzz_words) == 5


class TestSynonymProcessor:
    """Tests for SYNONYM processing (Task 4.6)."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_synonym_basic(self, processor):
        """Process SYNONYM directive."""
        # <SYNONYM WITH USING THROUGH THRU>
        form = Form(Atom("SYNONYM"), [
            Atom("WITH"), Atom("USING"), Atom("THROUGH"), Atom("THRU")
        ])
        processor.process(form)
        assert processor.get_canonical("USING") == "WITH"
        assert processor.get_canonical("THRU") == "WITH"
        assert processor.get_canonical("WITH") == "WITH"  # primary maps to itself

    def test_synonym_directions(self, processor):
        """Process direction synonyms."""
        # <SYNONYM NORTH N>
        processor.process(Form(Atom("SYNONYM"), [Atom("NORTH"), Atom("N")]))
        assert processor.get_canonical("N") == "NORTH"

    def test_multiple_synonyms(self, processor):
        """Process multiple SYNONYM directives."""
        processor.process(Form(Atom("SYNONYM"), [Atom("IN"), Atom("INSIDE"), Atom("INTO")]))
        processor.process(Form(Atom("SYNONYM"), [Atom("ON"), Atom("ONTO")]))
        assert processor.get_canonical("INSIDE") == "IN"
        assert processor.get_canonical("ONTO") == "ON"

    def test_unknown_canonical(self, processor):
        """Unknown word returns itself."""
        assert processor.get_canonical("TAKE") == "TAKE"

    def test_synonym_case_insensitive(self, processor):
        """SYNONYM lookup is case-insensitive."""
        processor.process(Form(Atom("SYNONYM"), [Atom("NORTH"), Atom("N")]))
        assert processor.get_canonical("n") == "NORTH"


class TestNonDirectiveForms:
    """Tests for forms that are not directives."""

    @pytest.fixture
    def processor(self):
        return DirectiveProcessor()

    def test_routine_ignored(self, processor):
        """ROUTINE forms are ignored."""
        form = Form(Atom("ROUTINE"), [Atom("FOO")])
        processor.process(form)
        # Should not raise, just be ignored
        assert len(processor.constants) == 0

    def test_object_ignored(self, processor):
        """OBJECT forms are ignored (for now)."""
        form = Form(Atom("OBJECT"), [Atom("LAMP")])
        processor.process(form)
        assert len(processor.constants) == 0

    def test_non_form_ignored(self, processor):
        """Non-Form nodes are ignored."""
        processor.process(Atom("FOO"))
        processor.process(Number(42))
        processor.process(String("hello"))
        assert len(processor.constants) == 0
