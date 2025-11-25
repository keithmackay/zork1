# Zork I Completion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the ZIL interpreter to play Zork I from source files.

**Architecture:** Extend existing operation registry pattern with 42 new operations across 6 batches. Add TableData infrastructure for array support. Follow TDD throughout.

**Tech Stack:** Python 3.11+, Lark parser, pytest, existing zil_interpreter codebase.

---

## Batch 1: Table Operations (CRITICAL)

Tables are the foundation - GET/PUT used 300+ times in Zork I.

---

### Task 1.1: TableData Class

**Files:**
- Create: `zil_interpreter/world/table_data.py`
- Test: `tests/world/test_table_data.py`

**Step 1: Write the failing test**

```python
# tests/world/test_table_data.py
"""Tests for TableData class."""
import pytest
from zil_interpreter.world.table_data import TableData


class TestTableData:
    """Tests for TableData word operations."""

    def test_create_table_with_words(self):
        """Table created with initial word values."""
        table = TableData(name="TEST", data=[10, 20, 30])
        assert table.name == "TEST"
        assert len(table.data) == 3

    def test_get_word_returns_value_at_index(self):
        """GET retrieves word at specified index."""
        table = TableData(name="TEST", data=[100, 200, 300])
        assert table.get_word(0) == 100
        assert table.get_word(1) == 200
        assert table.get_word(2) == 300

    def test_put_word_sets_value_at_index(self):
        """PUT sets word at specified index."""
        table = TableData(name="TEST", data=[0, 0, 0])
        table.put_word(1, 999)
        assert table.get_word(1) == 999

    def test_get_word_out_of_bounds_raises(self):
        """GET with invalid index raises IndexError."""
        table = TableData(name="TEST", data=[1, 2])
        with pytest.raises(IndexError):
            table.get_word(5)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/world/test_table_data.py -v`
Expected: FAIL with "No module named 'zil_interpreter.world.table_data'"

**Step 3: Write minimal implementation**

```python
# zil_interpreter/world/table_data.py
"""Table data structure for ZIL arrays."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TableData:
    """Represents a ZIL table (array of words)."""

    name: str
    data: List[int] = field(default_factory=list)

    def get_word(self, index: int) -> int:
        """Get word at index."""
        if index < 0 or index >= len(self.data):
            raise IndexError(f"Table index {index} out of range for table '{self.name}'")
        return self.data[index]

    def put_word(self, index: int, value: int) -> None:
        """Set word at index."""
        if index < 0 or index >= len(self.data):
            raise IndexError(f"Table index {index} out of range for table '{self.name}'")
        self.data[index] = value

    def __len__(self) -> int:
        """Return table length."""
        return len(self.data)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/world/test_table_data.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/world/table_data.py tests/world/test_table_data.py
git commit -m "feat(world): add TableData class for ZIL tables"
```

---

### Task 1.2: Byte Operations for TableData

**Files:**
- Modify: `zil_interpreter/world/table_data.py`
- Modify: `tests/world/test_table_data.py`

**Step 1: Write the failing tests**

```python
# Add to tests/world/test_table_data.py

class TestTableDataBytes:
    """Tests for TableData byte operations."""

    def test_get_byte_from_word_table(self):
        """GETB retrieves byte from word-based table."""
        # Word 0x0102 stored, get individual bytes
        table = TableData(name="TEST", data=[0x0102, 0x0304])
        # Byte 0 = high byte of word 0, Byte 1 = low byte of word 0
        assert table.get_byte(0) == 0x01
        assert table.get_byte(1) == 0x02
        assert table.get_byte(2) == 0x03
        assert table.get_byte(3) == 0x04

    def test_put_byte_modifies_word(self):
        """PUTB modifies specific byte within word."""
        table = TableData(name="TEST", data=[0x0000])
        table.put_byte(0, 0xAB)  # High byte
        assert table.get_word(0) == 0xAB00
        table.put_byte(1, 0xCD)  # Low byte
        assert table.get_word(0) == 0xABCD

    def test_get_byte_out_of_bounds_raises(self):
        """GETB with invalid byte index raises IndexError."""
        table = TableData(name="TEST", data=[0x0102])  # 2 bytes
        with pytest.raises(IndexError):
            table.get_byte(5)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/world/test_table_data.py::TestTableDataBytes -v`
Expected: FAIL with "AttributeError: 'TableData' object has no attribute 'get_byte'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/world/table_data.py TableData class

    def get_byte(self, byte_index: int) -> int:
        """Get byte at byte index (2 bytes per word)."""
        word_index = byte_index // 2
        if word_index >= len(self.data):
            raise IndexError(f"Byte index {byte_index} out of range for table '{self.name}'")
        word = self.data[word_index]
        if byte_index % 2 == 0:
            return (word >> 8) & 0xFF  # High byte
        else:
            return word & 0xFF  # Low byte

    def put_byte(self, byte_index: int, value: int) -> None:
        """Set byte at byte index."""
        word_index = byte_index // 2
        if word_index >= len(self.data):
            raise IndexError(f"Byte index {byte_index} out of range for table '{self.name}'")
        word = self.data[word_index]
        if byte_index % 2 == 0:
            # Set high byte, preserve low byte
            self.data[word_index] = ((value & 0xFF) << 8) | (word & 0xFF)
        else:
            # Preserve high byte, set low byte
            self.data[word_index] = (word & 0xFF00) | (value & 0xFF)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/world/test_table_data.py -v`
Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add zil_interpreter/world/table_data.py tests/world/test_table_data.py
git commit -m "feat(world): add byte operations to TableData"
```

