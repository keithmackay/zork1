# Zork I ZIL Interpreter Completion Design

**Date:** 2025-11-25
**Goal:** Complete ZIL source interpreter sufficient to play Zork I
**Approach:** Incremental TDD batches (5-8 operations per batch)

---

## Executive Summary

Extend the existing ZIL interpreter (47 operations, 349 tests) to support all operations required to play Zork I from source. This requires implementing ~42 additional operations across 6 batches, plus loader enhancements for tables and multi-file support.

## Current State

- **Operations implemented:** 47
- **Tests passing:** 349/350
- **Architecture:** Parser → World Model → Engine → CLI
- **Can run:** Simple test games

## Gap Analysis

Based on analysis of Zork I source files (zork1.zil, gmain.zil, gverbs.zil, 1actions.zil, gparser.zil):

- **Total operations needed:** ~88 critical operations
- **Currently missing:** ~42 operations (Priority 1-2)
- **Blocking issues:** Table access, bitwise operations, print variants

---

## Architecture Additions

### 1. Table Infrastructure

```python
@dataclass
class TableData:
    """Represents a ZIL table (array of words or bytes)."""
    name: str
    mode: Literal["words", "bytes"]
    data: list[int]

    def get_word(self, index: int) -> int:
        """Get word at index (2 bytes)."""
        return self.data[index]

    def put_word(self, index: int, value: int) -> None:
        """Set word at index."""
        self.data[index] = value

    def get_byte(self, index: int) -> int:
        """Get single byte at index."""
        # Implementation depends on table mode
        pass

    def put_byte(self, index: int, value: int) -> None:
        """Set single byte at index."""
        pass
```

**WorldState additions:**
```python
class WorldState:
    # Existing...
    tables: Dict[str, TableData] = field(default_factory=dict)

    def register_table(self, name: str, table: TableData) -> None
    def get_table(self, name: str) -> TableData
```

### 2. Interrupt Manager

```python
@dataclass
class Interrupt:
    """Scheduled game interrupt/daemon."""
    name: str
    routine: str
    turns_remaining: int
    enabled: bool = True

class InterruptManager:
    """Manages timed game events."""
    interrupts: Dict[str, Interrupt]

    def tick(self) -> list[str]:
        """Advance turn, return routines to execute."""
        pass

    def queue(self, name: str, turns: int) -> None:
        """Schedule interrupt."""
        pass

    def enable(self, name: str) -> None:
        """Enable interrupt."""
        pass

    def disable(self, name: str) -> None:
        """Disable interrupt."""
        pass
```

---

## Implementation Batches

### Batch 1: Table Operations (CRITICAL)

**Operations (8):**
| Operation | Description | Zork I Usage |
|-----------|-------------|--------------|
| GET | Get word from table by index | 150+ uses |
| PUT | Set word in table by index | 50+ uses |
| GETB | Get byte from table | 80+ uses |
| PUTB | Set byte in table | 30+ uses |
| GETPT | Get property table pointer | 20+ uses |
| PTSIZE | Get property table size | 15+ uses |
| NEXTP | Get next property | 10+ uses |
| VALUE | Dereference variable | 40+ uses |

**Implementation:**
```python
class GetOp(Operation):
    name = "GET"
    def execute(self, args, evaluator):
        table_name = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])
        table = evaluator.world.get_table(table_name)
        return table.get_word(index)

class PutOp(Operation):
    name = "PUT"
    def execute(self, args, evaluator):
        table_name = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])
        value = evaluator.evaluate(args[2])
        table = evaluator.world.get_table(table_name)
        table.put_word(index, value)
        return value
```

**Tests (~40):**
- Unit tests for each operation
- Edge cases: empty tables, out of bounds, negative indices
- Integration: PICK-ONE pattern from Zork I

---

### Batch 2: Bitwise Operations (CRITICAL)

