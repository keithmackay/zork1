"""Tests for control flow and I/O operations."""

import pytest
from zil_interpreter.parser.ast_nodes import Form, Atom, Number, String
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject


class TestPerformOperation:
    """Tests for PERFORM operation."""

    def test_perform_sets_prsa(self):
        """PERFORM sets PRSA global."""
        world = WorldState()
        evaluator = Evaluator(world)

        evaluator.evaluate(
            Form(Atom("PERFORM"), [Atom("TAKE")])
        )

        assert world.get_global("PRSA") == "TAKE"

    def test_perform_with_direct_object(self):
        """PERFORM sets PRSO for direct object."""
        world = WorldState()
        evaluator = Evaluator(world)

        evaluator.evaluate(
            Form(Atom("PERFORM"), [Atom("TAKE"), Atom("LAMP")])
        )

        assert world.get_global("PRSA") == "TAKE"
        assert world.get_global("PRSO") == "LAMP"

    def test_perform_with_indirect_object(self):
        """PERFORM sets PRSI for indirect object."""
        world = WorldState()
        evaluator = Evaluator(world)

        evaluator.evaluate(
            Form(Atom("PERFORM"), [Atom("PUT"), Atom("LAMP"), Atom("TABLE")])
        )

        assert world.get_global("PRSA") == "PUT"
        assert world.get_global("PRSO") == "LAMP"
        assert world.get_global("PRSI") == "TABLE"

    def test_perform_returns_true(self):
        """PERFORM returns TRUE by default."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PERFORM"), [Atom("LOOK")])
        )

        assert result is True


class TestApplyOperation:
    """Tests for APPLY operation."""

    def test_apply_calls_routine(self):
        """APPLY calls routine with arguments."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Mock routine executor
        class MockExecutor:
            def __init__(self):
                self.routines = {"MYROUTINE": True}
                self.called_with = None

            def call_routine(self, name, args):
                self.called_with = (name, args)
                return 42

        mock_executor = MockExecutor()
        evaluator.routine_executor = mock_executor

        result = evaluator.evaluate(
            Form(Atom("APPLY"), [String("MYROUTINE"), Number(1), Number(2)])
        )

        assert result == 42
        assert mock_executor.called_with == ("MYROUTINE", [1, 2])

    def test_apply_no_args(self):
        """APPLY with no function returns None."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("APPLY"), [])
        )

        assert result is None

    def test_apply_with_callable(self):
        """APPLY can call Python callables."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Create a simple callable
        def my_func(a, b):
            return a + b

        result = evaluator.evaluate(
            Form(Atom("APPLY"), [my_func, Number(10), Number(20)])
        )

        assert result == 30


class TestGotoOperation:
    """Tests for GOTO operation."""

    def test_goto_sets_here(self):
        """GOTO sets HERE global to new room."""
        world = WorldState()
        room1 = GameObject("ROOM1")
        room2 = GameObject("ROOM2")
        world.add_object(room1)
        world.add_object(room2)
        world.set_global("HERE", room1)

        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("GOTO"), [Atom("ROOM2")])
        )

        assert result is True
        assert world.get_global("HERE") == room2

    def test_goto_invalid_room(self):
        """GOTO with invalid room returns None."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("GOTO"), [Atom("NONEXISTENT")])
        )

        assert result is None

    def test_goto_triggers_look(self):
        """GOTO triggers PERFORM LOOK."""
        world = WorldState()
        room = GameObject("TESTROOM")
        world.add_object(room)

        evaluator = Evaluator(world)

        # Before GOTO, PRSA should not be LOOK
        world.set_global("PRSA", None)

        evaluator.evaluate(
            Form(Atom("GOTO"), [Atom("TESTROOM")])
        )

        # After GOTO, PRSA should be set to LOOK
        assert world.get_global("PRSA") == "LOOK"


class TestRandomOperation:
    """Tests for RANDOM operation."""

    def test_random_range(self):
        """RANDOM returns value in range 1..N."""
        world = WorldState()
        evaluator = Evaluator(world)

        # Test many times to ensure range
        results = set()
        for _ in range(100):
            result = evaluator.evaluate(
                Form(Atom("RANDOM"), [Number(5)])
            )
            results.add(result)
            assert 1 <= result <= 5

        # Should have seen multiple different values
        assert len(results) >= 2

    def test_random_one(self):
        """RANDOM 1 always returns 1."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("RANDOM"), [Number(1)])
        )

        assert result == 1

    def test_random_invalid(self):
        """RANDOM with invalid arg returns 1."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("RANDOM"), [Number(0)])
        )

        assert result == 1

    def test_random_evaluates_arg(self):
        """RANDOM evaluates its argument."""
        world = WorldState()
        world.set_global("MAX", 10)
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("RANDOM"), [Atom("MAX")])
        )

        assert 1 <= result <= 10


class TestPrintdOperation:
    """Tests for PRINTD operation."""

    def test_printd_prints_desc(self):
        """PRINTD prints object DESC property."""
        world = WorldState()
        lamp = GameObject("LAMP")
        lamp.set_property("DESC", "a brass lantern")
        world.add_object(lamp)

        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTD"), [Atom("LAMP")])
        )

        assert result is True
        assert "a brass lantern" in evaluator.output.get_output()

    def test_printd_no_desc(self):
        """PRINTD with no DESC property doesn't crash."""
        world = WorldState()
        obj = GameObject("OBJ")
        world.add_object(obj)

        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTD"), [Atom("OBJ")])
        )

        assert result is True

    def test_printd_invalid_object(self):
        """PRINTD with invalid object returns TRUE."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("PRINTD"), [Atom("NONEXISTENT")])
        )

        assert result is True


class TestCrlfOperation:
    """Tests for CRLF operation."""

    def test_crlf_prints_newline(self):
        """CRLF prints a newline."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("CRLF"), [])
        )

        assert result is True
        assert "\n" in evaluator.output.get_output()

    def test_crlf_no_args(self):
        """CRLF works with no arguments."""
        world = WorldState()
        evaluator = Evaluator(world)

        result = evaluator.evaluate(
            Form(Atom("CRLF"), [])
        )

        assert result is True

    def test_crlf_multiple(self):
        """Multiple CRLF calls print multiple newlines."""
        world = WorldState()
        evaluator = Evaluator(world)

        evaluator.evaluate(Form(Atom("CRLF"), []))
        evaluator.evaluate(Form(Atom("CRLF"), []))

        output = evaluator.output.get_output()
        assert output == "\n\n"
