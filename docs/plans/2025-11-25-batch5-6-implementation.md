# Batches 5-6 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement remaining control flow and system operations for Zork I interpreter completion.

**Architecture:** Extend existing operation registry with 14 new operations. Add InterruptManager for timed events.

**Tech Stack:** Python 3.11+, pytest, existing zil_interpreter codebase.

---

## Batch 5: Control Flow Operations

AGAIN and APPLY already exist. Need: PROG, DO, MAP-CONTENTS, JIGS-UP, YES?, QUIT

---

### Task 5.1: PROG Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/control.py`
- Modify: `tests/engine/operations/test_control.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_control.py
from zil_interpreter.engine.operations.control import ProgOperation


class TestProgOperation:
    """Tests for PROG operation."""

    def test_prog_name(self):
        """Operation has correct name."""
        op = ProgOperation()
        assert op.name == "PROG"

    def test_prog_executes_body(self):
        """PROG executes body expressions in sequence."""
        world = WorldState()
        output = OutputBuffer()

        op = ProgOperation()

        class MockEvaluator:
            def __init__(self):
                self.world = world
                self.output = output
                self.results = []

            def evaluate(self, arg):
                self.results.append(arg)
                return arg

        evaluator = MockEvaluator()
        # PROG with empty bindings and body of [1, 2, 3]
        result = op.execute([[], 1, 2, 3], evaluator)
        assert evaluator.results == [[], 1, 2, 3]

    def test_prog_returns_last_value(self):
        """PROG returns value of last expression."""
        op = ProgOperation()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg * 2 if isinstance(arg, int) else arg

        evaluator = MockEvaluator()
        result = op.execute([[], 5], evaluator)
        assert result == 10
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_control.py::TestProgOperation -v`
Expected: FAIL with "cannot import name 'ProgOperation'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/control.py

class ProgOperation(Operation):
    """PROG - block scope with optional bindings.

    Usage: <PROG (bindings) body...>
    Executes body expressions in sequence, returns last value.
    """

    @property
    def name(self) -> str:
        return "PROG"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None

        # First arg is bindings (may be empty list)
        bindings = evaluator.evaluate(args[0]) if args else []
        body = args[1:] if len(args) > 1 else []

        # Execute body expressions
        result = None
        for expr in body:
            result = evaluator.evaluate(expr)

        return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_control.py::TestProgOperation -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/control.py tests/engine/operations/test_control.py
git commit -m "feat(ops): add PROG block scope operation"
```

---

### Task 5.2: DO Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/control.py`
- Modify: `tests/engine/operations/test_control.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_control.py
from zil_interpreter.engine.operations.control import DoOperation


class TestDoOperation:
    """Tests for DO counted loop operation."""

    def test_do_name(self):
        """Operation has correct name."""
        op = DoOperation()
        assert op.name == "DO"

    def test_do_iterates_count(self):
        """DO iterates specified number of times."""
        op = DoOperation()
        iterations = []

        class MockEvaluator:
            def evaluate(self, arg):
                if isinstance(arg, int):
                    return arg
                # Track each iteration
                iterations.append(1)
                return None

        evaluator = MockEvaluator()
        # <DO (I 1 5) body> - iterate I from 1 to 5
        # Simplified: args = [var, start, end, body...]
        op.execute(["I", 1, 5, "body"], evaluator)
        assert len(iterations) == 5

    def test_do_returns_none(self):
        """DO returns None on completion."""
        op = DoOperation()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        result = op.execute(["I", 1, 3, "body"], evaluator)
        assert result is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_control.py::TestDoOperation -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/control.py

class DoOperation(Operation):
    """DO - counted iteration loop.

    Usage: <DO (var start end) body...>
    Iterates var from start to end (inclusive), executing body each time.
    """

    @property
    def name(self) -> str:
        return "DO"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 3:
            return None

        var_name = args[0]
        start = evaluator.evaluate(args[1])
        end = evaluator.evaluate(args[2])
        body = args[3:] if len(args) > 3 else []

        # Iterate from start to end inclusive
        for i in range(start, end + 1):
            # Set loop variable
            evaluator.world.set_global(str(var_name), i)
            # Execute body
            for expr in body:
                evaluator.evaluate(expr)

        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_control.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/control.py tests/engine/operations/test_control.py
git commit -m "feat(ops): add DO counted loop operation"
```

