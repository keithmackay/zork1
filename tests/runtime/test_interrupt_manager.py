"""Tests for InterruptManager."""
import pytest
from zil_interpreter.runtime.interrupt_manager import InterruptManager, Interrupt


class TestInterruptManager:
    """Tests for InterruptManager class."""

    def test_create_manager(self):
        """Can create interrupt manager."""
        manager = InterruptManager()
        assert manager is not None

    def test_queue_interrupt(self):
        """Can queue an interrupt."""
        manager = InterruptManager()
        manager.queue("I-LANTERN", "LANTERN-FCN", 100)
        assert manager.has_interrupt("I-LANTERN")

    def test_tick_decrements_turns(self):
        """Tick decrements turns remaining."""
        manager = InterruptManager()
        manager.queue("I-LANTERN", "LANTERN-FCN", 5)
        manager.tick()
        interrupt = manager.get_interrupt("I-LANTERN")
        assert interrupt.turns_remaining == 4

    def test_tick_fires_when_zero(self):
        """Interrupt fires when turns reaches zero."""
        manager = InterruptManager()
        manager.queue("I-TEST", "TEST-FCN", 1)
        ready = manager.tick()
        assert "TEST-FCN" in ready

    def test_enable_disable(self):
        """Can enable and disable interrupts."""
        manager = InterruptManager()
        manager.queue("I-TEST", "TEST-FCN", 10)
        manager.disable("I-TEST")

        interrupt = manager.get_interrupt("I-TEST")
        assert interrupt.enabled is False

        manager.enable("I-TEST")
        assert interrupt.enabled is True

    def test_dequeue_removes(self):
        """Dequeue removes interrupt."""
        manager = InterruptManager()
        manager.queue("I-TEST", "TEST-FCN", 10)
        manager.dequeue("I-TEST")
        assert not manager.has_interrupt("I-TEST")
