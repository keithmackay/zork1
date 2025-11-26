"""Tests for I/O operations (PRINTN, PRINT, PRINTI)."""

import pytest
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState


class TestPrintnOperation:
    """Tests for PRINTN operation."""

    def test_printn_integer(self):
        """PRINTN prints integer values."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTN"), [Number(42)])
        )

        assert result is True
        assert evaluator.output.get_output() == "42"

    def test_printn_negative(self):
        """PRINTN prints negative numbers."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTN"), [Number(-17)])
        )

        assert result is True
        assert evaluator.output.get_output() == "-17"

    def test_printn_zero(self):
        """PRINTN prints zero."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTN"), [Number(0)])
        )

        assert result is True
        assert evaluator.output.get_output() == "0"

    def test_printn_from_variable(self):
        """PRINTN evaluates and prints variable value."""
        world = WorldState()
        world.set_global("COUNT", 99)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTN"), [Atom("COUNT")])
        )

        assert result is True
        assert evaluator.output.get_output() == "99"

    def test_printn_from_expression(self):
        """PRINTN can print result of expression."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTN"), [
                Form(Atom("+"), [Number(10), Number(32)])
            ])
        )

        assert result is True
        assert evaluator.output.get_output() == "42"

    def test_printn_string_number(self):
        """PRINTN can parse numeric strings."""
        world = WorldState()
        world.set_global("NUM_STR", "123")
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTN"), [Atom("NUM_STR")])
        )

        assert result is True
        assert evaluator.output.get_output() == "123"

    def test_printn_no_args(self):
        """PRINTN with no args returns TRUE without printing."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTN"), [])
        )

        assert result is True
        assert evaluator.output.get_output() == ""

    def test_printn_multiple_calls(self):
        """Multiple PRINTN calls concatenate output."""
        world = WorldState()
        evaluator = Evaluator(world)

        evaluator.evaluate(Form(Atom("PRINTN"), [Number(1)]))
        evaluator.evaluate(Form(Atom("PRINTN"), [Number(2)]))
        evaluator.evaluate(Form(Atom("PRINTN"), [Number(3)]))

        assert evaluator.output.get_output() == "123"


class TestPrintOperation:
    """Tests for PRINT operation."""

    def test_print_string_variable(self):
        """PRINT prints string variable value."""
        world = WorldState()
        world.set_global("MESSAGE", "Hello, world!")
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINT"), [Atom("MESSAGE")])
        )

        assert result is True
        assert evaluator.output.get_output() == "Hello, world!"

    def test_print_number_variable(self):
        """PRINT can print numeric variables."""
        world = WorldState()
        world.set_global("SCORE", 100)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINT"), [Atom("SCORE")])
        )

        assert result is True
        assert evaluator.output.get_output() == "100"

    def test_print_expression(self):
        """PRINT evaluates and prints expressions."""
        world = WorldState()
        world.set_global("FIRST", "Hello")
        world.set_global("SECOND", " world")
        evaluator = Evaluator(world)

        # Test printing result of CONCAT
        result = evaluator.evaluate(
            Form(Atom("PRINT"), [
                Form(Atom("CONCAT"), [Atom("FIRST"), Atom("SECOND")])
            ])
        )

        assert result is True
        assert evaluator.output.get_output() == "Hello world"

    def test_print_none_value(self):
        """PRINT with None value doesn't print anything."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Non-existent variable evaluates to None
        result = evaluator.evaluate(
            Form(Atom("PRINT"), [Atom("NONEXISTENT")])
        )

        assert result is True
        assert evaluator.output.get_output() == ""

    def test_print_no_args(self):
        """PRINT with no args returns TRUE without printing."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINT"), [])
        )

        assert result is True
        assert evaluator.output.get_output() == ""

    def test_print_empty_string(self):
        """PRINT can print empty strings."""
        world = WorldState()
        world.set_global("EMPTY", "")
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINT"), [Atom("EMPTY")])
        )

        assert result is True
        assert evaluator.output.get_output() == ""

    def test_print_multiple_calls(self):
        """Multiple PRINT calls concatenate output."""
        world = WorldState()
        world.set_global("A", "Hello")
        world.set_global("B", " ")
        world.set_global("C", "world")
        evaluator = Evaluator(world)

        evaluator.evaluate(Form(Atom("PRINT"), [Atom("A")]))
        evaluator.evaluate(Form(Atom("PRINT"), [Atom("B")]))
        evaluator.evaluate(Form(Atom("PRINT"), [Atom("C")]))

        assert evaluator.output.get_output() == "Hello world"


class TestPrintiOperation:
    """Tests for PRINTI operation."""

    def test_printi_string_literal(self):
        """PRINTI prints string literals."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTI"), [String("Hello, world!")])
        )

        assert result is True
        assert evaluator.output.get_output() == "Hello, world!"

    def test_printi_empty_string(self):
        """PRINTI can print empty strings."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTI"), [String("")])
        )

        assert result is True
        assert evaluator.output.get_output() == ""

    def test_printi_with_special_chars(self):
        """PRINTI handles special characters."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTI"), [String("Line 1\nLine 2\tTabbed")])
        )

        assert result is True
        assert "Line 1\nLine 2\tTabbed" in evaluator.output.get_output()

    def test_printi_number(self):
        """PRINTI can print number literals."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTI"), [Number(42)])
        )

        assert result is True
        assert evaluator.output.get_output() == "42"

    def test_printi_no_args(self):
        """PRINTI with no args returns TRUE without printing."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTI"), [])
        )

        assert result is True
        assert evaluator.output.get_output() == ""

    def test_printi_multiple_calls(self):
        """Multiple PRINTI calls concatenate output."""
        world = WorldState()
        evaluator = Evaluator(world)

        evaluator.evaluate(Form(Atom("PRINTI"), [String("Hello")]))
        evaluator.evaluate(Form(Atom("PRINTI"), [String(", ")]))
        evaluator.evaluate(Form(Atom("PRINTI"), [String("world!")]))

        assert evaluator.output.get_output() == "Hello, world!"

    def test_printi_with_expression(self):
        """PRINTI evaluates expressions before printing."""
        world = WorldState()
        world.set_global("NAME", "Alice")
        evaluator = Evaluator(world)

        # PRINTI should evaluate the variable
        result = evaluator.evaluate(
            Form(Atom("PRINTI"), [Atom("NAME")])
        )

        assert result is True
        assert evaluator.output.get_output() == "Alice"


