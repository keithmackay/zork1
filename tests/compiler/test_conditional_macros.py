"""Tests for conditional/utility macros (Task 3.10)."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, GlobalRef, Number, LocalRef


class TestConditionalMacros:
    """Tests for FLAMING?, OPENABLE?, ABS, PROB macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_flaming(self, expander):
        """FLAMING? checks FLAMEBIT and ONBIT."""
        # <FLAMING? ,LAMP>
        form = Form(Atom("FLAMING?"), [GlobalRef("LAMP")])
        result = expander.expand(form)
        # <AND <FSET? ,LAMP ,FLAMEBIT> <FSET? ,LAMP ,ONBIT>>
        assert isinstance(result, Form)
        assert result.operator.value == "AND"
        assert len(result.args) == 2
        # First check: FLAMEBIT
        check1 = result.args[0]
        assert isinstance(check1, Form)
        assert check1.operator.value == "FSET?"
        assert check1.args[0].name == "LAMP"
        assert check1.args[1].name == "FLAMEBIT"
        # Second check: ONBIT
        check2 = result.args[1]
        assert isinstance(check2, Form)
        assert check2.operator.value == "FSET?"
        assert check2.args[0].name == "LAMP"
        assert check2.args[1].name == "ONBIT"

    def test_openable(self, expander):
        """OPENABLE? checks DOORBIT or CONTBIT."""
        # <OPENABLE? ,BOX>
        form = Form(Atom("OPENABLE?"), [GlobalRef("BOX")])
        result = expander.expand(form)
        # <OR <FSET? ,BOX ,DOORBIT> <FSET? ,BOX ,CONTBIT>>
        assert isinstance(result, Form)
        assert result.operator.value == "OR"
        assert len(result.args) == 2
        # First check: DOORBIT
        check1 = result.args[0]
        assert isinstance(check1, Form)
        assert check1.operator.value == "FSET?"
        assert check1.args[0].name == "BOX"
        assert check1.args[1].name == "DOORBIT"
        # Second check: CONTBIT
        check2 = result.args[1]
        assert isinstance(check2, Form)
        assert check2.operator.value == "FSET?"
        assert check2.args[0].name == "BOX"
        assert check2.args[1].name == "CONTBIT"

    def test_abs_with_globalref(self, expander):
        """ABS creates conditional for absolute value."""
        # <ABS ,NUM>
        form = Form(Atom("ABS"), [GlobalRef("NUM")])
        result = expander.expand(form)
        # <COND (<L? ,NUM 0> <- 0 ,NUM>) (T ,NUM)>
        assert isinstance(result, Form)
        assert result.operator.value == "COND"
        assert len(result.args) == 2
        # First clause: (<L? ,NUM 0> <- 0 ,NUM>)
        clause1 = result.args[0]
        assert isinstance(clause1, list)
        assert len(clause1) == 2
        # Condition: <L? ,NUM 0>
        cond = clause1[0]
        assert isinstance(cond, Form)
        assert cond.operator.value == "L?"
        assert cond.args[0].name == "NUM"
        assert cond.args[1].value == 0
        # Action: <- 0 ,NUM>
        action = clause1[1]
        assert isinstance(action, Form)
        assert action.operator.value == "-"
        assert action.args[0].value == 0
        assert action.args[1].name == "NUM"
        # Second clause: (T ,NUM)
        clause2 = result.args[1]
        assert isinstance(clause2, list)
        assert len(clause2) == 2
        assert clause2[0].value == "T"
        assert clause2[1].name == "NUM"

    def test_abs_with_number(self, expander):
        """ABS works with number literals."""
        # <ABS -5>
        form = Form(Atom("ABS"), [Number(-5)])
        result = expander.expand(form)
        assert result.operator.value == "COND"

    def test_abs_with_localref(self, expander):
        """ABS works with local variables."""
        # <ABS .X>
        form = Form(Atom("ABS"), [LocalRef("X")])
        result = expander.expand(form)
        assert result.operator.value == "COND"
        clause1 = result.args[0]
        assert clause1[0].args[0].name == "X"

    def test_prob_with_number(self, expander):
        """PROB creates probability check."""
        # <PROB 50>
        form = Form(Atom("PROB"), [Number(50)])
        result = expander.expand(form)
        # <G? 50 <RANDOM 100>>
        assert isinstance(result, Form)
        assert result.operator.value == "G?"
        assert len(result.args) == 2
        # First arg: threshold
        assert isinstance(result.args[0], Number)
        assert result.args[0].value == 50
        # Second arg: <RANDOM 100>
        random_form = result.args[1]
        assert isinstance(random_form, Form)
        assert random_form.operator.value == "RANDOM"
        assert len(random_form.args) == 1
        assert isinstance(random_form.args[0], Number)
        assert random_form.args[0].value == 100

    def test_prob_with_variable(self, expander):
        """PROB works with variables."""
        # <PROB ,CHANCE>
        form = Form(Atom("PROB"), [GlobalRef("CHANCE")])
        result = expander.expand(form)
        assert result.operator.value == "G?"
        assert result.args[0].name == "CHANCE"

    def test_flaming_case_insensitive(self, expander):
        """FLAMING? works regardless of case."""
        form = Form(Atom("flaming?"), [GlobalRef("LAMP")])
        result = expander.expand(form)
        assert result.operator.value == "AND"

    def test_openable_case_insensitive(self, expander):
        """OPENABLE? works regardless of case."""
        form = Form(Atom("openable?"), [GlobalRef("BOX")])
        result = expander.expand(form)
        assert result.operator.value == "OR"

    def test_abs_case_insensitive(self, expander):
        """ABS works regardless of case."""
        form = Form(Atom("abs"), [GlobalRef("NUM")])
        result = expander.expand(form)
        assert result.operator.value == "COND"

    def test_prob_case_insensitive(self, expander):
        """PROB works regardless of case."""
        form = Form(Atom("prob"), [Number(50)])
        result = expander.expand(form)
        assert result.operator.value == "G?"
