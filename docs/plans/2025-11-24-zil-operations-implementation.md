# ZIL Operations Registry Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend ZIL interpreter from 17 to 47 operations using an extensible registry pattern, enabling full Zork I gameplay.

**Architecture:** Create operation registry infrastructure, migrate 17 existing operations to registry classes, implement 30 new operations organized by category (logic, arithmetic, comparison, string, list, object, control), test with actual Zork I files.

**Tech Stack:** Python 3.11+, pytest, type hints, dataclasses, ABC for operation interface

---

## Phase 1: Foundation (Tasks 1-2)

### Task 1: Create Operation Registry Infrastructure

**Files:**
- Create: `zil_interpreter/engine/operations/__init__.py`
- Create: `zil_interpreter/engine/operations/base.py`
- Create: `tests/engine/operations/__init__.py`
- Create: `tests/engine/operations/test_registry.py`

**Step 1: Write the failing test**

Create test file:
```python
# tests/engine/operations/test_registry.py
from zil_interpreter.engine.operations.base import Operation, OperationRegistry

class MockOperation(Operation):
    @property
    def name(self) -> str:
        return "MOCK"

    def execute(self, args: list, evaluator) -> int:
        return 42

def test_registry_register():
    registry = OperationRegistry()
    op = MockOperation()
    registry.register(op)
    assert registry.has("MOCK")

def test_registry_get():
    registry = OperationRegistry()
    op = MockOperation()
    registry.register(op)
    retrieved = registry.get("MOCK")
    assert retrieved == op

def test_registry_case_insensitive():
    registry = OperationRegistry()
    op = MockOperation()
    registry.register(op)
    assert registry.get("mock") == op
    assert registry.get("Mock") == op
    assert registry.get("MOCK") == op
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/engine/operations/test_registry.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'zil_interpreter.engine.operations'"

**Step 3: Create operation base classes**

```python
# zil_interpreter/engine/operations/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zil_interpreter.engine.evaluator import Evaluator

class Operation(ABC):
    """Base class for all ZIL operations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Operation name (e.g., 'AND', 'OR', '+', 'EQUAL?')"""
        pass

    @abstractmethod
    def execute(self, args: list, evaluator: 'Evaluator') -> Any:
        """Execute the operation with given arguments.

        Args:
            args: List of unevaluated AST nodes (arguments)
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Result of operation execution
        """
        pass


class OperationRegistry:
    """Registry for all ZIL operations."""

    def __init__(self):
        self._operations: Dict[str, Operation] = {}

    def register(self, operation: Operation) -> None:
        """Register an operation by its name (case-insensitive)."""
        self._operations[operation.name.upper()] = operation

    def get(self, name: str) -> Optional[Operation]:
        """Get operation by name (case-insensitive)."""
        return self._operations.get(name.upper())

    def has(self, name: str) -> bool:
        """Check if operation is registered."""
        return name.upper() in self._operations
```

Create init file:
```python
# zil_interpreter/engine/operations/__init__.py
from .base import Operation, OperationRegistry

__all__ = ['Operation', 'OperationRegistry']
```

Create test init:
```python
# tests/engine/operations/__init__.py
# Empty init file for test package
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/engine/operations/test_registry.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/ tests/engine/operations/
git commit -m "feat(operations): add operation registry infrastructure

- Operation ABC with name and execute interface
- OperationRegistry for managing operations
- Case-insensitive operation lookup
- Tests for registry functionality

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: Integrate Registry into Evaluator

**Files:**
- Modify: `zil_interpreter/engine/evaluator.py:30-35` (add registry to __init__)
- Modify: `zil_interpreter/engine/evaluator.py:72-90` (_evaluate_form)
- Create: `tests/engine/test_evaluator_registry.py`

**Step 1: Write the failing test**

```python
# tests/engine/test_evaluator_registry.py
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number

class TestOperation(Operation):
    @property
    def name(self) -> str:
        return "TEST-OP"

    def execute(self, args: list, evaluator) -> int:
        return 999

def test_evaluator_uses_registry():
    """Evaluator should check registry for operations."""
    world = WorldState()
    evaluator = Evaluator(world)

    # Register test operation
    evaluator.registry.register(TestOperation())

    # Evaluate form using test operation
    result = evaluator.evaluate(Form(Atom("TEST-OP"), []))
    assert result == 999
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/engine/test_evaluator_registry.py -v`
Expected: FAIL with "AttributeError: 'Evaluator' object has no attribute 'registry'"