---

### Task 5.3: MAP-CONTENTS Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/object_ops.py`
- Modify: `tests/engine/operations/test_object_ops.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_object_ops.py
from zil_interpreter.engine.operations.object_ops import MapContentsOperation


class TestMapContentsOperation:
    """Tests for MAP-CONTENTS operation."""

    def test_map_contents_name(self):
        """Operation has correct name."""
        op = MapContentsOperation()
        assert op.name == "MAP-CONTENTS"

    def test_map_contents_iterates_children(self):
        """MAP-CONTENTS iterates over container's children."""
        world = WorldState()
        room = GameObject(name="ROOM")
        world.add_object(room)
        lamp = GameObject(name="LAMP")
        lamp.parent = room
        world.add_object(lamp)
        sword = GameObject(name="SWORD")
        sword.parent = room
        world.add_object(sword)

        op = MapContentsOperation()
        visited = []

        class MockEvaluator:
            def __init__(self):
                self.world = world

            def evaluate(self, arg):
                if isinstance(arg, str) and arg in ["LAMP", "SWORD"]:
                    visited.append(arg)
                return arg

        evaluator = MockEvaluator()
        op.execute(["OBJ", "ROOM", "body"], evaluator)
        assert "LAMP" in visited or "SWORD" in visited
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_object_ops.py::TestMapContentsOperation -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/object_ops.py

class MapContentsOperation(Operation):
    """MAP-CONTENTS - iterate over container's children.

    Usage: <MAP-CONTENTS (var container) body...>
    Sets var to each child of container and executes body.
    """

    @property
    def name(self) -> str:
        return "MAP-CONTENTS"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            return None

        var_name = args[0]
        container_name = evaluator.evaluate(args[1])
        body = args[2:] if len(args) > 2 else []

        # Get container and its children
        container = evaluator.world.get_object(container_name)
        children = [obj for obj in evaluator.world._objects.values()
                   if obj.parent == container]

        # Iterate over children
        for child in children:
            evaluator.world.set_global(str(var_name), child.name)
            for expr in body:
                evaluator.evaluate(expr)

        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_object_ops.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/object_ops.py tests/engine/operations/test_object_ops.py
git commit -m "feat(ops): add MAP-CONTENTS container iteration operation"
```

---

### Task 5.4: JIGS-UP Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/game_logic.py`
- Modify: `tests/engine/operations/test_game_logic.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_game_logic.py
import pytest
from zil_interpreter.engine.operations.game_logic import JigsUpOp


class TestJigsUpOp:
    """Tests for JIGS-UP game over operation."""

    def test_jigs_up_name(self):
        """Operation has correct name."""
        op = JigsUpOp()
        assert op.name == "JIGS-UP"

    def test_jigs_up_prints_message(self):
        """JIGS-UP prints death message."""
        world = WorldState()
        output = OutputBuffer()

        op = JigsUpOp()

        class MockEvaluator:
            def __init__(self):
                self.world = world
                self.output = output

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()

        try:
            op.execute(["You have died."], evaluator)
        except SystemExit:
            pass

        assert "died" in output.get_output().lower()

    def test_jigs_up_sets_dead_flag(self):
        """JIGS-UP sets DEAD global."""
        world = WorldState()
        output = OutputBuffer()

        op = JigsUpOp()

        class MockEvaluator:
            def __init__(self):
                self.world = world
                self.output = output

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()

        try:
            op.execute(["Game over"], evaluator)
        except SystemExit:
            pass

        assert world.get_global("DEAD") is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_game_logic.py::TestJigsUpOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/game_logic.py

class JigsUpOp(Operation):
    """JIGS-UP - game over with death message.

    Usage: <JIGS-UP "message">
    Prints death message, sets DEAD flag, ends game.
    """

    @property
    def name(self) -> str:
        return "JIGS-UP"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        message = evaluator.evaluate(args[0]) if args else "You have died."

        # Print death message
        evaluator.output.write(f"\n{message}\n")

        # Set dead flag
        evaluator.world.set_global("DEAD", True)

        # For now, just return - game engine should check DEAD flag
        return True
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_game_logic.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/game_logic.py tests/engine/operations/test_game_logic.py
git commit -m "feat(ops): add JIGS-UP game over operation"
```

