import pytest
from zil_interpreter.engine.zil_errors import ZILRuntimeError


def test_zil_runtime_error_has_context():
    err = ZILRuntimeError("Unknown operation: FROBNICATE")
    assert "FROBNICATE" in str(err)


def test_zil_runtime_error_is_exception():
    with pytest.raises(ZILRuntimeError):
        raise ZILRuntimeError("test")