**Step 3: Add registry to Evaluator**

Modify evaluator to add registry:
```python
# zil_interpreter/engine/evaluator.py
# At top, add import:
from zil_interpreter.engine.operations.base import OperationRegistry

# In __init__ method (around line 30), add:
def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
    self.world = world
    self.output = output or OutputBuffer()
    self.registry = OperationRegistry()  # NEW
```

Modify _evaluate_form to check registry:
```python
# In _evaluate_form method (around line 72):
def _evaluate_form(self, form: Form) -> Any:
    """Evaluate a form (function call)."""
    op = form.operator.value.upper()

    # NEW: Check registry first
    operation = self.registry.get(op)
    if operation:
        return operation.execute(form.args, self)

    # Existing if/elif chain continues...
    if op == "EQUAL?":
        return self._eval_equal(form.args)
    # ... rest of existing code
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/engine/test_evaluator_registry.py -v`
Expected: PASS

**Step 5: Verify all existing tests still pass**

Run: `python -m pytest -q`
Expected: 76 passed (all existing tests still work)

**Step 6: Commit**

```bash
git add zil_interpreter/engine/evaluator.py tests/engine/test_evaluator_registry.py
git commit -m "feat(evaluator): integrate operation registry

- Add OperationRegistry to Evaluator.__init__
- Check registry before if/elif chain in _evaluate_form
- All 76 existing tests still pass
- Ready for operation migration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 2: Migration (Tasks 3-19)

### Task 3: Migrate EQUAL? Operation

**Files:**
- Create: `zil_interpreter/engine/operations/comparison.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py:145-151` (remove _eval_equal)

**Step 1: Create comparison operations file with EQUAL?**

```python
# zil_interpreter/engine/operations/comparison.py
from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom

class EqualOperation(Operation):
    """EQUAL? - Value equality check."""

    @property
    def name(self) -> str:
        return "EQUAL?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        return val1 == val2
```

**Step 2: Register in __init__.py**

```python
# zil_interpreter/engine/operations/__init__.py
from .base import Operation, OperationRegistry
from .comparison import EqualOperation

def create_default_registry() -> OperationRegistry:
    """Create registry with all standard operations."""
    registry = OperationRegistry()

    # Comparison
    registry.register(EqualOperation())

    return registry

__all__ = ['Operation', 'OperationRegistry', 'create_default_registry']
```

**Step 3: Update Evaluator to use create_default_registry**

```python
# zil_interpreter/engine/evaluator.py
# At top, update import:
from zil_interpreter.engine.operations import create_default_registry

# In __init__:
def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
    self.world = world
    self.output = output or OutputBuffer()
    self.registry = create_default_registry()  # CHANGED
```

**Step 4: Remove old _eval_equal method**

In evaluator.py, remove:
```python
# DELETE THIS METHOD (around line 145):
def _eval_equal(self, args: list) -> bool:
    """Evaluate EQUAL? comparison."""
    if len(args) < 2:
        return False
    val1 = self.evaluate(args[0])
    val2 = self.evaluate(args[1])
    return val1 == val2
```

**Step 5: Remove EQUAL? from if/elif chain**

In _evaluate_form, remove:
```python
# DELETE THIS BLOCK (around line 83):
if op == "EQUAL?":
    return self._eval_equal(form.args)
elif op == "FSET?":
    # Continue with this...
```

**Step 6: Run tests to verify migration**

Run: `python -m pytest tests/engine/test_evaluator.py::test_evaluate_equal -v`
Expected: PASS

Run: `python -m pytest -q`
Expected: 77 passed (76 existing + 1 new registry test)

**Step 7: Commit**

```bash
git add zil_interpreter/engine/operations/comparison.py zil_interpreter/engine/operations/__init__.py zil_interpreter/engine/evaluator.py
git commit -m "refactor(operations): migrate EQUAL? to registry

- Create comparison.py with EqualOperation
- Use create_default_registry() in Evaluator
- Remove _eval_equal method
- All tests still passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: Migrate FSET? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/comparison.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py:153-172` (remove _eval_fset_check)

**Step 1: Add FsetCheckOperation to comparison.py**

```python
# zil_interpreter/engine/operations/comparison.py
# Add after EqualOperation:

from zil_interpreter.world.game_object import ObjectFlag

