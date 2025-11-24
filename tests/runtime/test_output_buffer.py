import pytest
from zil_interpreter.runtime.output_buffer import OutputBuffer


def test_create_empty_buffer():
    """Test creating an empty output buffer."""
    buffer = OutputBuffer()
    assert buffer.get_output() == ""


def test_write_to_buffer():
    """Test writing text to buffer."""
    buffer = OutputBuffer()
    buffer.write("Hello")
    buffer.write(" ")
    buffer.write("world")

    assert buffer.get_output() == "Hello world"


def test_flush_buffer():
    """Test flushing buffer clears it."""
    buffer = OutputBuffer()
    buffer.write("Test")

    output = buffer.flush()
    assert output == "Test"
    assert buffer.get_output() == ""


def test_write_line():
    """Test writing a line with newline."""
    buffer = OutputBuffer()
    buffer.writeln("Line 1")
    buffer.writeln("Line 2")

    assert buffer.get_output() == "Line 1\nLine 2\n"


def test_tell_directive():
    """Test TELL directive formatting."""
    buffer = OutputBuffer()
    buffer.tell("You are in a room.")
    buffer.tell("There is a lamp here.")

    output = buffer.get_output()
    assert "You are in a room" in output
    assert "There is a lamp here" in output