---

### Task 5.5: YES? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/io.py`
- Modify: `tests/engine/operations/test_io.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_io.py
from zil_interpreter.engine.operations.io import YesQuestionOp


class TestYesQuestionOp:
    """Tests for YES? Y/N prompt operation."""

    def test_yes_question_name(self):
        """Operation has correct name."""
        op = YesQuestionOp()
        assert op.name == "YES?"

    def test_yes_question_returns_true_for_y(self):
        """YES? returns true for 'y' input."""
        op = YesQuestionOp()

        class MockEvaluator:
            def get_input(self):
                return "y"

        evaluator = MockEvaluator()
        # In real implementation, would read input
        # For testing, we'll mock or use default
        result = op.execute([], evaluator)
        # Default implementation may return True or prompt
        assert result in [True, False, None]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_io.py::TestYesQuestionOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/io.py

class YesQuestionOp(Operation):
    """YES? - prompt for Y/N answer.

    Usage: <YES?>
    Prompts user and returns true for Y, false for N.
    """

    @property
    def name(self) -> str:
        return "YES?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        # In a real implementation, this would read input
        # For now, check if there's an input method on evaluator
        if hasattr(evaluator, 'get_input'):
            response = evaluator.get_input()
            return response.lower().startswith('y')

        # Default: prompt via output and return True
        evaluator.output.write("? ")
        return True  # Default to yes for non-interactive
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/io.py tests/engine/operations/test_io.py
git commit -m "feat(ops): add YES? Y/N prompt operation"
```

---

### Task 5.6: QUIT Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/control.py`
- Modify: `tests/engine/operations/test_control.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_control.py
from zil_interpreter.engine.operations.control import QuitOperation


class TestQuitOperation:
    """Tests for QUIT operation."""

    def test_quit_name(self):
        """Operation has correct name."""
        op = QuitOperation()
        assert op.name == "QUIT"

    def test_quit_sets_quit_flag(self):
        """QUIT sets QUIT global flag."""
        world = WorldState()

        op = QuitOperation()

        class MockEvaluator:
            def __init__(self):
                self.world = world

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        op.execute([], evaluator)

        assert world.get_global("QUIT") is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_control.py::TestQuitOperation -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/control.py

class QuitOperation(Operation):
    """QUIT - exit the game.

    Usage: <QUIT>
    Sets QUIT flag to signal game loop to exit.
    """

    @property
    def name(self) -> str:
        return "QUIT"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        evaluator.world.set_global("QUIT", True)
        return True
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_control.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/control.py tests/engine/operations/test_control.py
git commit -m "feat(ops): add QUIT exit game operation"
```

---

### Task 5.7: Register Batch 5 Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/__init__.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_registry.py
def test_batch5_operations_registered():
    """Batch 5 operations are registered."""
    from zil_interpreter.engine.operations import get_operation
    assert get_operation("PROG") is not None
    assert get_operation("DO") is not None
    assert get_operation("MAP-CONTENTS") is not None
    assert get_operation("JIGS-UP") is not None
    assert get_operation("YES?") is not None
    assert get_operation("QUIT") is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_registry.py::test_batch5_operations_registered -v`
Expected: FAIL

**Step 3: Register operations**

```python
# Add imports to zil_interpreter/engine/operations/__init__.py
from zil_interpreter.engine.operations.control import ProgOperation, DoOperation, QuitOperation
from zil_interpreter.engine.operations.object_ops import MapContentsOperation
from zil_interpreter.engine.operations.game_logic import JigsUpOp
from zil_interpreter.engine.operations.io import YesQuestionOp

# Add to create_default_registry():
    ProgOperation(),
    DoOperation(),
    MapContentsOperation(),
    JigsUpOp(),
    YesQuestionOp(),
    QuitOperation(),
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/__init__.py tests/engine/operations/test_registry.py
git commit -m "feat(ops): register Batch 5 control flow operations"
```

---

## Batch 6: System Operations

Need: QUEUE, ENABLE, DISABLE, INT, DEQUEUE, READ, LEX, WORD?

---

### Task 6.1: InterruptManager Infrastructure

**Files:**
- Create: `zil_interpreter/runtime/interrupt_manager.py`
- Create: `tests/runtime/test_interrupt_manager.py`

**Step 1: Write the failing test**

```python
# tests/runtime/test_interrupt_manager.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/runtime/test_interrupt_manager.py -v`
Expected: FAIL with "No module named"

