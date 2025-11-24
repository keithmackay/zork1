# Extended Evaluator Operations - Tasks 11-15

**Date:** 2025-11-24
**Goal:** Extend the ZIL expression evaluator with operations needed for game logic execution.

## Overview

Building on the basic evaluator from Task 8, we need to add:
- **Output operations**: TELL for displaying text
- **Object manipulation**: MOVE for changing object locations
- **Flag operations**: FSET and FCLEAR for modifying object flags
- **Property access**: GETP and PUTP for reading/writing object properties
- **Object predicates**: IN? and FIRST? for querying object relationships

---

## Task 11: TELL Operation (Output Text)

### Step 1: Write failing test

Create in `tests/engine/test_evaluator.py`:

```python
def test_evaluate_tell():
    """Test TELL form outputs text to buffer."""
    world = WorldState()
    output = OutputBuffer()
    evaluator = Evaluator(world, output)

    form = Form(operator=Atom("TELL"), args=[String("Hello, world!")])
    evaluator.evaluate(form)

    assert "Hello, world!" in output.get_output()


def test_evaluate_tell_with_crlf():
    """Test TELL with CR (carriage return)."""
    world = WorldState()
    output = OutputBuffer()
    evaluator = Evaluator(world, output)

    form = Form(operator=Atom("TELL"), args=[String("Line 1"), Atom("CR"), String("Line 2")])
    evaluator.evaluate(form)

    result = output.get_output()
    assert "Line 1" in result
    assert "Line 2" in result
```

### Step 2: Update Evaluator constructor

Modify `zil_interpreter/engine/evaluator.py`:

```python
from zil_interpreter.runtime.output_buffer import OutputBuffer

class Evaluator:
    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
```

### Step 3: Implement TELL operation

Add to `_evaluate_form()`:

```python
if op == "TELL":
    return self._eval_tell(form.args)
```

Add method:

```python
def _eval_tell(self, args: list) -> None:
    """Evaluate TELL form - output text."""
    for arg in args:
        if isinstance(arg, Atom):
            if arg.value.upper() in ("CR", "CRLF"):
                self.output.write("\n")
            else:
                # Variable lookup
                value = self.evaluate(arg)
                if value is not None:
                    self.output.write(str(value))
        else:
            value = self.evaluate(arg)
            if value is not None:
                self.output.write(str(value))
```

### Step 4: Run tests and commit

```bash
pytest tests/engine/test_evaluator.py::test_evaluate_tell -v
git add tests/engine/test_evaluator.py zil_interpreter/engine/evaluator.py
git commit -m "feat(engine): add TELL operation for text output

- Add OutputBuffer parameter to Evaluator constructor
- Implement TELL form evaluation
- Handle CR/CRLF atoms for newlines
- Support string and variable output

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 12: MOVE Operation (Object Movement)

### Step 1: Write failing test

```python
def test_evaluate_move():
    """Test MOVE form changes object location."""
    world = WorldState()

    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)
    player = GameObject(name="PLAYER")

    world.add_object(room)
    world.add_object(lamp)
    world.add_object(player)

    evaluator = Evaluator(world)

    # Move lamp to player
    form = Form(operator=Atom("MOVE"), args=[Atom("LAMP"), Atom("PLAYER")])
    evaluator.evaluate(form)

    assert lamp.parent == player
    assert lamp in player.children
```

### Step 2: Implement MOVE operation

Add to `_evaluate_form()`:

```python
if op == "MOVE":
    return self._eval_move(form.args)
```

Add method:

```python
def _eval_move(self, args: list) -> None:
    """Evaluate MOVE form - move object to new location."""
    if len(args) < 2:
        return

    obj_ref = self.evaluate(args[0])
    dest_ref = self.evaluate(args[1])

    # Get object by name
    obj = self.world.get_object(obj_ref) if isinstance(obj_ref, str) else obj_ref
    dest = self.world.get_object(dest_ref) if isinstance(dest_ref, str) else dest_ref

    if obj and dest:
        obj.move_to(dest)
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add MOVE operation for object movement

- Implement MOVE form to change object parent
- Support both atom and direct object references
- Update parent/child relationships

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 13: FSET and FCLEAR Operations

### Step 1: Write failing tests

```python
def test_evaluate_fset():
    """Test FSET form sets object flags."""
    world = WorldState()
    door = GameObject(name="DOOR")
    world.add_object(door)

    evaluator = Evaluator(world)

    assert not door.has_flag(ObjectFlag.OPEN)

    form = Form(operator=Atom("FSET"), args=[Atom("DOOR"), Atom("OPENBIT")])
    evaluator.evaluate(form)

    assert door.has_flag(ObjectFlag.OPEN)


def test_evaluate_fclear():
    """Test FCLEAR form clears object flags."""
    world = WorldState()
    door = GameObject(name="DOOR")
    door.set_flag(ObjectFlag.OPEN)
    world.add_object(door)

    evaluator = Evaluator(world)

    assert door.has_flag(ObjectFlag.OPEN)

    form = Form(operator=Atom("FCLEAR"), args=[Atom("DOOR"), Atom("OPENBIT")])
    evaluator.evaluate(form)

    assert not door.has_flag(ObjectFlag.OPEN)
```

### Step 2: Implement FSET and FCLEAR

Add to `_evaluate_form()`:

```python
if op == "FSET":
    return self._eval_fset(form.args)

if op == "FCLEAR":
    return self._eval_fclear(form.args)
```

Add methods:

```python
def _eval_fset(self, args: list) -> None:
    """Evaluate FSET form - set object flag."""
    if len(args) < 2:
        return

    obj_name = self.evaluate(args[0])
    flag_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

    obj = self.world.get_object(obj_name)
    if not obj:
        return

    flag = self.FLAG_MAP.get(flag_name.upper())
    if flag:
        obj.set_flag(flag)


def _eval_fclear(self, args: list) -> None:
    """Evaluate FCLEAR form - clear object flag."""
    if len(args) < 2:
        return

    obj_name = self.evaluate(args[0])
    flag_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

    obj = self.world.get_object(obj_name)
    if not obj:
        return

    flag = self.FLAG_MAP.get(flag_name.upper())
    if flag:
        obj.clear_flag(flag)
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add FSET and FCLEAR flag operations

- Implement FSET to set object flags
- Implement FCLEAR to clear object flags
- Use FLAG_MAP for flag name resolution

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 14: Property Access (GETP, PUTP)

### Step 1: Write failing tests

```python
def test_evaluate_getp():
    """Test GETP form reads object properties."""
    world = WorldState()
    chest = GameObject(name="CHEST")
    chest.set_property("SIZE", 20)
    chest.set_property("CAPACITY", 100)
    world.add_object(chest)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("GETP"), args=[Atom("CHEST"), Atom("SIZE")])
    result = evaluator.evaluate(form)

    assert result == 20


def test_evaluate_putp():
    """Test PUTP form sets object properties."""
    world = WorldState()
    chest = GameObject(name="CHEST")
    world.add_object(chest)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("PUTP"), args=[Atom("CHEST"), Atom("SIZE"), Number(30)])
    evaluator.evaluate(form)

    assert chest.get_property("SIZE") == 30
```

### Step 2: Implement GETP and PUTP

Add to `_evaluate_form()`:

```python
if op == "GETP":
    return self._eval_getp(form.args)

if op == "PUTP":
    return self._eval_putp(form.args)
```

Add methods:

```python
def _eval_getp(self, args: list) -> Any:
    """Evaluate GETP form - get object property."""
    if len(args) < 2:
        return None

    obj_name = self.evaluate(args[0])
    prop_name = args[1].value if isinstance(args[1], Atom) else str(args[1])

    obj = self.world.get_object(obj_name)
    if not obj:
        return None

    return obj.get_property(prop_name.upper())


def _eval_putp(self, args: list) -> None:
    """Evaluate PUTP form - set object property."""
    if len(args) < 3:
        return

    obj_name = self.evaluate(args[0])
    prop_name = args[1].value if isinstance(args[1], Atom) else str(args[1])
    value = self.evaluate(args[2])

    obj = self.world.get_object(obj_name)
    if obj:
        obj.set_property(prop_name.upper(), value)
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add GETP and PUTP property access

- Implement GETP to read object properties
- Implement PUTP to write object properties
- Return None for missing objects/properties

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 15: Object Predicates (IN?, FIRST?)

### Step 1: Write failing tests

```python
def test_evaluate_in_predicate():
    """Test IN? form checks object containment."""
    world = WorldState()

    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)
    player = GameObject(name="PLAYER")

    world.add_object(room)
    world.add_object(lamp)
    world.add_object(player)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("IN?"), args=[Atom("LAMP"), Atom("ROOM")])
    assert evaluator.evaluate(form) is True

    form2 = Form(operator=Atom("IN?"), args=[Atom("LAMP"), Atom("PLAYER")])
    assert evaluator.evaluate(form2) is False


def test_evaluate_first_predicate():
    """Test FIRST? form returns first child object."""
    world = WorldState()

    room = GameObject(name="ROOM")
    lamp = GameObject(name="LAMP", parent=room)
    sword = GameObject(name="SWORD", parent=room)

    world.add_object(room)
    world.add_object(lamp)
    world.add_object(sword)

    evaluator = Evaluator(world)

    form = Form(operator=Atom("FIRST?"), args=[Atom("ROOM")])
    result = evaluator.evaluate(form)

    # Should return one of the children
    assert result in ["LAMP", "SWORD"]
```

### Step 2: Implement IN? and FIRST?

Add to `_evaluate_form()`:

```python
if op == "IN?":
    return self._eval_in(form.args)

if op == "FIRST?":
    return self._eval_first(form.args)
```

Add methods:

```python
def _eval_in(self, args: list) -> bool:
    """Evaluate IN? form - check if object is in container."""
    if len(args) < 2:
        return False

    obj_name = self.evaluate(args[0])
    container_name = self.evaluate(args[1])

    obj = self.world.get_object(obj_name)
    container = self.world.get_object(container_name)

    if not obj or not container:
        return False

    return obj.parent == container


def _eval_first(self, args: list) -> Optional[str]:
    """Evaluate FIRST? form - get first child of container."""
    if not args:
        return None

    container_name = self.evaluate(args[0])
    container = self.world.get_object(container_name)

    if not container or not container.children:
        return None

    # Return first child's name
    return next(iter(container.children)).name
```

### Step 3: Commit

```bash
git commit -m "feat(engine): add IN? and FIRST? object predicates

- Implement IN? to check object containment
- Implement FIRST? to get first child object
- Return appropriate types (bool, string, None)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Completion

After completing Tasks 11-15, the evaluator will support:
- ✅ Text output (TELL)
- ✅ Object movement (MOVE)
- ✅ Flag manipulation (FSET, FCLEAR)
- ✅ Property access (GETP, PUTP)
- ✅ Object queries (IN?, FIRST?)

This provides the foundation for executing ZIL routines that manipulate game state.
