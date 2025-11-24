import pytest
from zil_interpreter.parser.ast_nodes import (
    Form, Atom, String, Number, Routine, Object, Global
)


def test_form_creation():
    """Test basic Form node creation."""
    form = Form(operator=Atom("ROUTINE"), args=[Atom("FOO"), []])
    assert form.operator.value == "ROUTINE"
    assert len(form.args) == 2


def test_atom_creation():
    """Test Atom node preserves value."""
    atom = Atom("FOO-BAR")
    assert atom.value == "FOO-BAR"


def test_string_creation():
    """Test String node creation."""
    string = String("Hello world")
    assert string.value == "Hello world"


def test_number_creation():
    """Test Number node creation."""
    num = Number(42)
    assert num.value == 42


def test_routine_node():
    """Test Routine AST node."""
    routine = Routine(
        name="FOO",
        args=["X", "Y"],
        body=[Form(operator=Atom("TELL"), args=[String("test")])]
    )
    assert routine.name == "FOO"
    assert len(routine.args) == 2
    assert len(routine.body) == 1


def test_object_node():
    """Test Object AST node."""
    obj = Object(
        name="LAMP",
        properties={
            "DESC": String("brass lamp"),
            "SYNONYM": [Atom("LAMP"), Atom("LANTERN")]
        }
    )
    assert obj.name == "LAMP"
    assert obj.properties["DESC"].value == "brass lamp"


def test_global_node():
    """Test Global variable node."""
    global_var = Global(name="SCORE", value=Number(0))
    assert global_var.name == "SCORE"
    assert global_var.value.value == 0
