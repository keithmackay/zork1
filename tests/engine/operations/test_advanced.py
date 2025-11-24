"""Tests for advanced ZIL operations."""

import pytest
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState


class TestPrimtypeOperation:
    """Tests for PRIMTYPE operation."""

    def test_primtype_list(self):
        """PRIMTYPE returns LIST type for lists."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRIMTYPE"), [[1, 2, 3]])
        )
        assert result == 1  # TYPE_LIST

    def test_primtype_string(self):
        """PRIMTYPE returns STRING type for strings."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRIMTYPE"), [String("hello")])
        )
        assert result == 3  # TYPE_STRING

    def test_primtype_number(self):
        """PRIMTYPE returns NUMBER type for integers."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRIMTYPE"), [Number(42)])
        )
        assert result == 4  # TYPE_NUMBER

    def test_primtype_evaluates_arg(self):
        """PRIMTYPE evaluates its argument."""
        world = WorldState()
        world.set_global("MYLIST", [1, 2, 3])
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRIMTYPE"), [Atom("MYLIST")])
        )
        assert result == 1  # TYPE_LIST


class TestPrintbOperation:
    """Tests for PRINTB operation."""

    def test_printb_string(self):
        """PRINTB prints string."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTB"), [String("hello")])
        )

        assert result is True
        assert "hello" in evaluator.output.get_output()

    def test_printb_bytes(self):
        """PRINTB prints byte array."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTB"), [bytes([72, 105])])  # "Hi"
        )

        assert result is True
        assert "Hi" in evaluator.output.get_output()

    def test_printb_list(self):
        """PRINTB prints list of byte values."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTB"), [[65, 66, 67]])  # "ABC"
        )

        assert result is True
        assert "ABC" in evaluator.output.get_output()


class TestIgrtrQuestionOperation:
    """Tests for IGRTR? operation."""

    def test_igrtr_question_true(self):
        """IGRTR? returns true when first > second."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("IGRTR?"), [Number(10), Number(5)])
        )
        assert result is True

    def test_igrtr_question_false(self):
        """IGRTR? returns false when first <= second."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("IGRTR?"), [Number(3), Number(5)])
        )
        assert result is False

    def test_igrtr_question_equal(self):
        """IGRTR? returns false for equal values."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("IGRTR?"), [Number(5), Number(5)])
        )
        assert result is False


class TestAgainOperation:
    """Tests for AGAIN operation."""

    def test_again_raises_exception(self):
        """AGAIN raises AgainException."""
        from zil_interpreter.engine.operations.advanced import AgainException

        world = WorldState()
        evaluator = Evaluator(world)

        with pytest.raises(AgainException):
            evaluator.evaluate(
                Form(Atom("AGAIN"), [])
            )

    def test_again_no_args(self):
        """AGAIN works with no arguments."""
        from zil_interpreter.engine.operations.advanced import AgainException

        world = WorldState()
        evaluator = Evaluator(world)

        with pytest.raises(AgainException):
            evaluator.evaluate(
                Form(Atom("AGAIN"), [])
            )


class TestTypeQuestionOperation:
    """Tests for TYPE? operation."""

    def test_type_question_string(self):
        """TYPE? identifies strings."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TYPE?"), [String("hello"), Atom("STRING")])
        )
        assert result is True

    def test_type_question_number(self):
        """TYPE? identifies numbers."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TYPE?"), [Number(42), Atom("NUMBER")])
        )
        assert result is True

    def test_type_question_list(self):
        """TYPE? identifies lists."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TYPE?"), [[1, 2, 3], Atom("LIST")])
        )
        assert result is True

    def test_type_question_multiple_types(self):
        """TYPE? checks multiple types (OR semantics)."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TYPE?"), [String("hello"), Atom("NUMBER"), Atom("STRING")])
        )
        assert result is True

    def test_type_question_wrong_type(self):
        """TYPE? returns FALSE for wrong type."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("TYPE?"), [Number(42), Atom("STRING")])
        )
        assert result is False


class TestValueOperation:
    """Tests for VALUE operation."""

    def test_value_global(self):
        """VALUE gets global variable value."""
        world = WorldState()
        world.set_global("SCORE", 100)
        world.set_global("VAR-NAME", "SCORE")  # Store variable name in another var
        evaluator = Evaluator(world)

        # Use VALUE with a variable that contains the name
        result = evaluator.evaluate(
            Form(Atom("VALUE"), [Atom("VAR-NAME")])
        )
        assert result == 100

    def test_value_string_name(self):
        """VALUE works with string variable names."""
        world = WorldState()
        world.set_global("MYVAR", 42)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("VALUE"), [String("MYVAR")])
        )
        assert result == 42

    def test_value_nonexistent(self):
        """VALUE returns None for nonexistent variable."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("VALUE"), [Atom("NONEXISTENT")])
        )
        assert result is None
