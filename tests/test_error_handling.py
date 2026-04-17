import pytest
from unittest.mock import MagicMock
from zil_interpreter.engine.zil_errors import ZILRuntimeError
from zil_interpreter.engine.operations.missing_ops import (
    ZmemqOperation, ZmemqbOperation, ChtypeOperation, SpnameOperation, StuffOperation
)


def test_zil_runtime_error_has_context():
    err = ZILRuntimeError("Unknown operation: FROBNICATE")
    assert "FROBNICATE" in str(err)


def test_zil_runtime_error_is_exception():
    with pytest.raises(ZILRuntimeError):
        raise ZILRuntimeError("test")


def test_stub_zmemq_raises():
    ev = MagicMock()
    with pytest.raises(NotImplementedError):
        ZmemqOperation().execute([], ev)


def test_stub_zmemqb_raises():
    ev = MagicMock()
    with pytest.raises(NotImplementedError):
        ZmemqbOperation().execute([], ev)


def test_stub_chtype_raises():
    ev = MagicMock()
    with pytest.raises(NotImplementedError):
        ChtypeOperation().execute([], ev)


def test_stub_spname_raises():
    ev = MagicMock()
    with pytest.raises(NotImplementedError):
        SpnameOperation().execute([], ev)


def test_stub_stuff_raises():
    ev = MagicMock()
    with pytest.raises(NotImplementedError):
        StuffOperation().execute([], ev)