---

### Task 1.3: Register Tables in WorldState

**Files:**
- Modify: `zil_interpreter/world/world_state.py`
- Modify: `tests/world/test_world_state.py`

**Step 1: Write the failing tests**

```python
# Add to tests/world/test_world_state.py
from zil_interpreter.world.table_data import TableData


class TestWorldStateTables:
    """Tests for table management in WorldState."""

    def test_register_table(self):
        """Can register a table in world state."""
        world = WorldState()
        table = TableData(name="DUMMY", data=[1, 2, 3])
        world.register_table("DUMMY", table)
        assert world.get_table("DUMMY") is table

    def test_get_unknown_table_raises(self):
        """Getting unknown table raises KeyError."""
        world = WorldState()
        with pytest.raises(KeyError):
            world.get_table("NONEXISTENT")

    def test_has_table(self):
        """Can check if table exists."""
        world = WorldState()
        table = TableData(name="TEST", data=[])
        world.register_table("TEST", table)
        assert world.has_table("TEST") is True
        assert world.has_table("NOPE") is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/world/test_world_state.py::TestWorldStateTables -v`
Expected: FAIL with "AttributeError: 'WorldState' object has no attribute 'register_table'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/world/world_state.py

# Add import at top:
from zil_interpreter.world.table_data import TableData

# Add to WorldState.__init__:
        self.tables: Dict[str, TableData] = {}

# Add methods to WorldState class:
    def register_table(self, name: str, table: TableData) -> None:
        """Register a table in the world."""
        self.tables[name] = table

    def get_table(self, name: str) -> TableData:
        """Get a table by name."""
        if name not in self.tables:
            raise KeyError(f"Unknown table: {name}")
        return self.tables[name]

    def has_table(self, name: str) -> bool:
        """Check if table exists."""
        return name in self.tables
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/world/test_world_state.py -v`
Expected: PASS (all tests including new ones)

**Step 5: Commit**

```bash
git add zil_interpreter/world/world_state.py tests/world/test_world_state.py
git commit -m "feat(world): add table registry to WorldState"
```

---

### Task 1.4: GET Operation

**Files:**
- Create: `zil_interpreter/engine/operations/table_access.py`
- Create: `tests/engine/operations/test_table_access.py`

**Step 1: Write the failing test**

```python
# tests/engine/operations/test_table_access.py
"""Tests for table access operations."""
import pytest
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.table_data import TableData
from zil_interpreter.engine.operations.table_access import GetOp


class TestGetOp:
    """Tests for GET operation."""

    def test_get_name(self):
        """Operation has correct name."""
        op = GetOp()
        assert op.name == "GET"

    def test_get_retrieves_word_from_table(self):
        """GET retrieves word at index from table."""
        world = WorldState()
        table = TableData(name="SCORES", data=[100, 200, 300])
        world.register_table("SCORES", table)

        op = GetOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        result = op.execute([Atom("SCORES"), Atom(1)], evaluator)
        assert result == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_table_access.py::TestGetOp -v`
Expected: FAIL with "No module named 'zil_interpreter.engine.operations.table_access'"

**Step 3: Write minimal implementation**

```python
# zil_interpreter/engine/operations/table_access.py
"""Table access operations: GET, PUT, GETB, PUTB."""
from typing import Any, List
from zil_interpreter.engine.operations.base import Operation


class GetOp(Operation):
    """GET - retrieve word from table by index."""

    @property
    def name(self) -> str:
        return "GET"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("GET requires table and index")
        table_name = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])
        table = evaluator.world.get_table(table_name)
        return table.get_word(index)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_table_access.py::TestGetOp -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/table_access.py tests/engine/operations/test_table_access.py
git commit -m "feat(ops): add GET operation for table word access"
```

---

### Task 1.5: PUT Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/table_access.py`
- Modify: `tests/engine/operations/test_table_access.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_table_access.py
from zil_interpreter.engine.operations.table_access import GetOp, PutOp


class TestPutOp:
    """Tests for PUT operation."""

    def test_put_name(self):
        """Operation has correct name."""
        op = PutOp()
        assert op.name == "PUT"

    def test_put_sets_word_in_table(self):
        """PUT sets word at index in table."""
        world = WorldState()
        table = TableData(name="DATA", data=[0, 0, 0])
        world.register_table("DATA", table)

        op = PutOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        result = op.execute([Atom("DATA"), Atom(1), Atom(999)], evaluator)

        # PUT returns the value set
        assert result == 999
        # Table is modified
        assert table.get_word(1) == 999
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_table_access.py::TestPutOp -v`
Expected: FAIL with "cannot import name 'PutOp'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/table_access.py

class PutOp(Operation):
    """PUT - set word in table by index."""

    @property
    def name(self) -> str:
        return "PUT"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 3:
            raise ValueError("PUT requires table, index, and value")
        table_name = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])
        value = evaluator.evaluate(args[2])
        table = evaluator.world.get_table(table_name)
        table.put_word(index, value)
        return value
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_table_access.py -v`
Expected: PASS (all tests)

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/table_access.py tests/engine/operations/test_table_access.py
git commit -m "feat(ops): add PUT operation for table word write"
```

---

