import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor, CircularDependencyError


def test_file_processor_accepts_max_depth_param():
    """FileProcessor should accept a max_depth parameter."""
    fp = FileProcessor(Path("/tmp"), max_depth=5)
    assert fp.max_depth == 5


def test_file_processor_default_max_depth():
    """Default max_depth should be 100."""
    fp = FileProcessor(Path("/tmp"))
    assert fp.max_depth == 100


def test_depth_check_raises_on_exceeded():
    """_check_depth should raise when current depth exceeds max."""
    fp = FileProcessor(Path("/tmp"), max_depth=3)
    fp._depth = 4
    with pytest.raises((CircularDependencyError, ValueError, RecursionError)):
        fp._check_depth()