class TestYesQuestionOp:
    """Tests for YES? Y/N prompt operation."""

    def test_yes_question_name(self):
        """Operation has correct name."""
        from zil_interpreter.engine.operations.io import YesQuestionOp
        op = YesQuestionOp()
        assert op.name == "YES?"

    def test_yes_question_returns_true_for_y(self):
        """YES? returns true for 'y' input."""
        from zil_interpreter.engine.operations.io import YesQuestionOp
        world = WorldState()
        evaluator = Evaluator(world)

        # Mock get_input method to return 'y'
        evaluator.get_input = lambda: "y"

        op = YesQuestionOp()
        result = op.execute([], evaluator)
        assert result is True

    def test_yes_question_returns_false_for_n(self):
        """YES? returns false for 'n' input."""
        from zil_interpreter.engine.operations.io import YesQuestionOp
        world = WorldState()
        evaluator = Evaluator(world)

        # Mock get_input method to return 'n'
        evaluator.get_input = lambda: "n"

        op = YesQuestionOp()
        result = op.execute([], evaluator)
        assert result is False

    def test_yes_question_case_insensitive(self):
        """YES? is case-insensitive."""
        from zil_interpreter.engine.operations.io import YesQuestionOp
        world = WorldState()
        evaluator = Evaluator(world)

        # Test uppercase Y
        evaluator.get_input = lambda: "Y"
        op = YesQuestionOp()
        assert op.execute([], evaluator) is True

        # Test uppercase N
        evaluator.get_input = lambda: "N"
        assert op.execute([], evaluator) is False

    def test_yes_question_defaults_true_non_interactive(self):
        """YES? defaults to True when no input available."""
        from zil_interpreter.engine.operations.io import YesQuestionOp
        world = WorldState()
        evaluator = Evaluator(world)

        # No get_input method - non-interactive mode
        op = YesQuestionOp()
        result = op.execute([], evaluator)
        assert result is True

        # Verify prompt was written
        assert "?" in evaluator.output.get_output()


class TestMixedPrintOperations:
    """Tests combining different print operations."""

    def test_mixed_print_operations(self):
        """Test combining PRINTN, PRINT, PRINTI, and CRLF."""
        world = WorldState()
        world.set_global("NAME", "Player")
        world.set_global("SCORE", 50)
        evaluator = Evaluator(world)

        # Build a complex output: "Player has 50 points.\n"
        evaluator.evaluate(Form(Atom("PRINT"), [Atom("NAME")]))
        evaluator.evaluate(Form(Atom("PRINTI"), [String(" has ")]))
        evaluator.evaluate(Form(Atom("PRINTN"), [Atom("SCORE")]))
        evaluator.evaluate(Form(Atom("PRINTI"), [String(" points.")]))
        evaluator.evaluate(Form(Atom("CRLF"), []))

        expected = "Player has 50 points.\n"
        assert evaluator.output.get_output() == expected

    def test_print_with_tell(self):
        """Print operations work alongside TELL."""
        world = WorldState()
        evaluator = Evaluator(world)

        evaluator.evaluate(Form(Atom("TELL"), [String("START: ")]))
        evaluator.evaluate(Form(Atom("PRINTN"), [Number(42)]))
        evaluator.evaluate(Form(Atom("TELL"), [String(" :END")]))

        assert evaluator.output.get_output() == "START: 42 :END"
