# ZIL Operations Registry - Adding 30 Missing Operations

**Date:** 2025-11-24
**Goal:** Extend ZIL interpreter to support full Zork I gameplay by adding ~30 missing operations using an extensible registry pattern.

## Requirements Summary

- **Current State**: 17 operations implemented in monolithic evaluator
- **Target**: 47 total operations (17 existing + 30 new)
- **Architecture**: Operation registry pattern for extensibility
- **Organization**: By category (logic, arithmetic, comparison, string, list, object, control)
- **Method**: Test-Driven Development with migration of existing operations
- **Success**: All 76 existing tests pass + new tests for each operation + Zork I playable

## Architecture: Operation Registry Pattern

### Core Components

**1. Operation Interface** (`engine/operations/base.py`)
```python
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

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
```

**2. Operation Registry** (`engine/operations/base.py`)
```python
from typing import Dict, Optional

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

**3. Modified Evaluator** (`engine/evaluator.py`)
```python
class Evaluator:
    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
        self.registry = create_default_registry()  # NEW: Operation registry

    def _evaluate_form(self, form: Form) -> Any:
        """Evaluate a form (function call)."""
        op = form.operator.value.upper()

        # NEW: Try registry lookup first
        operation = self.registry.get(op)
        if operation:
            return operation.execute(form.args, self)

        # Fallback: Routine calls
        if hasattr(self, 'routine_executor'):
            executor = self.routine_executor
            if op in executor.routines:
                args = [self.evaluate(arg) for arg in form.args]
                return executor.call_routine(op, args)

        raise NotImplementedError(f"Form not implemented: {op}")
```

### File Structure

```
zil_interpreter/engine/operations/
├── __init__.py          # Registry creation + exports
├── base.py              # Operation interface + OperationRegistry
├── logic.py             # AND, OR, NOT (3 ops)
├── arithmetic.py        # -, *, /, MOD (4 ops)
├── comparison.py        # <, >, <=, >=, ZERO?, == (6 ops)
├── string_ops.py        # CONCAT, SUBSTRING, PRINTC (3 ops)
├── list_ops.py          # LENGTH, NTH, REST, FIRST, NEXT, BACK, EMPTY?, MEMQ (8 ops)
├── object_ops.py        # LOC, REMOVE, HELD? (3 ops)
└── control.py           # RETURN, REPEAT, MAPF (3 ops)
```

### Design Benefits

1. **Extensibility**: Add new operations without modifying evaluator
2. **Testability**: Each operation is independently testable
3. **Separation of Concerns**: Operations isolated from evaluation logic
4. **Discoverability**: All operations visible in registry
5. **Type Safety**: Full type hints throughout
6. **Maintainability**: Small, focused classes vs giant if/elif chain

## Complete Operation List (47 Total)

### Existing Operations (17) - To Be Migrated

**Comparison (1)**:
- `EQUAL?` - Value equality check

**Logic/Predicates (3)**:
- `FSET?` - Flag check
- `VERB?` - Current verb check
- `IN?` - Containment check
- `FIRST?` - First child check

**Control Flow (1)**:
- `COND` - Conditional branching

**Arithmetic (1)**:
- `+` - Addition

**Object Operations (5)**:
- `MOVE` - Move object
- `FSET` - Set flag
- `FCLEAR` - Clear flag
- `GETP` - Get property
- `PUTP` - Set property

**I/O (1)**:
- `TELL` - Output text

**Variables (2)**:
- `SET` - Set local variable
- `SETG` - Set global variable

**Returns (2)**:
- `RTRUE` - Return true
- `RFALSE` - Return false

### New Operations (30)

#### Category 1: Logic (3 ops)

**`AND`** - Short-circuit logical AND
```python
class AndOperation(Operation):
    name = "AND"
    def execute(self, args, evaluator):
        # Returns first false value or last value
        for arg in args:
            result = evaluator.evaluate(arg)
            if not result:
                return result
        return result if args else False
```

**`OR`** - Short-circuit logical OR
```python
class OrOperation(Operation):
    name = "OR"
    def execute(self, args, evaluator):
        # Returns first true value or last value
        for arg in args:
            result = evaluator.evaluate(arg)
            if result:
                return result
        return result if args else False
```

**`NOT`** - Logical negation
```python
class NotOperation(Operation):
    name = "NOT"
    def execute(self, args, evaluator):
        if not args:
            return True
        return not evaluator.evaluate(args[0])