### Task 1.6: GETB Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/table_access.py`
- Modify: `tests/engine/operations/test_table_access.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_table_access.py
from zil_interpreter.engine.operations.table_access import GetOp, PutOp, GetBOp


class TestGetBOp:
    """Tests for GETB operation."""

    def test_getb_name(self):
        """Operation has correct name."""
        op = GetBOp()
        assert op.name == "GETB"

    def test_getb_retrieves_byte_from_table(self):
        """GETB retrieves byte at byte index."""
        world = WorldState()
        table = TableData(name="BYTES", data=[0x1234, 0x5678])
        world.register_table("BYTES", table)

        op = GetBOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("BYTES"), Atom(0)], evaluator) == 0x12
        assert op.execute([Atom("BYTES"), Atom(1)], evaluator) == 0x34
        assert op.execute([Atom("BYTES"), Atom(2)], evaluator) == 0x56
        assert op.execute([Atom("BYTES"), Atom(3)], evaluator) == 0x78
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_table_access.py::TestGetBOp -v`
Expected: FAIL with "cannot import name 'GetBOp'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/table_access.py

class GetBOp(Operation):
    """GETB - retrieve byte from table by byte index."""

    @property
    def name(self) -> str:
        return "GETB"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("GETB requires table and byte index")
        table_name = evaluator.evaluate(args[0])
        byte_index = evaluator.evaluate(args[1])
        table = evaluator.world.get_table(table_name)
        return table.get_byte(byte_index)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_table_access.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/table_access.py tests/engine/operations/test_table_access.py
git commit -m "feat(ops): add GETB operation for table byte access"
```

---

### Task 1.7: PUTB Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/table_access.py`
- Modify: `tests/engine/operations/test_table_access.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_table_access.py
from zil_interpreter.engine.operations.table_access import GetOp, PutOp, GetBOp, PutBOp


class TestPutBOp:
    """Tests for PUTB operation."""

    def test_putb_name(self):
        """Operation has correct name."""
        op = PutBOp()
        assert op.name == "PUTB"

    def test_putb_sets_byte_in_table(self):
        """PUTB sets byte at byte index."""
        world = WorldState()
        table = TableData(name="DATA", data=[0x0000])
        world.register_table("DATA", table)

        op = PutBOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        op.execute([Atom("DATA"), Atom(0), Atom(0xAB)], evaluator)
        assert table.get_word(0) == 0xAB00

        op.execute([Atom("DATA"), Atom(1), Atom(0xCD)], evaluator)
        assert table.get_word(0) == 0xABCD
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_table_access.py::TestPutBOp -v`
Expected: FAIL with "cannot import name 'PutBOp'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/table_access.py

class PutBOp(Operation):
    """PUTB - set byte in table by byte index."""

    @property
    def name(self) -> str:
        return "PUTB"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 3:
            raise ValueError("PUTB requires table, byte index, and value")
        table_name = evaluator.evaluate(args[0])
        byte_index = evaluator.evaluate(args[1])
        value = evaluator.evaluate(args[2])
        table = evaluator.world.get_table(table_name)
        table.put_byte(byte_index, value)
        return value
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_table_access.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/table_access.py tests/engine/operations/test_table_access.py
git commit -m "feat(ops): add PUTB operation for table byte write"
```

---

### Task 1.8: Register Table Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/__init__.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_registry.py
def test_table_operations_registered():
    """Table operations are registered."""
    from zil_interpreter.engine.operations import get_operation
    assert get_operation("GET") is not None
    assert get_operation("PUT") is not None
    assert get_operation("GETB") is not None
    assert get_operation("PUTB") is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_registry.py::test_table_operations_registered -v`
Expected: FAIL with "KeyError: 'GET'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/__init__.py

# Add import:
from zil_interpreter.engine.operations.table_access import GetOp, PutOp, GetBOp, PutBOp

# Add to register_all() or OPERATIONS dict:
    GetOp(),
    PutOp(),
    GetBOp(),
    PutBOp(),
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/__init__.py
git commit -m "feat(ops): register table access operations"
```

---

### Task 1.9: Integration Test - Table Operations

**Files:**
- Modify: `tests/integration/test_zil_operations_integration.py`

**Step 1: Write integration test**

```python
# Add to tests/integration/test_zil_operations_integration.py

class TestTableOperationsIntegration:
    """Integration tests for table operations."""

    def test_pick_one_pattern(self):
        """Test PICK-ONE pattern from Zork I (random table selection)."""
        # Simulates: <GET ,DUMMY <RANDOM <GET ,DUMMY 0>>>
        world = WorldState()
        output = OutputBuffer()
        # DUMMY table: length at 0, then strings
        table = TableData(name="DUMMY", data=[3, 0, 1, 2])  # 3 items
        world.register_table("DUMMY", table)

        # Test GET retrieves length
        assert table.get_word(0) == 3

        # Test GET retrieves items
        assert table.get_word(1) == 0
        assert table.get_word(2) == 1
        assert table.get_word(3) == 2

    def test_parser_lexv_pattern(self):
        """Test parser LEXV table access pattern."""
        # P-LEXV is byte-addressed table
        world = WorldState()
        # Simulated lexer output: word count, then word entries
        lexv = TableData(name="P-LEXV", data=[0x0200, 0x4E4F])  # 2 words, "NO"
        world.register_table("P-LEXV", lexv)

        # GETB gets byte 0 (word count high byte)
        assert lexv.get_byte(0) == 0x02
