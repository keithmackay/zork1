"""Interrupt manager for ZIL timed events."""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Interrupt:
    """A scheduled interrupt/daemon."""
    name: str
    routine: str
    turns_remaining: int
    enabled: bool = True


class InterruptManager:
    """Manages timed game events (interrupts/daemons)."""

    def __init__(self):
        self.interrupts: Dict[str, Interrupt] = {}

    def queue(self, name: str, routine: str, turns: int) -> None:
        """Schedule an interrupt to fire after N turns."""
        self.interrupts[name] = Interrupt(
            name=name,
            routine=routine,
            turns_remaining=turns,
            enabled=True
        )

    def dequeue(self, name: str) -> None:
        """Remove a scheduled interrupt."""
        if name in self.interrupts:
            del self.interrupts[name]

    def enable(self, name: str) -> None:
        """Enable an interrupt."""
        if name in self.interrupts:
            self.interrupts[name].enabled = True

    def disable(self, name: str) -> None:
        """Disable an interrupt."""
        if name in self.interrupts:
            self.interrupts[name].enabled = False

    def has_interrupt(self, name: str) -> bool:
        """Check if interrupt exists."""
        return name in self.interrupts

    def get_interrupt(self, name: str) -> Optional[Interrupt]:
        """Get interrupt by name."""
        return self.interrupts.get(name)

    def tick(self) -> List[str]:
        """Advance one turn, return routines ready to fire."""
        ready = []
        for interrupt in list(self.interrupts.values()):
            if not interrupt.enabled:
                continue
            interrupt.turns_remaining -= 1
            if interrupt.turns_remaining <= 0:
                ready.append(interrupt.routine)
                # Remove fired interrupt
                del self.interrupts[interrupt.name]
        return ready
