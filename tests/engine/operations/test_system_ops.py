"""Tests for system operations: SAVE, RESTORE, RESTART, VERIFY, PRINC, DIRIN, DIROUT."""
import pytest
from io import StringIO
from unittest.mock import Mock, patch, MagicMock


class TestSaveOperation:
    """Tests for SAVE operation."""

    def test_save_operation_registered(self):
        """SAVE operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("SAVE") is not None

    def test_save_returns_true_on_success(self):
        """SAVE returns True when save succeeds."""
        from zil_interpreter.engine.operations.system_ops import SaveOp
        op = SaveOp()

        mock_evaluator = Mock()
        mock_evaluator.world = Mock()
        mock_evaluator.world.serialize = Mock(return_value={"test": "data"})
        mock_evaluator.output = Mock()

        with patch("builtins.input", return_value="test_save.sav"):
            with patch("builtins.open", MagicMock()):
                with patch("json.dump"):
                    result = op.execute([], mock_evaluator)

        assert result is True

    def test_save_returns_false_on_failure(self):
        """SAVE returns False when save fails."""
        from zil_interpreter.engine.operations.system_ops import SaveOp
        op = SaveOp()

        mock_evaluator = Mock()
        mock_evaluator.world = Mock()
        mock_evaluator.world.serialize = Mock(side_effect=IOError("Save failed"))
        mock_evaluator.output = Mock()

        with patch("builtins.input", return_value="test_save.sav"):
            result = op.execute([], mock_evaluator)

        assert result is False


class TestRestoreOperation:
    """Tests for RESTORE operation."""

    def test_restore_operation_registered(self):
        """RESTORE operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("RESTORE") is not None

    def test_restore_returns_true_on_success(self):
        """RESTORE returns True when restore succeeds."""
        from zil_interpreter.engine.operations.system_ops import RestoreOp
        op = RestoreOp()

        mock_evaluator = Mock()
        mock_evaluator.world = Mock()
        mock_evaluator.world.deserialize = Mock()
        mock_evaluator.output = Mock()

        with patch("builtins.input", return_value="test_save.sav"):
            with patch("builtins.open", MagicMock()):
                with patch("json.load", return_value={"test": "data"}):
                    result = op.execute([], mock_evaluator)

        assert result is True

    def test_restore_returns_false_on_failure(self):
        """RESTORE returns False when file not found."""
        from zil_interpreter.engine.operations.system_ops import RestoreOp
        op = RestoreOp()

        mock_evaluator = Mock()
        mock_evaluator.output = Mock()

        with patch("builtins.input", return_value="nonexistent.sav"):
            with patch("builtins.open", side_effect=FileNotFoundError()):
                result = op.execute([], mock_evaluator)

        assert result is False


class TestRestartOperation:
    """Tests for RESTART operation."""

    def test_restart_operation_registered(self):
        """RESTART operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("RESTART") is not None

    def test_restart_resets_world_state(self):
        """RESTART resets world to initial state."""
        from zil_interpreter.engine.operations.system_ops import RestartOp
        op = RestartOp()

        mock_evaluator = Mock()
        mock_evaluator.world = Mock()
        mock_evaluator.world.reset = Mock()
        mock_evaluator.output = Mock()

        result = op.execute([], mock_evaluator)

        mock_evaluator.world.reset.assert_called_once()
        assert result is True


class TestVerifyOperation:
    """Tests for VERIFY operation."""

    def test_verify_operation_registered(self):
        """VERIFY operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("VERIFY") is not None

    def test_verify_returns_true(self):
        """VERIFY returns True (story file valid - always succeeds for interpreter)."""
        from zil_interpreter.engine.operations.system_ops import VerifyOp
        op = VerifyOp()

        mock_evaluator = Mock()
        mock_evaluator.output = Mock()

        result = op.execute([], mock_evaluator)

        assert result is True


class TestPrincOperation:
    """Tests for PRINC operation."""

    def test_princ_operation_registered(self):
        """PRINC operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("PRINC") is not None

    def test_princ_prints_string_without_quotes(self):
        """PRINC prints string without surrounding quotes."""
        from zil_interpreter.engine.operations.system_ops import PrincOp
        op = PrincOp()

        output = StringIO()
        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value="HELLO")
        mock_evaluator.output = Mock()
        mock_evaluator.output.write = output.write

        op.execute(["HELLO"], mock_evaluator)

        assert output.getvalue() == "HELLO"

    def test_princ_prints_number(self):
        """PRINC prints number value."""
        from zil_interpreter.engine.operations.system_ops import PrincOp
        op = PrincOp()

        output = StringIO()
        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value=42)
        mock_evaluator.output = Mock()
        mock_evaluator.output.write = output.write

        op.execute([42], mock_evaluator)

        assert output.getvalue() == "42"

    def test_princ_returns_printed_value(self):
        """PRINC returns the value it printed."""
        from zil_interpreter.engine.operations.system_ops import PrincOp
        op = PrincOp()

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value="TEST")
        mock_evaluator.output = Mock()

        result = op.execute(["TEST"], mock_evaluator)

        assert result == "TEST"


class TestDirinOperation:
    """Tests for DIRIN operation."""

    def test_dirin_operation_registered(self):
        """DIRIN operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("DIRIN") is not None

    def test_dirin_sets_input_stream(self):
        """DIRIN sets input stream direction."""
        from zil_interpreter.engine.operations.system_ops import DirinOp
        op = DirinOp()

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value=1)
        mock_evaluator.world = Mock()
        mock_evaluator.world.set_global = Mock()

        result = op.execute([1], mock_evaluator)

        mock_evaluator.world.set_global.assert_called_with("INPUT-STREAM", 1)
        assert result is True


class TestDiroutOperation:
    """Tests for DIROUT operation."""

    def test_dirout_operation_registered(self):
        """DIROUT operation is registered."""
        from zil_interpreter.engine.operations import create_default_registry
        registry = create_default_registry()
        assert registry.get("DIROUT") is not None

    def test_dirout_enables_stream(self):
        """DIROUT enables output stream when positive."""
        from zil_interpreter.engine.operations.system_ops import DiroutOp
        op = DiroutOp()

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value=4)
        mock_evaluator.world = Mock()
        mock_evaluator.world.set_global = Mock()

        result = op.execute([4], mock_evaluator)

        mock_evaluator.world.set_global.assert_called_with("OUTPUT-STREAM-4", True)
        assert result is True

    def test_dirout_disables_stream(self):
        """DIROUT disables output stream when negative."""
        from zil_interpreter.engine.operations.system_ops import DiroutOp
        op = DiroutOp()

        mock_evaluator = Mock()
        mock_evaluator.evaluate = Mock(return_value=-4)
        mock_evaluator.world = Mock()
        mock_evaluator.world.set_global = Mock()

        result = op.execute([-4], mock_evaluator)

        mock_evaluator.world.set_global.assert_called_with("OUTPUT-STREAM-4", False)
        assert result is True