```

**Step 2: Run test**

Run: `pytest tests/integration/test_zil_operations_integration.py::TestTableOperationsIntegration -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/integration/test_zil_operations_integration.py
git commit -m "test: add table operations integration tests"
```

---

## Batch 2: Bitwise Operations (CRITICAL)

---

### Task 2.1: BAND Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/bit_ops.py`
- Modify: `tests/engine/operations/test_bit_ops.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_bit_ops.py
from zil_interpreter.engine.operations.bit_ops import BandOp


class TestBandOp:
    """Tests for BAND operation."""

    def test_band_name(self):
        """Operation has correct name."""
        op = BandOp()
        assert op.name == "BAND"

    def test_band_two_values(self):
        """BAND performs bitwise AND."""
        op = BandOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        assert op.execute([0xFF, 0x0F], evaluator) == 0x0F
        assert op.execute([0b1100, 0b1010], evaluator) == 0b1000

    def test_band_multiple_values(self):
        """BAND chains multiple values."""
        op = BandOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        assert op.execute([0xFF, 0x0F, 0x03], evaluator) == 0x03
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_bit_ops.py::TestBandOp -v`
Expected: FAIL with "cannot import name 'BandOp'"

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/bit_ops.py

class BandOp(Operation):
    """BAND - bitwise AND."""

    @property
    def name(self) -> str:
        return "BAND"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("BAND requires at least 2 arguments")
        values = [evaluator.evaluate(a) for a in args]
        result = values[0]
        for v in values[1:]:
            result &= v
        return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_bit_ops.py::TestBandOp -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/bit_ops.py tests/engine/operations/test_bit_ops.py
git commit -m "feat(ops): add BAND bitwise AND operation"
```

---

### Task 2.2: BOR Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/bit_ops.py`
- Modify: `tests/engine/operations/test_bit_ops.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_bit_ops.py
from zil_interpreter.engine.operations.bit_ops import BandOp, BorOp


class TestBorOp:
    """Tests for BOR operation."""

    def test_bor_name(self):
        """Operation has correct name."""
        op = BorOp()
        assert op.name == "BOR"

    def test_bor_two_values(self):
        """BOR performs bitwise OR."""
        op = BorOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        assert op.execute([0xF0, 0x0F], evaluator) == 0xFF
        assert op.execute([0b1100, 0b0011], evaluator) == 0b1111

    def test_bor_multiple_values(self):
        """BOR chains multiple values."""
        op = BorOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        assert op.execute([0x01, 0x02, 0x04], evaluator) == 0x07
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_bit_ops.py::TestBorOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/bit_ops.py

class BorOp(Operation):
    """BOR - bitwise OR."""

    @property
    def name(self) -> str:
        return "BOR"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("BOR requires at least 2 arguments")
        values = [evaluator.evaluate(a) for a in args]
        result = values[0]
        for v in values[1:]:
            result |= v
        return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_bit_ops.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/bit_ops.py tests/engine/operations/test_bit_ops.py
git commit -m "feat(ops): add BOR bitwise OR operation"
```

---

### Task 2.3: BCOM Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/bit_ops.py`
- Modify: `tests/engine/operations/test_bit_ops.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_bit_ops.py
from zil_interpreter.engine.operations.bit_ops import BandOp, BorOp, BcomOp


class TestBcomOp:
    """Tests for BCOM operation."""

    def test_bcom_name(self):
        """Operation has correct name."""
        op = BcomOp()
        assert op.name == "BCOM"

    def test_bcom_inverts_bits(self):
        """BCOM performs bitwise complement."""
        op = BcomOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        # Use 16-bit mask for ZIL compatibility
        assert op.execute([0x0000], evaluator) == 0xFFFF
        assert op.execute([0xFFFF], evaluator) == 0x0000
        assert op.execute([0x00FF], evaluator) == 0xFF00
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_bit_ops.py::TestBcomOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/bit_ops.py

class BcomOp(Operation):
    """BCOM - bitwise complement (NOT)."""

    @property
    def name(self) -> str:
        return "BCOM"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("BCOM requires 1 argument")
        value = evaluator.evaluate(args[0])
        # ZIL uses 16-bit words
        return (~value) & 0xFFFF
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_bit_ops.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/bit_ops.py tests/engine/operations/test_bit_ops.py
git commit -m "feat(ops): add BCOM bitwise complement operation"
```

---

### Task 2.4: BTST Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/bit_ops.py`
- Modify: `tests/engine/operations/test_bit_ops.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_bit_ops.py
from zil_interpreter.engine.operations.bit_ops import BandOp, BorOp, BcomOp, BtstOp


class TestBtstOp:
    """Tests for BTST operation."""

    def test_btst_name(self):
        """Operation has correct name."""
        op = BtstOp()
        assert op.name == "BTST"

    def test_btst_true_when_all_bits_set(self):
        """BTST returns true when all mask bits are set."""
        op = BtstOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        assert op.execute([0xFF, 0x0F], evaluator) is True
        assert op.execute([0b1111, 0b0101], evaluator) is True

    def test_btst_false_when_bits_missing(self):
        """BTST returns false when mask bits not all set."""
        op = BtstOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()
        assert op.execute([0x0F, 0xFF], evaluator) is False
        assert op.execute([0b1010, 0b0101], evaluator) is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_bit_ops.py::TestBtstOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/bit_ops.py

class BtstOp(Operation):
    """BTST - test if all bits in mask are set."""

    @property
    def name(self) -> str:
        return "BTST"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("BTST requires value and mask")
        value = evaluator.evaluate(args[0])
        mask = evaluator.evaluate(args[1])
        return (value & mask) == mask
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_bit_ops.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/bit_ops.py tests/engine/operations/test_bit_ops.py
git commit -m "feat(ops): add BTST bit test operation"
```

---