class FsetCheckOperation(Operation):
    """FSET? - Check if object has flag set."""

    # Map ZIL flag names to ObjectFlag enum
    FLAG_MAP = {
        "OPENBIT": ObjectFlag.OPEN,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "TAKEABLEBIT": ObjectFlag.TAKEABLE,
        "LOCKEDBIT": ObjectFlag.LOCKED,
        "NDESCBIT": ObjectFlag.NDESCBIT,
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "ONBIT": ObjectFlag.ONBIT,
    }

    @property
    def name(self) -> str:
        return "FSET?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False

        # Get object name - if it's an Atom, use its value directly
        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        # Get flag name - same pattern
        flag_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return False

        flag = self.FLAG_MAP.get(flag_name.upper())
        if not flag:
            return False

        return obj.has_flag(flag)
```

**Step 2: Register in __init__.py**

```python
# zil_interpreter/engine/operations/__init__.py
from .comparison import EqualOperation, FsetCheckOperation

def create_default_registry() -> OperationRegistry:
    registry = OperationRegistry()

    # Comparison
    registry.register(EqualOperation())
    registry.register(FsetCheckOperation())

    return registry
```

**Step 3: Remove old method and if/elif**

Remove _eval_fset_check method and the if/elif block from evaluator.py

**Step 4: Run tests**

Run: `python -m pytest tests/engine/test_evaluator.py::test_evaluate_fset_check -v`
Expected: PASS

Run: `python -m pytest -q`
Expected: 77 passed

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/comparison.py zil_interpreter/engine/operations/__init__.py zil_interpreter/engine/evaluator.py
git commit -m "refactor(operations): migrate FSET? to registry

- Add FsetCheckOperation with flag mapping
- Register in default registry
- Remove _eval_fset_check method
- All tests passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: Migrate VERB? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/comparison.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py:173-180` (remove _eval_verb_check)

**Step 1: Add VerbCheckOperation**

```python
# zil_interpreter/engine/operations/comparison.py
# Add after FsetCheckOperation:

class VerbCheckOperation(Operation):
    """VERB? - Check current verb in parser state."""

    @property
    def name(self) -> str:
        return "VERB?"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return False

        verb_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        current_verb = evaluator.world.get_global("PRSA")
        return current_verb == verb_name
```

**Step 2: Register, remove old code, test, commit**

Follow same pattern as Task 4.

**Step 3: Commit**

```bash
git commit -m "refactor(operations): migrate VERB? to registry"
```

---

### Task 6: Migrate IN? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/comparison.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove _eval_in)

**Step 1: Add InCheckOperation**

```python
# zil_interpreter/engine/operations/comparison.py

class InCheckOperation(Operation):
    """IN? - Check if object is contained in another."""

    @property
    def name(self) -> str:
        return "IN?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        container_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        container = evaluator.world.get_object(container_name)

        if not obj or not container:
            return False

        return obj.parent == container
```

**Step 2: Register, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate IN? to registry"
```

---

### Task 7: Migrate FIRST? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/comparison.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove _eval_first)

**Step 1: Add FirstCheckOperation**

```python
# zil_interpreter/engine/operations/comparison.py

class FirstCheckOperation(Operation):
    """FIRST? - Get first child of object."""

    @property
    def name(self) -> str:
        return "FIRST?"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return None

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        obj = evaluator.world.get_object(obj_name)

        if not obj or not obj.children:
            return None

        return obj.children[0]
```

**Step 2: Register, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate FIRST? to registry"
```

---

### Task 8: Migrate COND Operation

**Files:**
- Create: `zil_interpreter/engine/operations/control.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove _eval_cond)

**Step 1: Create control.py with CondOperation**

```python
# zil_interpreter/engine/operations/control.py
from typing import Any
from zil_interpreter.engine.operations.base import Operation

class CondOperation(Operation):
    """COND - Conditional branching."""

    @property
    def name(self) -> str:
        return "COND"

    def execute(self, args: list, evaluator) -> Any:
        """Evaluate clauses until one succeeds."""
        for clause in args:
            if not hasattr(clause, '__iter__'):
                continue

            # Evaluate condition
            condition = evaluator.evaluate(clause[0])

            if condition:
                # Execute remaining forms in clause
                result = None
                for form in clause[1:]:
                    result = evaluator.evaluate(form)
                return result

        return None
```

**Step 2: Register, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate COND to registry"
```

---

### Task 9: Migrate + (Addition) Operation

