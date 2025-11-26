"""Tests for interrupt operations."""
import pytest
from zil_interpreter.engine.operations.interrupt_ops import QueueOp, EnableOp, DisableOp, DequeueOp
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


class TestEnableOp:
    """Tests for ENABLE operation."""

    def test_enable_name(self):
        op = EnableOp()
        assert op.name == "ENABLE"

    def test_enable_enables_interrupt(self):
        manager = InterruptManager()
        manager.queue("I-TEST", "TEST-FCN", 10)
        manager.disable("I-TEST")

        op = EnableOp()

        class MockEvaluator:
            def __init__(self):
                self.interrupt_manager = manager
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        op.execute(["I-TEST"], evaluator)

        assert manager.get_interrupt("I-TEST").enabled is True


class TestDisableOp:
    """Tests for DISABLE operation."""

    def test_disable_name(self):
        op = DisableOp()
        assert op.name == "DISABLE"

    def test_disable_disables_interrupt(self):
        manager = InterruptManager()
        manager.queue("I-TEST", "TEST-FCN", 10)

        op = DisableOp()

        class MockEvaluator:
            def __init__(self):
                self.interrupt_manager = manager
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        op.execute(["I-TEST"], evaluator)

        assert manager.get_interrupt("I-TEST").enabled is False


class TestDequeueOp:
    """Tests for DEQUEUE operation."""

    def test_dequeue_name(self):
        op = DequeueOp()
        assert op.name == "DEQUEUE"

    def test_dequeue_removes_interrupt(self):
        manager = InterruptManager()
        manager.queue("I-TEST", "TEST-FCN", 10)

        op = DequeueOp()

        class MockEvaluator:
            def __init__(self):
                self.interrupt_manager = manager
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        op.execute(["I-TEST"], evaluator)

        assert not manager.has_interrupt("I-TEST")
