"""Tests for interrupt operations."""
import pytest
from zil_interpreter.engine.operations.interrupt_ops import QueueOp
from zil_interpreter.runtime.interrupt_manager import InterruptManager


class TestQueueOp:
    """Tests for QUEUE operation."""

    def test_queue_name(self):
        """Operation has correct name."""
        op = QueueOp()
        assert op.name == "QUEUE"

    def test_queue_schedules_interrupt(self):
        """QUEUE schedules interrupt for future turn."""
        manager = InterruptManager()

        op = QueueOp()

        class MockEvaluator:
            def __init__(self):
                self.interrupt_manager = manager

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        op.execute(["I-LANTERN", 100], evaluator)

        assert manager.has_interrupt("I-LANTERN")