**Files:**
- Create: `zil_interpreter/engine/operations/arithmetic.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove _eval_add)

**Step 1: Create arithmetic.py with AddOperation**

```python
# zil_interpreter/engine/operations/arithmetic.py
from typing import Any
from zil_interpreter.engine.operations.base import Operation

class AddOperation(Operation):
    """+ - Addition."""

    @property
    def name(self) -> str:
        return "+"

    def execute(self, args: list, evaluator) -> Any:
        result = 0
        for arg in args:
            result += evaluator.evaluate(arg)
        return result
```

**Step 2: Register, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate + (addition) to registry"
```

---

### Task 10: Migrate TELL Operation

**Files:**
- Create: `zil_interpreter/engine/operations/io.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove _eval_tell)

**Step 1: Create io.py with TellOperation**

```python
# zil_interpreter/engine/operations/io.py
from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import String, Atom

class TellOperation(Operation):
    """TELL - Output text to player."""

    @property
    def name(self) -> str:
        return "TELL"

    def execute(self, args: list, evaluator) -> None:
        """Output strings and atoms to output buffer."""
        for arg in args:
            if isinstance(arg, String):
                text = arg.value
                # Handle special formatting
                text = text.replace("\\n", "\n")
                evaluator.output.write(text)
            elif isinstance(arg, Atom):
                atom_val = arg.value.upper()
                if atom_val == "CR":
                    evaluator.output.write("\n")
                elif atom_val == "CRLF":
                    evaluator.output.write("\n")
                else:
                    # Evaluate as variable/expression
                    val = evaluator.evaluate(arg)
                    evaluator.output.write(str(val))
            else:
                # Evaluate and output
                val = evaluator.evaluate(arg)
                evaluator.output.write(str(val))
```

**Step 2: Register, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate TELL to registry"
```

---

### Task 11: Migrate Object Operations (MOVE, FSET, FCLEAR, GETP, PUTP)

**Files:**
- Create: `zil_interpreter/engine/operations/object_ops.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove 5 methods)

**Step 1: Create object_ops.py with all 5 operations**

```python
# zil_interpreter/engine/operations/object_ops.py
from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom
from zil_interpreter.world.game_object import ObjectFlag

class MoveOperation(Operation):
    """MOVE - Move object to new location."""

    @property
    def name(self) -> str:
        return "MOVE"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        dest_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        dest = evaluator.world.get_object(dest_name)

        if obj and dest:
            evaluator.world.move_object(obj, dest)


class FsetOperation(Operation):
    """FSET - Set flag on object."""

    FLAG_MAP = {
        "OPENBIT": ObjectFlag.OPEN,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "TAKEABLEBIT": ObjectFlag.TAKEABLE,
        "LOCKEDBIT": ObjectFlag.LOCKED,
        "NDESCBIT": ObjectFlag.NDESCBIT,
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "ONBIT": ObjectFlag.ONBIT,
    }

    @property
    def name(self) -> str:
        return "FSET"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        flag_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return

        flag = self.FLAG_MAP.get(flag_name.upper())
        if flag:
            obj.set_flag(flag)


class FclearOperation(Operation):
    """FCLEAR - Clear flag on object."""

    FLAG_MAP = FsetOperation.FLAG_MAP

    @property
    def name(self) -> str:
        return "FCLEAR"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 2:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        flag_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return

        flag = self.FLAG_MAP.get(flag_name.upper())
        if flag:
            obj.clear_flag(flag)


class GetpOperation(Operation):
    """GETP - Get property value from object."""

    @property
    def name(self) -> str:
        return "GETP"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        prop_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return None

        return obj.get_property(prop_name)


class PutpOperation(Operation):
    """PUTP - Set property value on object."""

    @property
    def name(self) -> str:
        return "PUTP"

    def execute(self, args: list, evaluator) -> None:
        if len(args) < 3:
            return

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        prop_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))
        value = evaluator.evaluate(args[2])

        obj = evaluator.world.get_object(obj_name)
        if obj:
            obj.set_property(prop_name, value)
```

**Step 2: Register all 5, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate object operations to registry

- MOVE, FSET, FCLEAR, GETP, PUTP operations
- All in object_ops.py module
- Remove 5 _eval_* methods from evaluator
- All tests passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 12: Migrate Variable Operations (SET, SETG)

**Files:**
- Create: `zil_interpreter/engine/operations/variables.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove _eval_set, _eval_setg)

**Step 1: Create variables.py with SET and SETG**