**Operations (7):**
| Operation | Description | Zork I Usage |
|-----------|-------------|--------------|
| BAND | Bitwise AND | 80+ uses |
| BOR | Bitwise OR | 40+ uses |
| BCOM | Bitwise complement | 10+ uses |
| BTST | Test if bits set | 150+ uses |
| N==? | Not equal (numeric) | 30+ uses |
| DLESS? | Decrement and test < | 20+ uses |
| IGRTR? | Increment and test > | 15+ uses |

**Implementation:**
```python
class BitwiseAndOp(Operation):
    name = "BAND"
    def execute(self, args, evaluator):
        values = [evaluator.evaluate(a) for a in args]
        result = values[0]
        for v in values[1:]:
            result &= v
        return result

class BitTestOp(Operation):
    name = "BTST"
    def execute(self, args, evaluator):
        value = evaluator.evaluate(args[0])
        mask = evaluator.evaluate(args[1])
        return (value & mask) == mask
```

**Tests (~35):**
- All bitwise combinations
- BTST with various masks
- DLESS?/IGRTR? with global modification

---

### Batch 3: Print Operations (CRITICAL)

**Operations (5):**
| Operation | Description | Zork I Usage |
|-----------|-------------|--------------|
| PRINT | Print global string | 100+ uses |
| PRINTI | Print immediate string | 200+ uses |
| PRINTD | Print object DESC | 80+ uses |
| PRINTN | Print number | 50+ uses |
| CRLF | Print newline | 100+ uses |

**Implementation:**
```python
class PrintDescOp(Operation):
    name = "PRINTD"
    def execute(self, args, evaluator):
        obj_name = evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_name)
        desc = obj.properties.get("DESC", obj_name)
        evaluator.output.write(str(desc))
        return None

class PrintNumberOp(Operation):
    name = "PRINTN"
    def execute(self, args, evaluator):
        num = evaluator.evaluate(args[0])
        evaluator.output.write(str(num))
        return None
```

**Tests (~25):**
- Each print variant
- Object DESC resolution
- Number formatting

---

### Batch 4: Game Logic Operations (HIGH)

**Operations (6):**
| Operation | Description | Zork I Usage |
|-----------|-------------|--------------|
| ACCESSIBLE? | Object reachable | 40+ uses |
| VISIBLE? | Object visible | 30+ uses |
| LIT? | Location has light | 25+ uses |
| META-LOC | Ultimate container | 20+ uses |
| GLOBAL-IN? | Is global object | 15+ uses |
| RANDOM | Random number | 35+ uses |

**Implementation:**
```python
class AccessibleOp(Operation):
    name = "ACCESSIBLE?"
    def execute(self, args, evaluator):
        obj_name = evaluator.evaluate(args[0])
        obj = evaluator.world.get_object(obj_name)
        here = evaluator.world.get_global("HERE")
        player = evaluator.world.get_global("PLAYER")

        # Accessible if: in room, held by player, or in open container
        if obj.parent == here or obj.parent == player:
            return True
        # Check container chain...
        return self._check_container_chain(obj, here, player, evaluator.world)

class RandomOp(Operation):
    name = "RANDOM"
    def execute(self, args, evaluator):
        max_val = evaluator.evaluate(args[0])
        import random
        return random.randint(1, max_val)
```

**Tests (~35):**
- Accessibility in various scenarios
- Light propagation
- Random distribution

---

### Batch 5: Control Flow Operations (HIGH)

**Operations (8):**
| Operation | Description | Zork I Usage |
|-----------|-------------|--------------|
| PROG | Block scope | 30+ uses |
| AGAIN | Loop restart | 25+ uses |
| DO | Counted loop | 20+ uses |
| MAP-CONTENTS | Iterate children | 15+ uses |
| APPLY | Call by reference | 10+ uses |
| JIGS-UP | Game over | 20+ uses |
| YES? | Y/N prompt | 10+ uses |
| QUIT | Exit game | 5+ uses |