### Task 2.5: Register Bitwise Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/__init__.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_registry.py
def test_bitwise_operations_registered():
    """Bitwise operations are registered."""
    from zil_interpreter.engine.operations import get_operation
    assert get_operation("BAND") is not None
    assert get_operation("BOR") is not None
    assert get_operation("BCOM") is not None
    assert get_operation("BTST") is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_registry.py::test_bitwise_operations_registered -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/__init__.py

# Add import:
from zil_interpreter.engine.operations.bit_ops import BandOp, BorOp, BcomOp, BtstOp

# Add to OPERATIONS list:
    BandOp(),
    BorOp(),
    BcomOp(),
    BtstOp(),
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/__init__.py
git commit -m "feat(ops): register bitwise operations"
```

---

### Task 2.6: DLESS? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/comparison.py`
- Modify: `tests/engine/operations/test_comparison.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_comparison.py
from zil_interpreter.engine.operations.comparison import DlessOp


class TestDlessOp:
    """Tests for DLESS? operation."""

    def test_dless_name(self):
        """Operation has correct name."""
        op = DlessOp()
        assert op.name == "DLESS?"

    def test_dless_decrements_and_tests(self):
        """DLESS? decrements global and returns true if now < value."""
        world = WorldState()
        world.set_global("COUNTER", 5)

        op = DlessOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)

        # COUNTER=5, decrement to 4, test if 4 < 5 -> True
        result = op.execute([Atom("COUNTER"), Atom(5)], evaluator)
        assert result is True
        assert world.get_global("COUNTER") == 4

        # COUNTER=4, decrement to 3, test if 3 < 3 -> False
        result = op.execute([Atom("COUNTER"), Atom(3)], evaluator)
        assert result is False
        assert world.get_global("COUNTER") == 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_comparison.py::TestDlessOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/comparison.py

class DlessOp(Operation):
    """DLESS? - decrement global, return true if now < value."""

    @property
    def name(self) -> str:
        return "DLESS?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("DLESS? requires variable name and value")
        var_name = evaluator.evaluate(args[0])
        test_value = evaluator.evaluate(args[1])

        current = evaluator.world.get_global(var_name)
        new_value = current - 1
        evaluator.world.set_global(var_name, new_value)

        return new_value < test_value
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_comparison.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/comparison.py tests/engine/operations/test_comparison.py
git commit -m "feat(ops): add DLESS? decrement and test operation"
```

---

### Task 2.7: IGRTR? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/comparison.py`
- Modify: `tests/engine/operations/test_comparison.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_comparison.py
from zil_interpreter.engine.operations.comparison import DlessOp, IgrtrOp


class TestIgrtrOp:
    """Tests for IGRTR? operation."""

    def test_igrtr_name(self):
        """Operation has correct name."""
        op = IgrtrOp()
        assert op.name == "IGRTR?"

    def test_igrtr_increments_and_tests(self):
        """IGRTR? increments global and returns true if now > value."""
        world = WorldState()
        world.set_global("COUNTER", 3)

        op = IgrtrOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)

        # COUNTER=3, increment to 4, test if 4 > 3 -> True
        result = op.execute([Atom("COUNTER"), Atom(3)], evaluator)
        assert result is True
        assert world.get_global("COUNTER") == 4

        # COUNTER=4, increment to 5, test if 5 > 6 -> False
        result = op.execute([Atom("COUNTER"), Atom(6)], evaluator)
        assert result is False
        assert world.get_global("COUNTER") == 5
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_comparison.py::TestIgrtrOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/comparison.py

class IgrtrOp(Operation):
    """IGRTR? - increment global, return true if now > value."""

    @property
    def name(self) -> str:
        return "IGRTR?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("IGRTR? requires variable name and value")
        var_name = evaluator.evaluate(args[0])
        test_value = evaluator.evaluate(args[1])

        current = evaluator.world.get_global(var_name)
        new_value = current + 1
        evaluator.world.set_global(var_name, new_value)

        return new_value > test_value
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_comparison.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/comparison.py tests/engine/operations/test_comparison.py
git commit -m "feat(ops): add IGRTR? increment and test operation"
```

---

## Batch 3: Print Operations

---

### Task 3.1: PRINTD Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/io.py`
- Modify: `tests/engine/operations/test_io.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_io.py
from zil_interpreter.engine.operations.io import PrintdOp


class TestPrintdOp:
    """Tests for PRINTD operation."""

    def test_printd_name(self):
        """Operation has correct name."""
        op = PrintdOp()
        assert op.name == "PRINTD"

    def test_printd_prints_object_desc(self):
        """PRINTD prints object's DESC property."""
        world = WorldState()
        output = OutputBuffer()
        obj = GameObject(name="LAMP")
        obj.properties["DESC"] = "brass lantern"
        world.register_object(obj)

        op = PrintdOp()

        class MockEvaluator:
            def __init__(self, w, o):
                self.world = w
                self.output = o

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world, output)
        op.execute([Atom("LAMP")], evaluator)

        assert output.get_output() == "brass lantern"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_io.py::TestPrintdOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/io.py

class PrintdOp(Operation):
    """PRINTD - print object's DESC property."""

    @property
    def name(self) -> str:
        return "PRINTD"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("PRINTD requires object")
        obj_name = evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_name)
        desc = obj.properties.get("DESC", obj_name)
        evaluator.output.write(str(desc))
        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/io.py tests/engine/operations/test_io.py
git commit -m "feat(ops): add PRINTD operation for object descriptions"
```

---