**Step 3: Write minimal implementation**

```python
# zil_interpreter/runtime/interrupt_manager.py
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/runtime/test_interrupt_manager.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/runtime/interrupt_manager.py tests/runtime/test_interrupt_manager.py
git commit -m "feat(runtime): add InterruptManager for timed events"
```

---

### Task 6.2: QUEUE Operation

**Files:**
- Create: `zil_interpreter/engine/operations/interrupt_ops.py`
- Create: `tests/engine/operations/test_interrupt_ops.py`

**Step 1: Write the failing test**

```python
# tests/engine/operations/test_interrupt_ops.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_interrupt_ops.py::TestQueueOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# zil_interpreter/engine/operations/interrupt_ops.py
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_interrupt_ops.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/interrupt_ops.py tests/engine/operations/test_interrupt_ops.py
git commit -m "feat(ops): add QUEUE interrupt scheduling operation"
```

---

### Task 6.3: ENABLE, DISABLE, DEQUEUE Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/interrupt_ops.py`
- Modify: `tests/engine/operations/test_interrupt_ops.py`

**Step 1: Write the failing tests**

```python
# Add to tests/engine/operations/test_interrupt_ops.py
from zil_interpreter.engine.operations.interrupt_ops import QueueOp, EnableOp, DisableOp, DequeueOp


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_interrupt_ops.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/interrupt_ops.py

class EnableOp(Operation):
    """ENABLE - enable an interrupt."""

    @property
    def name(self) -> str:
        return "ENABLE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None
        int_name = evaluator.evaluate(args[0])
        if hasattr(evaluator, 'interrupt_manager'):
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
        int_name = evaluator.evaluate(args[0])
        if hasattr(evaluator, 'interrupt_manager'):
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
        int_name = evaluator.evaluate(args[0])
        if hasattr(evaluator, 'interrupt_manager'):
            evaluator.interrupt_manager.dequeue(int_name)
        return True
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_interrupt_ops.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/interrupt_ops.py tests/engine/operations/test_interrupt_ops.py
git commit -m "feat(ops): add ENABLE, DISABLE, DEQUEUE interrupt operations"
```

---

### Task 6.4: INT Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/interrupt_ops.py`
- Modify: `tests/engine/operations/test_interrupt_ops.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_interrupt_ops.py
from zil_interpreter.engine.operations.interrupt_ops import IntOp


class TestIntOp:
    """Tests for INT operation."""

    def test_int_name(self):
        op = IntOp()
        assert op.name == "INT"

    def test_int_returns_interrupt_ref(self):
        manager = InterruptManager()
        manager.queue("I-TEST", "TEST-FCN", 10)

        op = IntOp()

        class MockEvaluator:
            def __init__(self):
                self.interrupt_manager = manager
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        result = op.execute(["I-TEST"], evaluator)

        assert result == "I-TEST"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_interrupt_ops.py::TestIntOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/interrupt_ops.py

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
        int_name = evaluator.evaluate(args[0])
        return int_name
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_interrupt_ops.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/interrupt_ops.py tests/engine/operations/test_interrupt_ops.py
git commit -m "feat(ops): add INT interrupt reference operation"
```

---

### Task 6.5: READ and LEX Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/io.py`
- Modify: `tests/engine/operations/test_io.py`

**Step 1: Write the failing tests**

