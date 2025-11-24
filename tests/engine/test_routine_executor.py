import pytest
from zil_interpreter.engine.routine_executor import RoutineExecutor
from zil_interpreter.parser.ast_nodes import Routine, Form, Atom, String, Number
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


def test_routine_with_arguments():
    """Test routine with argument binding."""
    world = WorldState()
    output = OutputBuffer()
    executor = RoutineExecutor(world, output)

    # <ROUTINE GREET (NAME) <TELL "Hello, " .NAME "!">>
    routine = Routine(
        name="GREET",
        args=["NAME"],
        body=[
            Form(operator=Atom("TELL"), args=[
                String("Hello, "),
                Atom(".NAME"),
                String("!")
            ])
        ]
    )

    executor.register_routine(routine)
    executor.call_routine("GREET", ["Alice"])

    assert "Hello, Alice!" in output.get_output()


def test_routine_multiple_arguments():
    """Test routine with multiple arguments."""
    world = WorldState()
    executor = RoutineExecutor(world)

    # <ROUTINE ADD (X Y) <+ .X .Y>>
    routine = Routine(
        name="ADD",
        args=["X", "Y"],
        body=[
            Form(operator=Atom("+"), args=[Atom(".X"), Atom(".Y")])
        ]
    )

    executor.register_routine(routine)
    result = executor.call_routine("ADD", [5, 3])

    assert result == 8


def test_set_local_variable():
    """Test SET for local variable assignment."""
    world = WorldState()
    executor = RoutineExecutor(world)

    # <ROUTINE TEST ()
    #   <SET X 10>
    #   <+ .X 5>>
    routine = Routine(
        name="TEST",
        args=[],
        body=[
            Form(operator=Atom("SET"), args=[Atom("X"), Number(10)]),
            Form(operator=Atom("+"), args=[Atom(".X"), Number(5)])
        ]
    )

    executor.register_routine(routine)
    result = executor.call_routine("TEST", [])

    assert result == 15


def test_setg_global_variable():
    """Test SETG for global variable assignment."""
    world = WorldState()
    executor = RoutineExecutor(world)

    # <ROUTINE TEST ()
    #   <SETG SCORE 100>>
    routine = Routine(
        name="TEST",
        args=[],
        body=[
            Form(operator=Atom("SETG"), args=[Atom("SCORE"), Number(100)])
        ]
    )

    executor.register_routine(routine)
    executor.call_routine("TEST", [])

    assert world.get_global("SCORE") == 100


def test_rtrue_return():
    """Test RTRUE returns True."""
    world = WorldState()
    executor = RoutineExecutor(world)

    # <ROUTINE IS_OPEN () <RTRUE>>
    routine = Routine(
        name="IS_OPEN",
        args=[],
        body=[Form(operator=Atom("RTRUE"), args=[])]
    )

    executor.register_routine(routine)
    result = executor.call_routine("IS_OPEN", [])

    assert result is True


def test_rfalse_return():
    """Test RFALSE returns False."""
    world = WorldState()
    executor = RoutineExecutor(world)

    # <ROUTINE IS_CLOSED () <RFALSE>>
    routine = Routine(
        name="IS_CLOSED",
        args=[],
        body=[Form(operator=Atom("RFALSE"), args=[])]
    )

    executor.register_routine(routine)
    result = executor.call_routine("IS_CLOSED", [])

    assert result is False


def test_early_return():
    """Test RTRUE causes early return."""
    world = WorldState()
    output = OutputBuffer()
    executor = RoutineExecutor(world, output)

    # <ROUTINE TEST ()
    #   <TELL "Before">
    #   <RTRUE>
    #   <TELL "After">>  ; Should not execute
    routine = Routine(
        name="TEST",
        args=[],
        body=[
            Form(operator=Atom("TELL"), args=[String("Before")]),
            Form(operator=Atom("RTRUE"), args=[]),
            Form(operator=Atom("TELL"), args=[String("After")])
        ]
    )

    executor.register_routine(routine)
    result = executor.call_routine("TEST", [])

    assert result is True
    assert "Before" in output.get_output()
    assert "After" not in output.get_output()