### Task 3.2: PRINTN Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/io.py`
- Modify: `tests/engine/operations/test_io.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_io.py
from zil_interpreter.engine.operations.io import PrintdOp, PrintnOp


class TestPrintnOp:
    """Tests for PRINTN operation."""

    def test_printn_name(self):
        """Operation has correct name."""
        op = PrintnOp()
        assert op.name == "PRINTN"

    def test_printn_prints_number(self):
        """PRINTN prints number as string."""
        output = OutputBuffer()

        op = PrintnOp()

        class MockEvaluator:
            def __init__(self, o):
                self.output = o

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator(output)
        op.execute([42], evaluator)
        assert output.get_output() == "42"

    def test_printn_prints_negative(self):
        """PRINTN prints negative numbers."""
        output = OutputBuffer()

        op = PrintnOp()

        class MockEvaluator:
            def __init__(self, o):
                self.output = o

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator(output)
        op.execute([-123], evaluator)
        assert output.get_output() == "-123"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_io.py::TestPrintnOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/io.py

class PrintnOp(Operation):
    """PRINTN - print number."""

    @property
    def name(self) -> str:
        return "PRINTN"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("PRINTN requires number")
        num = evaluator.evaluate(args[0])
        evaluator.output.write(str(num))
        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/io.py tests/engine/operations/test_io.py
git commit -m "feat(ops): add PRINTN operation for number output"
```

---

### Task 3.3: PRINT and PRINTI Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/io.py`
- Modify: `tests/engine/operations/test_io.py`

**Step 1: Write the failing tests**

```python
# Add to tests/engine/operations/test_io.py
from zil_interpreter.engine.operations.io import PrintOp, PrintiOp


class TestPrintOp:
    """Tests for PRINT operation."""

    def test_print_name(self):
        """Operation has correct name."""
        op = PrintOp()
        assert op.name == "PRINT"

    def test_print_prints_global_string(self):
        """PRINT prints string from global variable."""
        world = WorldState()
        output = OutputBuffer()
        world.set_global("MSG", "Hello, Adventurer!")

        op = PrintOp()

        class MockEvaluator:
            def __init__(self, w, o):
                self.world = w
                self.output = o

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world, output)
        op.execute([Atom("MSG")], evaluator)
        assert output.get_output() == "Hello, Adventurer!"


class TestPrintiOp:
    """Tests for PRINTI operation."""

    def test_printi_name(self):
        """Operation has correct name."""
        op = PrintiOp()
        assert op.name == "PRINTI"

    def test_printi_prints_immediate_string(self):
        """PRINTI prints immediate string value."""
        output = OutputBuffer()

        op = PrintiOp()

        class MockEvaluator:
            def __init__(self, o):
                self.output = o

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator(output)
        op.execute(["You are in a maze."], evaluator)
        assert output.get_output() == "You are in a maze."
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_io.py::TestPrintOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/io.py

class PrintOp(Operation):
    """PRINT - print string from global variable."""

    @property
    def name(self) -> str:
        return "PRINT"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("PRINT requires variable name")
        var_name = evaluator.evaluate(args[0])
        value = evaluator.world.get_global(var_name)
        evaluator.output.write(str(value))
        return None


class PrintiOp(Operation):
    """PRINTI - print immediate string."""

    @property
    def name(self) -> str:
        return "PRINTI"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("PRINTI requires string")
        text = evaluator.evaluate(args[0])
        evaluator.output.write(str(text))
        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/io.py tests/engine/operations/test_io.py
git commit -m "feat(ops): add PRINT and PRINTI operations"
```

---

### Task 3.4: CRLF Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/io.py`
- Modify: `tests/engine/operations/test_io.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_io.py
from zil_interpreter.engine.operations.io import CrlfOp


class TestCrlfOp:
    """Tests for CRLF operation."""

    def test_crlf_name(self):
        """Operation has correct name."""
        op = CrlfOp()
        assert op.name == "CRLF"

    def test_crlf_prints_newline(self):
        """CRLF prints newline character."""
        output = OutputBuffer()

        op = CrlfOp()

        class MockEvaluator:
            def __init__(self, o):
                self.output = o

            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator(output)
        op.execute([], evaluator)
        assert output.get_output() == "\n"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_io.py::TestCrlfOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/io.py

class CrlfOp(Operation):
    """CRLF - print newline."""

    @property
    def name(self) -> str:
        return "CRLF"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        evaluator.output.write("\n")
        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_io.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/io.py tests/engine/operations/test_io.py
git commit -m "feat(ops): add CRLF newline operation"
```

---

### Task 3.5: Register Print Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/__init__.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_registry.py
def test_print_operations_registered():
    """Print operations are registered."""
    from zil_interpreter.engine.operations import get_operation
    assert get_operation("PRINT") is not None
    assert get_operation("PRINTI") is not None
    assert get_operation("PRINTD") is not None
    assert get_operation("PRINTN") is not None
    assert get_operation("CRLF") is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_registry.py::test_print_operations_registered -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add imports and registrations to zil_interpreter/engine/operations/__init__.py
from zil_interpreter.engine.operations.io import PrintOp, PrintiOp, PrintdOp, PrintnOp, CrlfOp

# Add to OPERATIONS:
    PrintOp(),
    PrintiOp(),
    PrintdOp(),
    PrintnOp(),
    CrlfOp(),
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/__init__.py
git commit -m "feat(ops): register print operations"
```

---

## Batch 4: Game Logic Operations

---

### Task 4.1: RANDOM Operation

**Files:**
- Create: `zil_interpreter/engine/operations/game_logic.py`
- Create: `tests/engine/operations/test_game_logic.py`

**Step 1: Write the failing test**

```python
# tests/engine/operations/test_game_logic.py
"""Tests for game logic operations."""
import pytest
from zil_interpreter.engine.operations.game_logic import RandomOp