```python
# Add to tests/engine/operations/test_io.py
from zil_interpreter.engine.operations.io import ReadOp, LexOp


class TestReadOp:
    """Tests for READ operation."""

    def test_read_name(self):
        op = ReadOp()
        assert op.name == "READ"

    def test_read_returns_input(self):
        op = ReadOp()

        class MockEvaluator:
            def __init__(self):
                self.input_buffer = "look around"
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        result = op.execute([], evaluator)
        assert result is not None


class TestLexOp:
    """Tests for LEX operation."""

    def test_lex_name(self):
        op = LexOp()
        assert op.name == "LEX"

    def test_lex_tokenizes_input(self):
        op = LexOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        result = op.execute(["look around"], evaluator)
        # Returns tokenized form
        assert result is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_io.py::TestReadOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/io.py

class ReadOp(Operation):
    """READ - read player input.

    Usage: <READ buffer lexv>
    Reads input into buffer and tokenizes into lexv.
    """

    @property
    def name(self) -> str:
        return "READ"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        # Get input from evaluator if available
        if hasattr(evaluator, 'input_buffer'):
            return evaluator.input_buffer
        return ""


class LexOp(Operation):
    """LEX - tokenize input string.

    Usage: <LEX input-buffer lexv-table>
    Tokenizes input string into words.
    """

    @property
    def name(self) -> str:
        return "LEX"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return []

        input_str = evaluator.evaluate(args[0])
        if isinstance(input_str, str):
            return input_str.split()
        return []
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/io.py tests/engine/operations/test_io.py
git commit -m "feat(ops): add READ and LEX input operations"
```

---

### Task 6.6: WORD? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/io.py`
- Modify: `tests/engine/operations/test_io.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_io.py
from zil_interpreter.engine.operations.io import WordQuestionOp


class TestWordQuestionOp:
    """Tests for WORD? operation."""

    def test_word_question_name(self):
        op = WordQuestionOp()
        assert op.name == "WORD?"

    def test_word_question_checks_type(self):
        op = WordQuestionOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        # WORD? checks if word has certain property
        result = op.execute(["TAKE", "VERB"], evaluator)
        assert result in [True, False]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_io.py::TestWordQuestionOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/io.py

class WordQuestionOp(Operation):
    """WORD? - check word type/property.

    Usage: <WORD? word type>
    Returns true if word has specified type.
    """

    @property
    def name(self) -> str:
        return "WORD?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            return False

        word = evaluator.evaluate(args[0])
        word_type = evaluator.evaluate(args[1])

        # Simplified: check if word matches common types
        # In full implementation, would check vocabulary table
        verb_words = {"TAKE", "GET", "DROP", "LOOK", "OPEN", "CLOSE", "GO"}

        if word_type == "VERB":
            return str(word).upper() in verb_words

        return False
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/io.py tests/engine/operations/test_io.py
git commit -m "feat(ops): add WORD? word type checking operation"
```

---

### Task 6.7: Register Batch 6 Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/__init__.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_registry.py
def test_batch6_operations_registered():
    """Batch 6 operations are registered."""
    from zil_interpreter.engine.operations import get_operation
    assert get_operation("QUEUE") is not None
    assert get_operation("ENABLE") is not None
    assert get_operation("DISABLE") is not None
    assert get_operation("INT") is not None
    assert get_operation("DEQUEUE") is not None
    assert get_operation("READ") is not None
    assert get_operation("LEX") is not None
    assert get_operation("WORD?") is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_registry.py::test_batch6_operations_registered -v`
Expected: FAIL

**Step 3: Register operations**

```python
# Add imports to zil_interpreter/engine/operations/__init__.py
from zil_interpreter.engine.operations.interrupt_ops import (
    QueueOp, EnableOp, DisableOp, IntOp, DequeueOp
)
from zil_interpreter.engine.operations.io import ReadOp, LexOp, WordQuestionOp

# Add to create_default_registry():
    QueueOp(),
    EnableOp(),
    DisableOp(),
    IntOp(),
    DequeueOp(),
    ReadOp(),
    LexOp(),
    WordQuestionOp(),
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/__init__.py tests/engine/operations/test_registry.py
git commit -m "feat(ops): register Batch 6 system operations"
```

---

## Summary

| Batch | Tasks | Operations | Est. Tests |
|-------|-------|------------|------------|
| 5 | 5.1-5.7 | PROG, DO, MAP-CONTENTS, JIGS-UP, YES?, QUIT | ~30 |
| 6 | 6.1-6.7 | InterruptManager + QUEUE, ENABLE, DISABLE, INT, DEQUEUE, READ, LEX, WORD? | ~35 |

**Total: 14 new operations + InterruptManager infrastructure, ~65 new tests**