```python
# zil_interpreter/engine/operations/variables.py
from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom

class SetOperation(Operation):
    """SET - Set local variable."""

    @property
    def name(self) -> str:
        return "SET"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None

        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        value = evaluator.evaluate(args[1])

        # Set in routine executor's local scope
        if hasattr(evaluator, 'routine_executor'):
            evaluator.routine_executor.set_local(var_name, value)

        return value


class SetgOperation(Operation):
    """SETG - Set global variable."""

    @property
    def name(self) -> str:
        return "SETG"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return None

        var_name = args[0].value if isinstance(args[0], Atom) else str(args[0])
        value = evaluator.evaluate(args[1])

        evaluator.world.set_global(var_name, value)
        return value
```

**Step 2: Register, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate SET and SETG to registry"
```

---

### Task 13: Migrate Return Operations (RTRUE, RFALSE)

**Files:**
- Modify: `zil_interpreter/engine/operations/control.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `zil_interpreter/engine/evaluator.py` (remove RTRUE/RFALSE if/elif)

**Step 1: Add to control.py**

```python
# zil_interpreter/engine/operations/control.py
# At top, import ReturnValue:
from zil_interpreter.engine.evaluator import ReturnValue

class RtrueOperation(Operation):
    """RTRUE - Return true from routine."""

    @property
    def name(self) -> str:
        return "RTRUE"

    def execute(self, args: list, evaluator) -> None:
        raise ReturnValue(True)


class RfalseOperation(Operation):
    """RFALSE - Return false from routine."""

    @property
    def name(self) -> str:
        return "RFALSE"

    def execute(self, args: list, evaluator) -> None:
        raise ReturnValue(False)
```

**Step 2: Register, remove old code, test, commit**

```bash
git commit -m "refactor(operations): migrate RTRUE and RFALSE to registry"
```

---

## Phase 3: New Operations (Tasks 14-43)

### Task 14: Implement AND Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/logic.py` (create new)
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Create: `tests/engine/operations/test_logic.py`

**Step 1: Write failing tests**

```python
# tests/engine/operations/test_logic.py
from zil_interpreter.engine.evaluator import Evaluator
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.parser.ast_nodes import Form, Atom, Number

def test_and_all_true():
    """AND with all true values returns last value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("AND"), [Number(1), Number(2), Number(3)])
    )
    assert result == 3

def test_and_with_false():
    """AND with false value returns first false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("AND"), [Number(1), Number(0), Number(3)])
    )
    assert result == 0

def test_and_empty():
    """AND with no arguments returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("AND"), []))
    assert result is False
```

**Step 2: Run test to verify failure**

Run: `python -m pytest tests/engine/operations/test_logic.py -v`
Expected: FAIL with "NotImplementedError: Form not implemented: AND"

**Step 3: Implement AND operation**

```python
# zil_interpreter/engine/operations/logic.py
from typing import Any
from zil_interpreter.engine.operations.base import Operation

class AndOperation(Operation):
    """AND - Short-circuit logical AND."""

    @property
    def name(self) -> str:
        return "AND"

    def execute(self, args: list, evaluator) -> Any:
        """Returns first false value or last value."""
        if not args:
            return False

        result = None
        for arg in args:
            result = evaluator.evaluate(arg)
            if not result:
                return result
        return result
```

**Step 4: Register operation**

```python
# zil_interpreter/engine/operations/__init__.py
from .logic import AndOperation

def create_default_registry() -> OperationRegistry:
    registry = OperationRegistry()

    # Logic
    registry.register(AndOperation())

    # ... existing registrations
    return registry
```

**Step 5: Run tests to verify**

Run: `python -m pytest tests/engine/operations/test_logic.py::test_and_all_true -v`
Expected: PASS

Run: `python -m pytest tests/engine/operations/test_logic.py -v`
Expected: PASS (3 tests)

**Step 6: Commit**

```bash
git add zil_interpreter/engine/operations/logic.py tests/engine/operations/test_logic.py zil_interpreter/engine/operations/__init__.py
git commit -m "feat(operations): implement AND operation

- Short-circuit logical AND
- Returns first false or last value
- Tests for all-true, has-false, and empty cases

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 15: Implement OR Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/logic.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `tests/engine/operations/test_logic.py`

**Step 1: Write failing tests**

```python
# tests/engine/operations/test_logic.py
# Add after AND tests:

def test_or_with_true():
    """OR returns first true value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("OR"), [Number(0), Number(2), Number(3)])
    )
    assert result == 2

def test_or_all_false():
    """OR with all false returns last value."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(
        Form(Atom("OR"), [Number(0), Number(0), Number(0)])
    )
    assert result == 0

def test_or_empty():
    """OR with no arguments returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("OR"), []))
    assert result is False
```

**Step 2: Run test, implement, register, test, commit**

```python
# zil_interpreter/engine/operations/logic.py

class OrOperation(Operation):
    """OR - Short-circuit logical OR."""

    @property
    def name(self) -> str:
        return "OR"

    def execute(self, args: list, evaluator) -> Any:
        """Returns first true value or last value."""
        if not args:
            return False

        result = None
        for arg in args:
            result = evaluator.evaluate(arg)
            if result:
                return result
        return result
```

```bash
git commit -m "feat(operations): implement OR operation"
```

---

### Task 16: Implement NOT Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/logic.py`
- Modify: `zil_interpreter/engine/operations/__init__.py`
- Modify: `tests/engine/operations/test_logic.py`

**Step 1: Write failing tests**

```python
# tests/engine/operations/test_logic.py

def test_not_true():
    """NOT true returns false."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("NOT"), [Number(1)]))
    assert result is False