class TestRandomOp:
    """Tests for RANDOM operation."""

    def test_random_name(self):
        """Operation has correct name."""
        op = RandomOp()
        assert op.name == "RANDOM"

    def test_random_returns_in_range(self):
        """RANDOM returns value between 1 and max."""
        op = RandomOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()

        # Test many times to ensure range
        for _ in range(100):
            result = op.execute([10], evaluator)
            assert 1 <= result <= 10

    def test_random_returns_1_for_max_1(self):
        """RANDOM with max 1 always returns 1."""
        op = RandomOp()

        class MockEvaluator:
            def evaluate(self, arg):
                return arg

        evaluator = MockEvaluator()

        for _ in range(10):
            result = op.execute([1], evaluator)
            assert result == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_game_logic.py::TestRandomOp -v`
Expected: FAIL with "No module named"

**Step 3: Write minimal implementation**

```python
# zil_interpreter/engine/operations/game_logic.py
"""Game logic operations: RANDOM, ACCESSIBLE?, LIT?, etc."""
import random
from typing import Any, List
from zil_interpreter.engine.operations.base import Operation


class RandomOp(Operation):
    """RANDOM - generate random number 1 to max."""

    @property
    def name(self) -> str:
        return "RANDOM"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("RANDOM requires max value")
        max_val = evaluator.evaluate(args[0])
        return random.randint(1, max_val)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_game_logic.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/game_logic.py tests/engine/operations/test_game_logic.py
git commit -m "feat(ops): add RANDOM operation"
```

---

### Task 4.2: META-LOC Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/game_logic.py`
- Modify: `tests/engine/operations/test_game_logic.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_game_logic.py
from zil_interpreter.engine.operations.game_logic import RandomOp, MetaLocOp
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject


class TestMetaLocOp:
    """Tests for META-LOC operation."""

    def test_meta_loc_name(self):
        """Operation has correct name."""
        op = MetaLocOp()
        assert op.name == "META-LOC"

    def test_meta_loc_finds_room(self):
        """META-LOC returns ultimate container (room)."""
        world = WorldState()

        # Create hierarchy: ROOM -> PLAYER -> BAG -> LAMP
        room = GameObject(name="LIVING-ROOM")
        room.flags.add("ROOMBIT")
        world.register_object(room)

        player = GameObject(name="PLAYER", parent="LIVING-ROOM")
        world.register_object(player)

        bag = GameObject(name="BAG", parent="PLAYER")
        world.register_object(bag)

        lamp = GameObject(name="LAMP", parent="BAG")
        world.register_object(lamp)

        op = MetaLocOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        result = op.execute([Atom("LAMP")], evaluator)
        assert result == "LIVING-ROOM"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_game_logic.py::TestMetaLocOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/game_logic.py

class MetaLocOp(Operation):
    """META-LOC - find ultimate container (room)."""

    @property
    def name(self) -> str:
        return "META-LOC"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("META-LOC requires object")
        obj_name = evaluator.evaluate(args[0])

        # Traverse parent chain until we find a room
        current = obj_name
        visited = set()
        while current and current not in visited:
            visited.add(current)
            obj = evaluator.world.get_object(current)
            if "ROOMBIT" in obj.flags:
                return current
            current = obj.parent

        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_game_logic.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/game_logic.py tests/engine/operations/test_game_logic.py
git commit -m "feat(ops): add META-LOC operation"
```

---

### Task 4.3: LIT? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/game_logic.py`
- Modify: `tests/engine/operations/test_game_logic.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_game_logic.py
from zil_interpreter.engine.operations.game_logic import LitOp


class TestLitOp:
    """Tests for LIT? operation."""

    def test_lit_name(self):
        """Operation has correct name."""
        op = LitOp()
        assert op.name == "LIT?"

    def test_lit_true_for_room_with_light(self):
        """LIT? returns true if room has LIGHTBIT."""
        world = WorldState()
        room = GameObject(name="KITCHEN")
        room.flags.add("LIGHTBIT")
        world.register_object(room)

        op = LitOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("KITCHEN")], evaluator) is True

    def test_lit_false_for_dark_room(self):
        """LIT? returns false if room has no light."""
        world = WorldState()
        room = GameObject(name="CELLAR")
        world.register_object(room)

        op = LitOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("CELLAR")], evaluator) is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_game_logic.py::TestLitOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/game_logic.py

class LitOp(Operation):
    """LIT? - check if location has light."""

    @property
    def name(self) -> str:
        return "LIT?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("LIT? requires room")
        room_name = evaluator.evaluate(args[0])
        room = evaluator.world.get_object(room_name)
        return "LIGHTBIT" in room.flags
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_game_logic.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/game_logic.py tests/engine/operations/test_game_logic.py
git commit -m "feat(ops): add LIT? operation"
```

---

### Task 4.4: ACCESSIBLE? Operation

