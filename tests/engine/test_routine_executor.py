import pytest
from zil_interpreter.engine.routine_executor import RoutineExecutor
from zil_interpreter.parser.ast_nodes import Routine, Form, Atom, String
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_execute_simple_routine():
    """Test executing a routine with no arguments."""
    world = WorldState()
    output = OutputBuffer()
    executor = RoutineExecutor(world, output)

    # <ROUTINE GREET () <TELL "Hello!">>
    routine = Routine(
        name="GREET",
        args=[],
        body=[Form(operator=Atom("TELL"), args=[String("Hello!")])]
    )

    executor.register_routine(routine)
    result = executor.call_routine("GREET", [])

    assert "Hello!" in output.get_output()


def test_execute_routine_sequence():
    """Test routine executes multiple expressions in sequence."""
    world = WorldState()
    output = OutputBuffer()
    executor = RoutineExecutor(world, output)

    # <ROUTINE TEST ()
    #   <TELL "Line 1">
    #   <TELL "Line 2">>
    routine = Routine(
        name="TEST",
        args=[],
        body=[
            Form(operator=Atom("TELL"), args=[String("Line 1")]),
            Form(operator=Atom("TELL"), args=[String("Line 2")])
        ]
    )

    executor.register_routine(routine)
    executor.call_routine("TEST", [])

    result = output.get_output()
    assert "Line 1" in result
    assert "Line 2" in result