def test_not_false():
    """NOT false returns true."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("NOT"), [Number(0)]))
    assert result is True

def test_not_empty():
    """NOT with no arguments returns true."""
    world = WorldState()
    evaluator = Evaluator(world)

    result = evaluator.evaluate(Form(Atom("NOT"), []))
    assert result is True
```

**Step 2: Implement, register, test, commit**

```python
# zil_interpreter/engine/operations/logic.py

class NotOperation(Operation):
    """NOT - Logical negation."""

    @property
    def name(self) -> str:
        return "NOT"

    def execute(self, args: list, evaluator) -> bool:
        if not args:
            return True
        return not evaluator.evaluate(args[0])
```

```bash
git commit -m "feat(operations): implement NOT operation"
```

---

### Tasks 17-20: Arithmetic Operations (-, *, /, MOD)

**Files:**
- Modify: `zil_interpreter/engine/operations/arithmetic.py`
- Create: `tests/engine/operations/test_arithmetic.py`

**Follow same TDD pattern for each:**

1. Write 3-4 tests per operation
2. Run tests (fail)
3. Implement operation
4. Register in __init__.py
5. Run tests (pass)
6. Commit

**Subtract Operation:**
```python
class SubtractOperation(Operation):
    """- - Subtraction or negation."""

    @property
    def name(self) -> str:
        return "-"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return 0
        if len(args) == 1:
            # Unary negation
            return -evaluator.evaluate(args[0])
        # Binary subtraction
        result = evaluator.evaluate(args[0])
        for arg in args[1:]:
            result -= evaluator.evaluate(arg)
        return result
```

**Multiply, Divide, Modulo follow similar pattern.**

```bash
git commit -m "feat(operations): implement arithmetic operations (-, *, /, MOD)"
```

---

### Tasks 21-26: Comparison Operations (<, >, <=, >=, ZERO?, ==)

**Files:**
- Modify: `zil_interpreter/engine/operations/comparison.py`
- Create: `tests/engine/operations/test_comparison.py`

**Follow TDD pattern. Example for <:**

```python
class LessThanOperation(Operation):
    """< (L?) - Less than comparison."""

    @property
    def name(self) -> str:
        return "L?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        return val1 < val2
```

**Note:** Register both "L?" and "<" as aliases for same operation.

```bash
git commit -m "feat(operations): implement comparison operations (<, >, <=, >=, ZERO?, ==)"
```

---

### Tasks 27-29: String Operations (CONCAT, SUBSTRING, PRINTC)

**Files:**
- Create: `zil_interpreter/engine/operations/string_ops.py`
- Create: `tests/engine/operations/test_string_ops.py`

**Example:**

```python
class ConcatOperation(Operation):
    """CONCAT - Concatenate strings."""

    @property
    def name(self) -> str:
        return "CONCAT"

    def execute(self, args: list, evaluator) -> str:
        result = ""
        for arg in args:
            val = evaluator.evaluate(arg)
            result += str(val)
        return result
```

```bash
git commit -m "feat(operations): implement string operations (CONCAT, SUBSTRING, PRINTC)"
```

---

### Tasks 30-37: List Operations (LENGTH, NTH, REST, FIRST, NEXT, BACK, EMPTY?, MEMQ)

**Files:**
- Create: `zil_interpreter/engine/operations/list_ops.py`
- Create: `tests/engine/operations/test_list_ops.py`

**Example:**

```python
class LengthOperation(Operation):
    """LENGTH - Get length of list or string."""

    @property
    def name(self) -> str:
        return "LENGTH"

    def execute(self, args: list, evaluator) -> int:
        if not args:
            return 0
        val = evaluator.evaluate(args[0])
        if hasattr(val, '__len__'):
            return len(val)
        return 0
```

```bash
git commit -m "feat(operations): implement list operations (LENGTH, NTH, REST, etc.)"
```

---

### Tasks 38-40: Additional Object Operations (LOC, REMOVE, HELD?)

**Files:**
- Modify: `zil_interpreter/engine/operations/object_ops.py`
- Modify: `tests/engine/operations/test_object_ops.py`

**Example:**

```python
class LocOperation(Operation):
    """LOC - Get object location/parent."""

    @property
    def name(self) -> str:
        return "LOC"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return None
        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return None
        return obj.parent
```

```bash
git commit -m "feat(operations): implement LOC, REMOVE, and HELD? operations"
```

---

### Tasks 41-43: Control Flow Operations (RETURN, REPEAT, MAPF)

**Files:**
- Modify: `zil_interpreter/engine/operations/control.py`
- Create: `tests/engine/operations/test_control.py`

**Note:** REPEAT and MAPF are complex - implement minimal versions for now.

```bash
git commit -m "feat(operations): implement RETURN, REPEAT, and MAPF operations"
```

---

## Phase 4: Integration & Testing

### Task 44: Zork I Integration Test

**Files:**
- Create: `tests/integration/test_zork1.py`
- Modify: `README.md`

**Step 1: Write integration test**

```python
# tests/integration/test_zork1.py
import pytest
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.engine.game_engine import GameEngine

def test_load_zork1_files():
    """Verify Zork I loads without NotImplementedError."""
    try:
        loader = WorldLoader()
        # Adjust path based on actual location
        world = loader.load_file("../../zork1/zork1.zil")
        assert world is not None
    except NotImplementedError as e:
        pytest.fail(f"Missing operation: {e}")

def test_zork1_start_room():
    """Verify Zork I starting room displays."""
    try:
        loader = WorldLoader()
        world = loader.load_file("../../zork1/zork1.zil")
        engine = GameEngine(world)
        engine.execute_command("look")
        output = engine.output.get_text()
        # Check for iconic opening text
        assert "West of House" in output or "mailbox" in output.lower()
    except NotImplementedError as e:
        pytest.fail(f"Missing operation: {e}")
```

**Step 2: Run test and identify missing operations**

Run: `python -m pytest tests/integration/test_zork1.py -v`

If NotImplementedError occurs, note which operations are still missing and implement them.

**Step 3: Update README with complete operation list**

Update README.md to list all 47 operations organized by category.

**Step 4: Run full test suite**

Run: `python -m pytest -q`
Expected: 100+ tests passing

**Step 5: Commit**

```bash
git add tests/integration/test_zork1.py README.md
git commit -m "feat(integration): add Zork I integration tests

- Test loading full Zork I source files
- Verify starting room displays
- Update README with complete operation list
- All 47 operations implemented

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Step 6: Final verification**

Run: `python -m pytest --cov=zil_interpreter --cov-report=term`
Review coverage and add tests for any gaps.

---

## Success Criteria Checklist

- [ ] Phase 1 complete: Registry infrastructure created
- [ ] Phase 2 complete: All 17 existing operations migrated
- [ ] Phase 3 complete: All 30 new operations implemented
- [ ] Phase 4 complete: Zork I integration test passing
- [ ] All tests passing (100+ tests)
- [ ] README updated with operation list
- [ ] No NotImplementedError when loading Zork I
- [ ] Can execute basic Zork I commands (look, take, etc.)

---

## Appendix: Quick Reference

**Test command:** `python -m pytest -q`
**Verbose test:** `python -m pytest -v`
**Single test:** `python -m pytest tests/path/test.py::test_name -v`
**Coverage:** `python -m pytest --cov=zil_interpreter --cov-report=html`

**Commit message format:**
```
<type>(<scope>): <description>

- Bullet points with details
- What was added/changed/fixed

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** feat, refactor, test, docs, fix
**Scopes:** operations, evaluator, integration