**Files:**
- Modify: `zil_interpreter/engine/operations/game_logic.py`
- Modify: `tests/engine/operations/test_game_logic.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_game_logic.py
from zil_interpreter.engine.operations.game_logic import AccessibleOp


class TestAccessibleOp:
    """Tests for ACCESSIBLE? operation."""

    def test_accessible_name(self):
        """Operation has correct name."""
        op = AccessibleOp()
        assert op.name == "ACCESSIBLE?"

    def test_accessible_true_in_room(self):
        """ACCESSIBLE? true for objects in current room."""
        world = WorldState()
        room = GameObject(name="KITCHEN")
        world.register_object(room)
        lamp = GameObject(name="LAMP", parent="KITCHEN")
        world.register_object(lamp)
        world.set_global("HERE", "KITCHEN")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("LAMP")], evaluator) is True

    def test_accessible_true_if_held(self):
        """ACCESSIBLE? true for objects held by player."""
        world = WorldState()
        player = GameObject(name="PLAYER")
        world.register_object(player)
        sword = GameObject(name="SWORD", parent="PLAYER")
        world.register_object(sword)
        world.set_global("PLAYER", "PLAYER")
        world.set_global("HERE", "KITCHEN")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("SWORD")], evaluator) is True

    def test_accessible_false_in_other_room(self):
        """ACCESSIBLE? false for objects in other rooms."""
        world = WorldState()
        room1 = GameObject(name="KITCHEN")
        world.register_object(room1)
        room2 = GameObject(name="CELLAR")
        world.register_object(room2)
        lamp = GameObject(name="LAMP", parent="CELLAR")
        world.register_object(lamp)
        world.set_global("HERE", "KITCHEN")
        world.set_global("PLAYER", "PLAYER")

        op = AccessibleOp()

        class MockEvaluator:
            def __init__(self, w):
                self.world = w

            def evaluate(self, arg):
                if hasattr(arg, "value"):
                    return arg.value
                return arg

        class Atom:
            def __init__(self, v):
                self.value = v

        evaluator = MockEvaluator(world)
        assert op.execute([Atom("LAMP")], evaluator) is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_game_logic.py::TestAccessibleOp -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/game_logic.py

class AccessibleOp(Operation):
    """ACCESSIBLE? - check if object can be reached."""

    @property
    def name(self) -> str:
        return "ACCESSIBLE?"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 1:
            raise ValueError("ACCESSIBLE? requires object")
        obj_name = evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_name)

        here = evaluator.world.get_global("HERE")
        player = evaluator.world.get_global("PLAYER")

        # Directly in room or held by player
        if obj.parent == here or obj.parent == player:
            return True

        # Check if in open container in room or held
        parent = obj.parent
        while parent:
            parent_obj = evaluator.world.get_object(parent)
            if parent == here or parent == player:
                return True
            # If parent is closed container, not accessible
            if "CONTAINERBIT" in parent_obj.flags and "OPENBIT" not in parent_obj.flags:
                return False
            parent = parent_obj.parent

        return False
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_game_logic.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/game_logic.py tests/engine/operations/test_game_logic.py
git commit -m "feat(ops): add ACCESSIBLE? operation"
```

---

### Task 4.5: Register Game Logic Operations

**Files:**
- Modify: `zil_interpreter/engine/operations/__init__.py`

**Step 1: Write the failing test**

```python
# Add to tests/engine/operations/test_registry.py
def test_game_logic_operations_registered():
    """Game logic operations are registered."""
    from zil_interpreter.engine.operations import get_operation
    assert get_operation("RANDOM") is not None
    assert get_operation("META-LOC") is not None
    assert get_operation("LIT?") is not None
    assert get_operation("ACCESSIBLE?") is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/engine/operations/test_registry.py::test_game_logic_operations_registered -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# Add to zil_interpreter/engine/operations/__init__.py
from zil_interpreter.engine.operations.game_logic import (
    RandomOp, MetaLocOp, LitOp, AccessibleOp
)

# Add to OPERATIONS:
    RandomOp(),
    MetaLocOp(),
    LitOp(),
    AccessibleOp(),
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/engine/operations/test_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add zil_interpreter/engine/operations/__init__.py
git commit -m "feat(ops): register game logic operations"
```

---

## Validation Milestone 1

After completing Batches 1-4, run full test suite:

```bash
pytest -v
```

Expected: All tests pass (~50+ new tests)

Then attempt to load Zork I:

```bash
python -c "
from zil_interpreter.loader.world_loader import WorldLoader
from zil_interpreter.runtime.output_buffer import OutputBuffer

output = OutputBuffer()
loader = WorldLoader(output)
# This will likely fail until loader enhancements are complete
# but we can see how far we get
"
```

---

## Remaining Batches (5-6)

Batches 5 and 6 follow the same TDD pattern for:

**Batch 5: Control Flow**
- PROG, AGAIN, DO, MAP-CONTENTS, APPLY
- JIGS-UP, YES?, QUIT

**Batch 6: System Operations**
- QUEUE, ENABLE, DISABLE, INT, DEQUEUE
- READ, LEX, WORD?

Each task follows the same structure:
1. Write failing test
2. Run test to verify failure
3. Write minimal implementation
4. Run test to verify pass
5. Commit

---

## Summary

| Batch | Tasks | Operations | Est. Tests |
|-------|-------|------------|------------|
| 1 | 1.1-1.9 | GET, PUT, GETB, PUTB + infrastructure | ~40 |
| 2 | 2.1-2.7 | BAND, BOR, BCOM, BTST, DLESS?, IGRTR? | ~35 |
| 3 | 3.1-3.5 | PRINT, PRINTI, PRINTD, PRINTN, CRLF | ~25 |
| 4 | 4.1-4.5 | RANDOM, META-LOC, LIT?, ACCESSIBLE? | ~35 |
| 5 | TBD | Control flow operations | ~40 |
| 6 | TBD | System operations | ~30 |

**Total: ~205 new tests, 42 operations**