```

#### Category 2: Arithmetic (4 ops)

**`-`** - Subtraction (binary) or negation (unary)
- Binary: `<- 10 3>` → 7
- Unary: `<- 5>` → -5

**`*`** - Multiplication
- `<* 3 4>` → 12

**`/`** - Integer division
- `</ 10 3>` → 3

**`MOD`** - Modulo/remainder
- `<MOD 10 3>` → 1

#### Category 3: Comparison (6 ops)

**`<` (or `L?`)** - Less than
- `<L? 3 5>` → true

**`>` (or `G?`)** - Greater than
- `<G? 5 3>` → true

**`<=`** - Less than or equal
- `<<= 3 3>` → true

**`>=`** - Greater than or equal
- `<>= 5 3>` → true

**`ZERO?`** - Check if zero
- `<ZERO? 0>` → true

**`==`** - Numeric equality (stricter than EQUAL?)
- `<== 3 3>` → true

#### Category 4: String Operations (3 ops)

**`CONCAT`** - Concatenate strings
- `<CONCAT "hello" " " "world">` → "hello world"

**`SUBSTRING`** - Extract substring
- `<SUBSTRING "hello" 2 4>` → "ell" (positions 2-4)

**`PRINTC`** - Print single character
- `<PRINTC 65>` → prints 'A'

#### Category 5: List Operations (8 ops)

**`LENGTH`** - Get length
- `<LENGTH '(1 2 3)>` → 3

**`NTH`** - Get nth element (1-indexed)
- `<NTH '(A B C) 2>` → B

**`REST`** - Get tail (all but first)
- `<REST '(1 2 3)>` → (2 3)

**`FIRST`** - Get first element
- `<FIRST '(1 2 3)>` → 1

**`NEXT`** - Get next sibling object
- Used for iterating object hierarchies

**`BACK`** - Get previous element
- Reverse of NEXT

**`EMPTY?`** - Check if empty
- `<EMPTY? '()>` → true

**`MEMQ`** - Check membership
- `<MEMQ 2 '(1 2 3)>` → true

#### Category 6: Object Operations (3 ops)

**`LOC`** - Get object location/parent
- `<LOC LAMP>` → ROOM

**`REMOVE`** - Remove object from world
- Equivalent to `<MOVE OBJ void>`

**`HELD?`** - Check if player holds object
- `<HELD? LAMP>` → true/false

#### Category 7: Control Flow (3 ops)

**`RETURN`** - Return value from routine
- Similar to RTRUE/RFALSE but with arbitrary value

**`REPEAT`** - Loop construct
- `<REPEAT () <...>>` - infinite loop with break conditions

**`MAPF`** - Map function over collection
- `<MAPF ,FUNC ,LIST>` - apply function to each element

## Migration Strategy

### Phase 1: Foundation (Tasks 1-2)

**Task 1: Create Operation Infrastructure**
1. Create `engine/operations/` directory
2. Implement `base.py` with Operation interface and OperationRegistry
3. Write unit tests for OperationRegistry
4. Implement `__init__.py` with `create_default_registry()` function

**Task 2: Integrate Registry into Evaluator**
1. Add `self.registry` to Evaluator.__init__()
2. Modify `_evaluate_form()` to check registry first
3. Ensure all 76 existing tests still pass
4. No behavioral changes at this stage

### Phase 2: Migration (Tasks 3-19)

Migrate 17 existing operations from evaluator methods to operation classes:

**Task 3-19**: One task per existing operation
- Create operation class in appropriate category file
- Move logic from `_eval_xxx()` to `execute()`
- Register in `create_default_registry()`
- Verify tests still pass
- Remove old `_eval_xxx()` method

**Example Migration**:
```python
# Before (evaluator.py):
def _eval_equal(self, args: list) -> bool:
    if len(args) < 2:
        return False
    val1 = self.evaluate(args[0])
    val2 = self.evaluate(args[1])
    return val1 == val2

# After (operations/comparison.py):
class EqualOperation(Operation):
    @property
    def name(self) -> str:
        return "EQUAL?"

    def execute(self, args: list, evaluator) -> Any:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        return val1 == val2
```

### Phase 3: New Operations (Tasks 20-49)

Implement 30 new operations by category, one task per operation:

**Tasks 20-22: Logic Operations**
- Task 20: Implement AND operation + tests
- Task 21: Implement OR operation + tests
- Task 22: Implement NOT operation + tests

**Tasks 23-26: Arithmetic Operations**
- Task 23: Implement subtraction (-) + tests
- Task 24: Implement multiplication (*) + tests
- Task 25: Implement division (/) + tests
- Task 26: Implement modulo (MOD) + tests

**Tasks 27-32: Comparison Operations**
- Task 27: Implement less than (<, L?) + tests
- Task 28: Implement greater than (>, G?) + tests
- Task 29: Implement less-equal (<=) + tests
- Task 30: Implement greater-equal (>=) + tests
- Task 31: Implement ZERO? predicate + tests
- Task 32: Implement numeric equality (==) + tests

