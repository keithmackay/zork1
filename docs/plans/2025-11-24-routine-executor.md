# Routine Executor - Tasks 16-20

**Date:** 2025-11-24
**Goal:** Implement routine execution engine to run ZIL functions with arguments, local variables, and return values.

## Overview

ZIL routines are functions that contain sequences of expressions. We need:
- Routine registry (mapping names to Routine AST nodes)
- Argument binding (passing values to routine parameters)
- Local variable scope (SET for locals, SETG for globals)
- Return value handling (RTRUE, RFALSE, explicit returns)
- Routine call evaluation (executing routines from expressions)

---

## Task 16: Basic Routine Execution

### Step 1: Write failing test

Create `tests/engine/test_routine_executor.py`:

```python
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
```

### Step 2: Implement RoutineExecutor class

Create `zil_interpreter/engine/routine_executor.py`:

```python
"""ZIL routine executor."""

from typing import Any, Dict, List, Optional
from zil_interpreter.parser.ast_nodes import Routine
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.evaluator import Evaluator


class RoutineExecutor:
    """Executes ZIL routines."""

    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
        self.evaluator = Evaluator(world, self.output)
        self.routines: Dict[str, Routine] = {}

    def register_routine(self, routine: Routine) -> None:
        """Register a routine for execution.

        Args:
            routine: Routine AST node
        """
        self.routines[routine.name.upper()] = routine

    def call_routine(self, name: str, args: List[Any]) -> Any:
        """Call a routine by name with arguments.

        Args:
            name: Routine name
            args: Argument values

        Returns:
            Return value from routine (last expression or explicit return)
        """
        routine = self.routines.get(name.upper())
        if not routine:
            raise ValueError(f"Unknown routine: {name}")

        # Execute routine body
        result = None
        for expr in routine.body:
            result = self.evaluator.evaluate(expr)

        return result
```

### Step 3: Commit

```bash
git add tests/engine/test_routine_executor.py zil_interpreter/engine/routine_executor.py
git commit -m "feat(engine): add basic routine execution

- Implement RoutineExecutor class
- Support routine registration and lookup
- Execute routine body expressions in sequence
- Return last expression value

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 17: Routine Arguments

### Step 1: Write failing test

```python
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
    from zil_interpreter.parser.ast_nodes import Number
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
```

### Step 2: Implement argument binding

Update `RoutineExecutor.call_routine()`:

```python
def call_routine(self, name: str, args: List[Any]) -> Any:
    """Call a routine by name with arguments."""
    routine = self.routines.get(name.upper())
    if not routine:
        raise ValueError(f"Unknown routine: {name}")

    # Create local variable scope
    local_scope: Dict[str, Any] = {}

    # Bind arguments to parameters
    for param, value in zip(routine.args, args):
        local_scope[param.upper()] = value

    # Save evaluator's current scope and set new scope
    old_scope = getattr(self.evaluator, 'local_scope', None)
    self.evaluator.local_scope = local_scope

    try:
        # Execute routine body
        result = None
        for expr in routine.body:
            result = self.evaluator.evaluate(expr)
        return result
    finally:
        # Restore previous scope
        if old_scope is not None:
            self.evaluator.local_scope = old_scope
        else:
            delattr(self.evaluator, 'local_scope')
```

### Step 3: Update Evaluator for local variables

In `evaluator.py`, update `Atom` evaluation:

```python
elif isinstance(expr, Atom):
    atom_value = expr.value.upper()

    # Check for local variable reference (.VAR syntax)
    if atom_value.startswith('.'):
        var_name = atom_value[1:]  # Remove leading dot
        if hasattr(self, 'local_scope') and var_name in self.local_scope:
            return self.local_scope[var_name]
        return None

    # Global variable lookup
    return self.world.get_global(atom_value)
```

### Step 4: Implement + operator

Add to evaluator's `_evaluate_form()`:

```python
if op == "+":
    return self._eval_add(form.args)
```

```python
def _eval_add(self, args: list) -> Any:
    """Evaluate + (addition)."""
    result = 0
    for arg in args:
        value = self.evaluate(arg)
        if isinstance(value, (int, float)):
            result += value
    return result
```

### Step 5: Commit

```bash
git commit -m "feat(engine): add routine argument binding

- Bind arguments to routine parameters
- Support local variable scope in routines
- Handle .VAR syntax for local variable access
- Add + operator for arithmetic

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 18: Local Variables (SET, SETG)

### Step 1: Write failing tests