**Implementation:**
```python
class ProgOp(Operation):
    name = "PROG"
    def execute(self, args, evaluator):
        bindings = args[0].children if args else []
        body = args[1:] if len(args) > 1 else []

        with evaluator.local_scope(bindings):
            for expr in body:
                result = evaluator.evaluate(expr)
                if evaluator.returning:
                    return result
            return None

class JigsUpOp(Operation):
    name = "JIGS-UP"
    def execute(self, args, evaluator):
        message = evaluator.evaluate(args[0]) if args else "You have died."
        evaluator.output.write(f"\n{message}\n")
        evaluator.world.set_global("DEAD", True)
        raise GameOverException(message)
```

**Tests (~40):**
- PROG/AGAIN interaction
- DO loop counts
- Game termination states

---

### Batch 6: System Operations (MEDIUM)

**Operations (8):**
| Operation | Description | Zork I Usage |
|-----------|-------------|--------------|
| QUEUE | Schedule interrupt | 15+ uses |
| ENABLE | Enable interrupt | 10+ uses |
| DISABLE | Disable interrupt | 10+ uses |
| INT | Get interrupt ref | 15+ uses |
| DEQUEUE | Cancel interrupt | 5+ uses |
| READ | Read input | 5+ uses |
| LEX | Tokenize input | 5+ uses |
| WORD? | Check word type | 10+ uses |

**Tests (~30):**
- Interrupt scheduling/firing
- Parser tokenization

---

## Loader Enhancements

### Table Declarations

```zil
<TABLE DUMMY "foo" "bar" "baz">
<ITABLE 10 0>                    ; 10 zeros
<LTABLE "a" "b" "c">             ; Length-prefixed
```

**Parser additions:**
- Recognize TABLE, ITABLE, LTABLE forms
- Extract initialization values
- Create TableData in WorldState

### Multi-File Support

```zil
<INSERT-FILE "gverbs" T>
```

**Loader additions:**
- Track loaded files to prevent cycles
- Resolve relative paths
- Merge into single world state

### SYNTAX Definitions

```zil
<SYNTAX TAKE OBJECT = V-TAKE>
```

**Parser integration:**
- Load SYNTAX forms
- Build verb→routine mapping
- Support preposition patterns

---

## Validation Milestones

### Milestone 1: After Batch 2
- Load Zork I files without parse errors
- Tables initialized correctly
- Basic operations execute

### Milestone 2: After Batch 4
- Run GO routine
- "West of House" prints correctly
- LOOK command works
- Basic navigation (N/S/E/W)

### Milestone 3: After Batch 6
- Full game playable
- Interrupts fire (lamp warning)
- Combat works
- Game can be won

---

## Test Strategy

### Unit Tests
- Each operation tested in isolation
- Edge cases and error conditions
- ~205 new tests total

### Integration Tests
- Zork I source patterns
- Multi-operation sequences
- Real game scenarios

### Validation Tests
- Golden output comparisons
- Known Zork I transcripts
- Regression suite

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Parser differences | Compare against ZILF behavior |
| Missing operations | Add stub that logs and continues |
| Performance | Profile after Batch 4, optimize if needed |
| Edge cases | Use Zork I source as test oracle |

---

## Future Projects (Post Zork I)

1. **Zork II/III Support** - Extend interpreter to full trilogy (shared codebase, incremental additions)

2. **ZIL Compiler** - Compile ZIL source to Z-machine bytecode (.z3/.z5/.z8 output)

3. **Z-Machine Interpreter** - Run compiled Infocom games universally (like Frotz)

---

## Summary

| Metric | Value |
|--------|-------|
| New operations | 42 |
| New tests | ~205 |
| Batches | 6 |
| Target | Playable Zork I |

**Approach:** Incremental TDD batches maintaining current quality standards (100% test pass rate, type-safe, documented).
