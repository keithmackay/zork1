"""Interrupt operations: QUEUE, ENABLE, DISABLE, INT, DEQUEUE."""
from typing import Any, List
from zil_interpreter.engine.operations.base import Operation


class QueueOp(Operation):
    """QUEUE - schedule interrupt for future turn.

    Usage: <QUEUE interrupt-name turns>
    Schedules interrupt to fire after N turns.
    """

    @property
    def name(self) -> str:
        return "QUEUE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            return None

        int_name = evaluator.evaluate(args[0])
        turns = evaluator.evaluate(args[1])

        # Get interrupt manager from evaluator
        if hasattr(evaluator, 'interrupt_manager'):
            evaluator.interrupt_manager.queue(int_name, int_name, turns)

        return True