**Tasks 33-35: String Operations**
- Task 33: Implement CONCAT + tests
- Task 34: Implement SUBSTRING + tests
- Task 35: Implement PRINTC + tests

**Tasks 36-43: List Operations**
- Task 36: Implement LENGTH + tests
- Task 37: Implement NTH + tests
- Task 38: Implement REST + tests
- Task 39: Implement FIRST + tests
- Task 40: Implement NEXT + tests
- Task 41: Implement BACK + tests
- Task 42: Implement EMPTY? + tests
- Task 43: Implement MEMQ + tests

**Tasks 44-46: Object Operations**
- Task 44: Implement LOC + tests
- Task 45: Implement REMOVE + tests
- Task 46: Implement HELD? + tests

**Tasks 47-49: Control Flow**
- Task 47: Implement RETURN + tests
- Task 48: Implement REPEAT + tests
- Task 49: Implement MAPF + tests

### Phase 4: Integration & Testing (Task 50)

**Task 50: Zork I Integration Test**
1. Load actual Zork I source files (`zork1/zork1.zil`)
2. Identify any remaining missing operations
3. Verify game starts and basic commands work
4. Create integration test with real Zork I commands
5. Update README with complete operation list

## Testing Strategy

### Test Organization

```
tests/engine/operations/
├── test_logic.py          # AND, OR, NOT tests
├── test_arithmetic.py     # -, *, /, MOD tests
├── test_comparison.py     # <, >, <=, >=, ZERO?, == tests
├── test_string_ops.py     # CONCAT, SUBSTRING, PRINTC tests
├── test_list_ops.py       # LENGTH, NTH, REST, etc. tests
├── test_object_ops.py     # LOC, REMOVE, HELD? tests
└── test_control.py        # RETURN, REPEAT, MAPF tests
```

### Test Pattern (TDD)

For each operation:
1. **RED**: Write failing test first
2. **GREEN**: Implement minimal operation to pass
3. **REFACTOR**: Clean up implementation
4. **REGISTER**: Add to registry
5. **VERIFY**: Run full test suite

**Example Test**:
```python
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

def test_and_short_circuit():
    """AND stops evaluating after first false."""
    world = WorldState()
    evaluator = Evaluator(world)

    # This would fail if NOT short-circuiting
    result = evaluator.evaluate(
        Form(Atom("AND"), [
            Number(0),
            Form(Atom("/"), [Number(1), Number(0)])  # Would divide by zero
        ])
    )
    assert result == 0  # Stopped at first false, no error
```

### Integration Testing

**Test with Simple Game**:
```zil
<ROUTINE TEST-LOGIC ()
    <COND (<AND <NOT <ZERO? SCORE>> <G? SCORE 0>>
           <TELL "Score is positive!" CR>)>>

<ROUTINE TEST-ARITHMETIC ()
    <TELL "5 - 3 = " <- 5 3> CR>
    <TELL "4 * 3 = " <* 4 3> CR>
    <TELL "10 / 3 = " </ 10 3> CR>>
```

**Test with Actual Zork I**:
```python
def test_load_zork1():
    """Verify Zork I loads without NotImplementedError."""
    loader = WorldLoader()
    world = loader.load_file("zork1/zork1.zil")
    assert world is not None

def test_zork1_start():
    """Verify Zork I starting room works."""
    engine = GameEngine.from_file("zork1/zork1.zil")
    engine.execute_command("look")
    output = engine.output.get_text()
    assert "West of House" in output
```

## Success Criteria

✅ **Foundation Complete**:
- Operation registry infrastructure implemented
- All 76 existing tests pass after registry integration

✅ **Migration Complete**:
- All 17 existing operations moved to registry pattern
- All tests still passing
- Old evaluator methods removed

✅ **New Operations Complete**:
- 30 new operations implemented with tests
- 100% test pass rate
- ~106+ total tests (76 existing + 30 new minimum)

✅ **Integration Success**:
- Zork I loads without NotImplementedError
- Can execute basic Zork I commands
- Game is playable (rooms, objects, verbs work)

✅ **Documentation Updated**:
- README lists all 47 operations
- Each operation documented with examples
- Architecture section explains registry pattern

## Implementation Timeline Estimate

- **Phase 1 (Foundation)**: 2 tasks, ~1-2 hours
- **Phase 2 (Migration)**: 17 tasks, ~4-6 hours
- **Phase 3 (New Operations)**: 30 tasks, ~10-12 hours
- **Phase 4 (Integration)**: 1 task, ~2-3 hours

**Total**: 50 tasks, ~17-23 hours development time

## References

- Current evaluator: `zil_interpreter/engine/evaluator.py`
- Existing tests: `tests/engine/test_evaluator.py`
- ZIL language reference: Original Zork I source (`zork1/`)
- Implementation summary: `docs/IMPLEMENTATION_SUMMARY.md`
