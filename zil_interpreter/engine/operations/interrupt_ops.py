"""Interrupt operations: QUEUE, ENABLE, DISABLE, INT, DEQUEUE."""
from typing import Any, List
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


def _get_interrupt_name(arg: Any, evaluator: Any) -> str:
    """Extract interrupt name from argument.

    In ZIL, interrupt names are bare atoms (e.g. I-WIZARD), not variables.
    Treat Atom args as literal names; evaluate others normally.
    """
    if isinstance(arg, Atom):
        return arg.value.upper()
    val = evaluator.evaluate(arg)
    if isinstance(val, str):
        return val.upper()
    return str(val) if val is not None else ""


class QueueOp(Operation):
    """QUEUE - schedule interrupt for future turn.

    Usage: <QUEUE interrupt-name turns>
    Schedules interrupt to fire after N turns.
    Returns the interrupt name (for use with ENABLE).
    """

    @property
    def name(self) -> str:
        return "QUEUE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            return None

        int_name = _get_interrupt_name(args[0], evaluator)
        turns = evaluator.evaluate(args[1])
        if not isinstance(turns, int):
            turns = int(turns) if turns is not None else 1

        # Get interrupt manager from evaluator
        if hasattr(evaluator, 'interrupt_manager') and int_name:
            evaluator.interrupt_manager.queue(int_name, int_name, turns)

        return int_name  # Return name so ENABLE can reference it


class EnableOp(Operation):
    """ENABLE - enable an interrupt."""

    @property
    def name(self) -> str:
        return "ENABLE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None
        int_name = _get_interrupt_name(args[0], evaluator)
        if hasattr(evaluator, 'interrupt_manager') and int_name:
            evaluator.interrupt_manager.enable(int_name)
        return True


class DisableOp(Operation):
    """DISABLE - disable an interrupt."""

    @property
    def name(self) -> str:
        return "DISABLE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None
        int_name = _get_interrupt_name(args[0], evaluator)
        if hasattr(evaluator, 'interrupt_manager') and int_name:
            evaluator.interrupt_manager.disable(int_name)
        return True


class DequeueOp(Operation):
    """DEQUEUE - remove scheduled interrupt."""

    @property
    def name(self) -> str:
        return "DEQUEUE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None
        int_name = _get_interrupt_name(args[0], evaluator)
        if hasattr(evaluator, 'interrupt_manager') and int_name:
            evaluator.interrupt_manager.dequeue(int_name)
        return True


class IntOp(Operation):
    """INT - get interrupt reference.

    Usage: <INT interrupt-name>
    Returns the interrupt name/reference.
    """

    @property
    def name(self) -> str:
        return "INT"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None
        int_name = _get_interrupt_name(args[0], evaluator)
        return int_name
