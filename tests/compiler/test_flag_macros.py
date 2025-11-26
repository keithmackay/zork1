"""Tests for flag manipulation macros (Task 3.9)."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, GlobalRef


class TestFlagMacros:
    """Tests for BSET, BCLEAR, BSET? macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_bset_single(self, expander):
        """BSET with single flag."""
        # <BSET ,LAMP ONBIT>
        form = Form(Atom("BSET"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        # <FSET ,LAMP ,ONBIT>
        assert isinstance(result, Form)
        assert result.operator.value == "FSET"
        assert len(result.args) == 2
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "LAMP"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "ONBIT"

    def test_bset_multiple(self, expander):
        """BSET with multiple flags creates PROG."""
        # <BSET ,LAMP ONBIT LIGHTBIT>
        form = Form(Atom("BSET"), [
            GlobalRef("LAMP"), Atom("ONBIT"), Atom("LIGHTBIT")
        ])
        result = expander.expand(form)
        # <PROG () <FSET ,LAMP ,ONBIT> <FSET ,LAMP ,LIGHTBIT>>
        assert isinstance(result, Form)
        assert result.operator.value == "PROG"
        assert len(result.args) == 3  # () + 2 FSET forms
        assert result.args[0] == []
        # First FSET
        fset1 = result.args[1]
        assert isinstance(fset1, Form)
        assert fset1.operator.value == "FSET"
        assert fset1.args[0].name == "LAMP"
        assert fset1.args[1].name == "ONBIT"
        # Second FSET
        fset2 = result.args[2]
        assert isinstance(fset2, Form)
        assert fset2.operator.value == "FSET"
        assert fset2.args[0].name == "LAMP"
        assert fset2.args[1].name == "LIGHTBIT"

    def test_bclear_single(self, expander):
        """BCLEAR clears flags."""
        # <BCLEAR ,LAMP ONBIT>
        form = Form(Atom("BCLEAR"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        # <FCLEAR ,LAMP ,ONBIT>
        assert isinstance(result, Form)
        assert result.operator.value == "FCLEAR"
        assert len(result.args) == 2
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "LAMP"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "ONBIT"

    def test_bclear_multiple(self, expander):
        """BCLEAR with multiple flags creates PROG."""
        # <BCLEAR ,LAMP ONBIT LIGHTBIT>
        form = Form(Atom("BCLEAR"), [
            GlobalRef("LAMP"), Atom("ONBIT"), Atom("LIGHTBIT")
        ])
        result = expander.expand(form)
        # <PROG () <FCLEAR...> <FCLEAR...>>
        assert isinstance(result, Form)
        assert result.operator.value == "PROG"
        assert len(result.args) == 3
        assert result.args[0] == []

    def test_bset_question_single(self, expander):
        """BSET? with single flag."""
        # <BSET? ,LAMP ONBIT>
        form = Form(Atom("BSET?"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        # <FSET? ,LAMP ,ONBIT>
        assert isinstance(result, Form)
        assert result.operator.value == "FSET?"
        assert len(result.args) == 2
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "LAMP"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "ONBIT"

    def test_bset_question_multiple(self, expander):
        """BSET? checks flags with OR."""
        # <BSET? ,LAMP ONBIT LIGHTBIT>
        form = Form(Atom("BSET?"), [
            GlobalRef("LAMP"), Atom("ONBIT"), Atom("LIGHTBIT")
        ])
        result = expander.expand(form)
        # <OR <FSET? ,LAMP ,ONBIT> <FSET? ,LAMP ,LIGHTBIT>>
        assert isinstance(result, Form)
        assert result.operator.value == "OR"
        assert len(result.args) == 2
        # First FSET?
        fset1 = result.args[0]
        assert isinstance(fset1, Form)
        assert fset1.operator.value == "FSET?"
        assert fset1.args[0].name == "LAMP"
        assert fset1.args[1].name == "ONBIT"
        # Second FSET?
        fset2 = result.args[1]
        assert isinstance(fset2, Form)
        assert fset2.operator.value == "FSET?"
        assert fset2.args[0].name == "LAMP"
        assert fset2.args[1].name == "LIGHTBIT"

    def test_bset_three_flags(self, expander):
        """BSET with three flags."""
        # <BSET ,OBJ F1 F2 F3>
        form = Form(Atom("BSET"), [
            GlobalRef("OBJ"), Atom("F1"), Atom("F2"), Atom("F3")
        ])
        result = expander.expand(form)
        assert result.operator.value == "PROG"
        assert len(result.args) == 4  # () + 3 FSET forms

    def test_bset_case_insensitive(self, expander):
        """BSET works regardless of case."""
        form = Form(Atom("bset"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        assert result.operator.value == "FSET"

    def test_bclear_case_insensitive(self, expander):
        """BCLEAR works regardless of case."""
        form = Form(Atom("bclear"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        assert result.operator.value == "FCLEAR"

    def test_bset_question_case_insensitive(self, expander):
        """BSET? works regardless of case."""
        form = Form(Atom("bset?"), [GlobalRef("LAMP"), Atom("ONBIT")])
        result = expander.expand(form)
        assert result.operator.value == "FSET?"
