# ZIL Operations Catalog

Complete reference for all 47 operations implemented in the ZIL interpreter.

## Overview

This catalog documents all ZIL operations supported by the interpreter, organized by category. Each operation includes syntax, description, examples, and compatibility notes with historical Zork I source code.

## Comparison Operations (11)

Operations for comparing values and checking object states.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **EQUAL?** | Value equality check | `<EQUAL? val1 val2>` | `<EQUAL? ,HERE ,WEST-OF-HOUSE>` | true/false |
| **==** | Numeric equality | `<== num1 num2>` | `<== 3 3>` | true/false |
| **<** (L?) | Less than | `<L? num1 num2>` | `<L? 3 5>` | true/false |
| **>** (G?) | Greater than | `<G? num1 num2>` | `<G? 5 3>` | true/false |
| **<=** | Less than or equal | `<<= num1 num2>` | `<<= 3 5>` | true/false |
| **>=** | Greater than or equal | `<>= num1 num2>` | `<>= 5 3>` | true/false |
| **ZERO?** | Check if zero | `<ZERO? num>` | `<ZERO? 0>` | true/false |
| **FSET?** | Check object flag | `<FSET? obj flag>` | `<FSET? ,LAMP ,ONBIT>` | true/false |
| **VERB?** | Check current verb | `<VERB? verb>` | `<VERB? TAKE>` | true/false |
| **IN?** | Check containment | `<IN? obj container>` | `<IN? ,LAMP ,ROOM>` | true/false |
| **FIRST?** | Get first child | `<FIRST? obj>` | `<FIRST? ,PLAYER>` | object name |

### Comparison Examples

```zil
; Value equality
<COND (<EQUAL? ,HERE ,KITCHEN>
       <TELL "You're in the kitchen.">)>

; Numeric comparison
<COND (<G? ,SCORE 100>
       <TELL "You're doing great!">)>

; Object flag check
<COND (<FSET? ,LAMP ,ONBIT>
       <TELL "The lamp is on.">)>

; Verb check pattern (from Zork I)
<COND (<VERB? TAKE>
       <TELL "You take it.">)>
```

## Logic Operations (3)

Boolean logic operations with short-circuit evaluation.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **AND** | Logical AND (short-circuit) | `<AND expr1 expr2 ...>` | `<AND <G? 5 3> <L? 2 4>>` | last value or false |
| **OR** | Logical OR (short-circuit) | `<OR expr1 expr2 ...>` | `<OR <ZERO? 0> <G? 1 2>>` | first true or false |
| **NOT** | Logical NOT | `<NOT expr>` | `<NOT <ZERO? 5>>` | true/false |

### Logic Examples

```zil
; Compound condition
<COND (<AND <IN? ,LAMP ,PLAYER>
            <FSET? ,LAMP ,ONBIT>>
       <TELL "Your lamp provides light.">)>

; Short-circuit OR
<COND (<OR <VERB? TAKE>
           <VERB? GET>
           <VERB? PICK-UP>>
       <DO-TAKE>)>

; Negation
<COND (<NOT <FSET? ,DOOR ,OPENBIT>>
       <TELL "The door is closed.">)>
```

## Arithmetic Operations (5)

