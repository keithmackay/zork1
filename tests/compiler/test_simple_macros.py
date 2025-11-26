"""Tests for simple macro expansions (Task 3.7)."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, GlobalRef, Number


class TestSimpleMacros:
    """Tests for simple single-form macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_enable_macro(self, expander):
        """ENABLE expands to PUT form."""
        # <ENABLE ,LAMP-INT>
        form = Form(Atom("ENABLE"), [GlobalRef("LAMP-INT")])
        result = expander.expand(form)
        # <PUT ,LAMP-INT ,C-ENABLED? 1>
        assert isinstance(result, Form)
        assert result.operator.value == "PUT"
        assert len(result.args) == 3
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "LAMP-INT"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "C-ENABLED?"
        assert isinstance(result.args[2], Number)
        assert result.args[2].value == 1

    def test_disable_macro(self, expander):
        """DISABLE expands to PUT form."""
        # <DISABLE ,LAMP-INT>
        form = Form(Atom("DISABLE"), [GlobalRef("LAMP-INT")])
        result = expander.expand(form)
        # <PUT ,LAMP-INT ,C-ENABLED? 0>
        assert isinstance(result, Form)
        assert result.operator.value == "PUT"
        assert len(result.args) == 3
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "LAMP-INT"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "C-ENABLED?"
        assert isinstance(result.args[2], Number)
        assert result.args[2].value == 0

    def test_rfatal_macro(self, expander):
        """RFATAL expands to PROG with PUSH/RSTACK."""
        # <RFATAL>
        form = Form(Atom("RFATAL"), [])
        result = expander.expand(form)
        # <PROG () <PUSH 2> <RSTACK>>
        assert isinstance(result, Form)
        assert result.operator.value == "PROG"
        assert len(result.args) == 3
        assert result.args[0] == []
        # Check <PUSH 2>
        push_form = result.args[1]
        assert isinstance(push_form, Form)
        assert push_form.operator.value == "PUSH"
        assert len(push_form.args) == 1
        assert isinstance(push_form.args[0], Number)
        assert push_form.args[0].value == 2
        # Check <RSTACK>
        rstack_form = result.args[2]
        assert isinstance(rstack_form, Form)
        assert rstack_form.operator.value == "RSTACK"
        assert len(rstack_form.args) == 0

    def test_enable_case_insensitive(self, expander):
        """ENABLE works regardless of case."""
        form = Form(Atom("enable"), [GlobalRef("INT")])
        result = expander.expand(form)
        assert result.operator.value == "PUT"

    def test_disable_case_insensitive(self, expander):
        """DISABLE works regardless of case."""
        form = Form(Atom("disable"), [GlobalRef("INT")])
        result = expander.expand(form)
        assert result.operator.value == "PUT"
        assert result.args[2].value == 0

    def test_rfatal_case_insensitive(self, expander):
        """RFATAL works regardless of case."""
        form = Form(Atom("rfatal"), [])
        result = expander.expand(form)
        assert result.operator.value == "PROG"