```python
def test_set_local_variable():
    """Test SET for local variable assignment."""
    world = WorldState()
    executor = RoutineExecutor(world)

    # <ROUTINE TEST ()
    #   <SET X 10>
    #   <+ .X 5>>
    from zil_interpreter.parser.ast_nodes import Number
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
    from zil_interpreter.parser.ast_nodes import Number
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
```

### Step 2: Implement SET and SETG

Add to evaluator's `_evaluate_form()`:

```python
if op == "SET":
    return self._eval_set(form.args)

if op == "SETG":
    return self._eval_setg(form.args)
```

```python
def _eval_set(self, args: list) -> Any:
    """Evaluate SET form - set local variable."""
    if len(args) < 2:
        return None

    var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
    value = self.evaluate(args[1])

    # Set in local scope if it exists
    if hasattr(self, 'local_scope'):
        self.local_scope[var_name.upper()] = value
    else:
        # Fallback to global if no local scope
        self.world.set_global(var_name.upper(), value)

    return value


def _eval_setg(self, args: list) -> Any:
    """Evaluate SETG form - set global variable."""
    if len(args) < 2:
        return None

    var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
    value = self.evaluate(args[1])

    self.world.set_global(var_name.upper(), value)
    return value
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add SET and SETG variable assignment

- Implement SET for local variable assignment
- Implement SETG for global variable assignment
- Support variable scoping (local vs global)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 19: Return Values (RTRUE, RFALSE)

### Step 1: Write failing tests

```python
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
```

### Step 2: Implement RTRUE and RFALSE with early return

Update `Evaluator`:

```python
class ReturnValue(Exception):
    """Exception to implement early return from routines."""
    def __init__(self, value):
        self.value = value


# In _evaluate_form():
if op == "RTRUE":
    raise ReturnValue(True)

if op == "RFALSE":
    raise ReturnValue(False)
```

Update `RoutineExecutor.call_routine()`:

```python
try:
    # Execute routine body
    result = None
    for expr in routine.body:
        result = self.evaluator.evaluate(expr)
    return result
except ReturnValue as rv:
    return rv.value
finally:
    # Restore previous scope
    ...
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add RTRUE and RFALSE return values

- Implement RTRUE to return True
- Implement RFALSE to return False
- Support early return from routines
- Use exception-based control flow for returns

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 20: Routine Call from Expressions

### Step 1: Write failing test

```python
def test_call_routine_from_expression():
    """Test calling a routine from within an expression."""
    world = WorldState()
    executor = RoutineExecutor(world)

    # <ROUTINE DOUBLE (X) <+ .X .X>>
    # <ROUTINE TEST () <DOUBLE 5>>
    from zil_interpreter.parser.ast_nodes import Number

    double_routine = Routine(
        name="DOUBLE",
        args=["X"],
        body=[Form(operator=Atom("+"), args=[Atom(".X"), Atom(".X")])]
    )

    test_routine = Routine(
        name="TEST",
        args=[],
        body=[Form(operator=Atom("DOUBLE"), args=[Number(5)])]
    )

    executor.register_routine(double_routine)
    executor.register_routine(test_routine)

    result = executor.call_routine("TEST", [])
    assert result == 10
```

### Step 2: Update Evaluator to handle routine calls

In `Evaluator._evaluate_form()`, add fallback for unknown forms:

```python
def _evaluate_form(self, form: Form) -> Any:
    """Evaluate a form (function call)."""
    op = form.operator.value.upper()

    # ... all existing operations ...

    # Check if it's a routine call
    if hasattr(self, 'routine_executor'):
        executor = self.routine_executor
        if op in executor.routines:
            # Evaluate arguments
            args = [self.evaluate(arg) for arg in form.args]
            return executor.call_routine(op, args)

    raise NotImplementedError(f"Form not implemented: {op}")
```

Update `RoutineExecutor.__init__()` to link evaluator:

```python
def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
    self.world = world
    self.output = output or OutputBuffer()
    self.evaluator = Evaluator(world, self.output)
    self.evaluator.routine_executor = self  # Link back for routine calls
    self.routines: Dict[str, Routine] = {}
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add routine calls from expressions

- Allow routines to call other routines
- Link evaluator and executor bidirectionally
- Evaluate arguments before passing to routines
- Support recursive routine calls

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Completion

After Tasks 16-20, we have:
- ✅ Routine registration and execution
- ✅ Argument binding with local scope
- ✅ Local (SET) and global (SETG) variable assignment
- ✅ Return values (RTRUE, RFALSE) with early return
- ✅ Routine calls from expressions (recursion support)

This provides the runtime engine needed to execute ZIL game logic.