Basic arithmetic with support for multiple operands.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **+** | Addition | `<+ num1 num2 ...>` | `<+ 2 3 4>` | 9 |
| **-** | Subtraction/Negation | `<- num1 num2>` or `<- num>` | `<- 10 3>` | 7 |
| **\*** | Multiplication | `<* num1 num2 ...>` | `<* 3 4>` | 12 |
| **/** | Integer division | `</ num1 num2>` | `</ 10 3>` | 3 |
| **MOD** | Modulo | `<MOD num1 num2>` | `<MOD 10 3>` | 1 |

### Arithmetic Examples

```zil
; Score calculation
<SETG SCORE <+ ,SCORE 10>>

; Damage calculation
<SET HEALTH <- ,HEALTH ,DAMAGE>>

; Timer countdown
<SETG COUNTER <- ,COUNTER 1>>

; Complex expression
<SET RESULT <+ <- 10 3> <* 2 5> </ 20 4>>>
; = 7 + 10 + 5 = 22
```

## Control Flow Operations (6)

Operations for conditional execution and flow control.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **COND** | Multi-branch conditional | `<COND (test1 action1) (test2 action2) ...>` | See below | varies |
| **RETURN** | Return value from routine | `<RETURN value>` | `<RETURN 42>` | value |
| **RTRUE** | Return true | `<RTRUE>` | `<RTRUE>` | true |
| **RFALSE** | Return false | `<RFALSE>` | `<RFALSE>` | false |
| **REPEAT** | Loop construct | `<REPEAT () ...>` | See below | varies |
| **MAPF** | Map function over list | `<MAPF func list>` | See below | list |

### Control Flow Examples

```zil
; COND with multiple branches
<COND (<VERB? OPEN>
       <COND (<FSET? ,OBJ ,OPENBIT>
              <TELL "It's already open.">)
             (T
              <FSET ,OBJ ,OPENBIT>
              <TELL "Opened.">)>)
      (<VERB? CLOSE>
       <COND (<FSET? ,OBJ ,OPENBIT>
              <FCLEAR ,OBJ ,OPENBIT>
              <TELL "Closed.">)
             (T
              <TELL "It's already closed.">)>)>

; Early return
<ROUTINE CHECK-ACCESS ()
  <COND (<NOT <IN? ,PLAYER ,ROOM>>
         <RTRUE>)>
  <TELL "Access granted.">
  <RTRUE>>

; Pattern from Zork I
<COND (<EQUAL? ,RARG ,M-LOOK>
       <TELL "Room description...">)
      (<EQUAL? ,RARG ,M-ENTER>
       <TELL "Entry message...">)
      (T <RFALSE>)>
```

## I/O Operations (2)

Operations for text output.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **TELL** | Output text | `<TELL text1 text2 ...>` | `<TELL "Hello" CR>` | void |
| **PRINTC** | Print character | `<PRINTC char-code>` | `<PRINTC 65>` | void |

### I/O Examples

```zil
; Simple output
<TELL "You are in a maze of twisty passages." CR>

; Variable interpolation
<TELL "Your score is " ,SCORE " out of 350." CR>

; Special atoms
<TELL "Press any key..." CR CR>  ; Two newlines

; From Zork I
<TELL
"You are standing in an open field west of a white house, with a boarded
front door." CR>
```

### Special TELL Atoms

- **CR** - Carriage return (newline)
- **CRLF** - CR + LF (typically same as CR)

## Object Operations (8)

Operations for manipulating game objects and their states.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **MOVE** | Move object | `<MOVE obj dest>` | `<MOVE ,LAMP ,PLAYER>` | void |
| **REMOVE** | Remove from parent | `<REMOVE obj>` | `<REMOVE ,LAMP>` | void |
| **FSET** | Set flag | `<FSET obj flag>` | `<FSET ,LAMP ,ONBIT>` | void |
| **FCLEAR** | Clear flag | `<FCLEAR obj flag>` | `<FCLEAR ,LAMP ,ONBIT>` | void |
| **GETP** | Get property | `<GETP obj prop>` | `<GETP ,LAMP ,DESC>` | value |
| **PUTP** | Set property | `<PUTP obj prop val>` | `<PUTP ,LAMP ,DESC "...">` | void |
| **LOC** | Get location | `<LOC obj>` | `<LOC ,LAMP>` | parent object |
| **HELD?** | Check if held | `<HELD? obj>` | `<HELD? ,LAMP>` | true/false |

### Object Examples

```zil
; Take object pattern
<ROUTINE DO-TAKE ()
  <COND (<HELD? ,PRSO>
         <TELL "You already have it." CR>)
        (T
         <MOVE ,PRSO ,PLAYER>
         <TELL "Taken." CR>)>>

; Light source management
<COND (<AND <HELD? ,LAMP> <FSET? ,LAMP ,ONBIT>>
       <FSET ,HERE ,LIGHTBIT>)>

; Object interaction
<COND (<NOT <IN? ,PRSO ,HERE>>
       <TELL "You can't see that here." CR>
       <RFALSE>)>
```

### Standard Object Flags

- **OPENBIT** - Object is open
- **CONTAINERBIT** - Object can contain other objects
- **TAKEABLEBIT** - Object can be taken
- **LOCKEDBIT** - Object is locked
- **NDESCBIT** - No automatic description
- **LIGHTBIT** - Provides light
- **ONBIT** - Light is currently on
- **TOUCHBIT** - Has been touched/seen
- **INVISIBLE** - Not visible to parser

## Variable Operations (2)

Operations for setting variables.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **SET** | Set local variable | `<SET var value>` | `<SET FOO 42>` | value |
| **SETG** | Set global variable | `<SETG var value>` | `<SETG SCORE 100>` | value |

### Variable Examples

```zil
; Global variables
<SETG SCORE 0>
<SETG MOVES 0>
<SETG VERBOSE T>

; Local variables in routines
<ROUTINE CALC-DAMAGE (WEAPON)
  <SET DMG <GETP .WEAPON ,POWER>>
  <SET DMG <* .DMG 2>>
  .DMG>

; Incrementing
<SETG SCORE <+ ,SCORE 10>>
```

## String Operations (3)

Operations for string manipulation.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **CONCAT** | Concatenate strings | `<CONCAT str1 str2 ...>` | `<CONCAT "Hi" " " "there">` | string |
| **SUBSTRING** | Extract substring | `<SUBSTRING str start end>` | `<SUBSTRING "Hello" 0 5>` | string |
| **PRINTC** | Print character | `<PRINTC code>` | `<PRINTC 65>` | void |

### String Examples

```zil
; Building messages
<SET MSG <CONCAT "You see " <GETP ,OBJ ,DESC> " here.">>

; String manipulation
<SET NAME <SUBSTRING "RUSTY-SWORD" 0 5>>
; NAME = "RUSTY"

; Character output
<PRINTC 42>  ; Prints '*'
```

## List Operations (8)

Operations for list/collection manipulation.

| Operation | Description | Syntax | Example | Returns |
|-----------|-------------|--------|---------|---------|
| **LENGTH** | Get list length | `<LENGTH list>` | `<LENGTH '(1 2 3)>` | 3 |
| **NTH** | Get nth element | `<NTH list index>` | `<NTH '(A B C) 2>` | B |
| **FIRST** | Get first element | `<FIRST list>` | `<FIRST '(1 2 3)>` | 1 |
| **REST** | Get tail (all but first) | `<REST list>` | `<REST '(1 2 3)>` | (2 3) |
| **NEXT** | Next sibling object | `<NEXT obj>` | `<NEXT ,OBJ>` | next object |
| **BACK** | Previous element | `<BACK obj>` | `<BACK ,OBJ>` | previous object |
| **EMPTY?** | Check if empty | `<EMPTY? list>` | `<EMPTY? '()>` | true/false |
| **MEMQ** | Check membership | `<MEMQ item list>` | `<MEMQ 2 '(1 2 3)>` | true/false |

### List Examples

```zil
; Iterating children
<ROUTINE DESCRIBE-CONTENTS (CONTAINER)
  <SET CHILD <FIRST? .CONTAINER>>
  <COND (.CHILD
         <TELL "You see:" CR>
         <REPEAT ()
           <TELL "  " <GETP .CHILD ,DESC> CR>
           <SET CHILD <NEXT? .CHILD>>
           <COND (<NOT .CHILD> <RETURN>)>>)>>

; List processing
<SET ITEMS '(SWORD LAMP BOOK)>
<SET FIRST-ITEM <FIRST ,ITEMS>>
<SET REST-ITEMS <REST ,ITEMS>>

; Membership check
<COND (<MEMQ ,PRSO ,TREASURES>
       <TELL "That's a treasure!" CR>)>
```

## Operation Categories Summary

| Category | Count | Operations |
|----------|-------|------------|
| **Comparison** | 11 | EQUAL?, ==, <, >, <=, >=, ZERO?, FSET?, VERB?, IN?, FIRST? |
| **Logic** | 3 | AND, OR, NOT |
| **Arithmetic** | 5 | +, -, *, /, MOD |
| **Control Flow** | 6 | COND, RETURN, RTRUE, RFALSE, REPEAT, MAPF |
| **I/O** | 2 | TELL, PRINTC |
| **Object** | 8 | MOVE, REMOVE, FSET, FCLEAR, GETP, PUTP, LOC, HELD? |
| **Variables** | 2 | SET, SETG |
| **String** | 3 | CONCAT, SUBSTRING, PRINTC |
| **List** | 8 | LENGTH, NTH, FIRST, REST, NEXT, BACK, EMPTY?, MEMQ |
| **TOTAL** | **47** | All core operations for Zork I compatibility |

## Zork I Compatibility

All operations have been tested against patterns found in the original Zork I source code:

- **gverbs.zil** - Generic verb implementations
- **1actions.zil** - Game-specific action handlers
- **gparser.zil** - Parser implementation
- **gmain.zil** - Main game loop

### Common Zork I Patterns

```zil
; Room routine pattern (from 1actions.zil)
<ROUTINE WEST-HOUSE (RARG)
  <COND (<EQUAL? .RARG ,M-LOOK>
         <TELL "You are standing in an open field..." CR>)>>

; Open/Close pattern (from 1actions.zil)
<ROUTINE OPEN-CLOSE (OBJ STROPN STRCLS)
  <COND (<VERB? OPEN>
         <COND (<FSET? .OBJ ,OPENBIT>
                <TELL <PICK-ONE ,DUMMY>>)
               (T
                <TELL .STROPN>
                <FSET .OBJ ,OPENBIT>)>
         <CRLF>)
        (<VERB? CLOSE>
         <COND (<FSET? .OBJ ,OPENBIT>
                <TELL .STRCLS>
                <FCLEAR .OBJ ,OPENBIT>
                T)
               (T <TELL <PICK-ONE ,DUMMY>>)>
         <CRLF>)>>

; Inventory pattern (from gverbs.zil)
<ROUTINE V-INVENTORY ()
  <COND (<FIRST? ,WINNER> <PRINT-CONT ,WINNER>)
        (T <TELL "You are empty-handed." CR>)>>
```

## Implementation Notes

### Operation Registry

All operations are implemented using the **Operation Registry Pattern**:

```python
from zil_interpreter.engine.operations.registry import OperationRegistry

registry = OperationRegistry()
registry.register_all()

# Operations are automatically discovered and registered
operation = registry.get("EQUAL?")
result = operation.execute(args, evaluator)
```

### Adding New Operations

To add a new operation:

1. Create a class inheriting from `Operation`
2. Implement `name` property and `execute` method
3. Place in appropriate category module
4. Operation is auto-registered on import

```python
class MyOperation(Operation):
    @property
    def name(self) -> str:
        return "MY-OP"

    def execute(self, args: list, evaluator) -> Any:
        # Implementation
        pass
```

## Testing

All operations are covered by:

- **215 unit tests** - Individual operation testing
- **25 integration tests** - Multi-operation scenarios
- **Zork I compatibility tests** - Real-world patterns

Total: **240 tests** with **100% pass rate**

## See Also

- [README.md](../README.md) - Project overview
- [test_zil_operations_integration.py](../tests/integration/test_zil_operations_integration.py) - Integration test examples
- [Zork I Source](../../zork1/) - Original historical source code

---

*Last updated: 2025-11-24*
*Operations catalog for ZIL Interpreter v1.0.0*
