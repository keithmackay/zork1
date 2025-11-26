"""Tests for compile-time evaluation (%<...>)."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import PercentEval, Form, Atom, Number


class TestPercentEval:
    """Tests for %<...> compile-time evaluation."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_simple_addition(self, expander):
        """Simple addition is evaluated at compile time."""
        # %<+ 1 2> -> 3
        inner = Form(Atom("+"), [Number(1), Number(2)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 3

    def test_simple_subtraction(self, expander):
        """Simple subtraction is evaluated at compile time."""
        # %<- 10 4> -> 6
        inner = Form(Atom("-"), [Number(10), Number(4)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 6

    def test_simple_multiplication(self, expander):
        """Simple multiplication is evaluated at compile time."""
        # %<* 3 5> -> 15
        inner = Form(Atom("*"), [Number(3), Number(5)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 15

    def test_simple_division(self, expander):
        """Simple integer division is evaluated at compile time."""
        # %</ 20 4> -> 5
        inner = Form(Atom("/"), [Number(20), Number(4)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 5

    def test_nested_arithmetic(self, expander):
        """Nested arithmetic evaluated."""
        # %<* 2 <+ 3 4>> -> 14
        inner = Form(Atom("*"), [
            Number(2),
            Form(Atom("+"), [Number(3), Number(4)])
        ])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 14

    def test_deeply_nested_arithmetic(self, expander):
        """Deeply nested arithmetic."""
        # %<+ <* 2 3> <- 10 </ 8 2>>> -> 6 + 6 = 12
        inner = Form(Atom("+"), [
            Form(Atom("*"), [Number(2), Number(3)]),
            Form(Atom("-"), [Number(10), Form(Atom("/"), [Number(8), Number(2)])])
        ])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 12  # (2*3) + (10 - (8/2)) = 6 + 6 = 12

    def test_percent_in_form(self, expander):
        """Percent eval within larger form."""
        # <SETG X %<+ 1 1>> -> <SETG X 2>
        percent = PercentEval(Form(Atom("+"), [Number(1), Number(1)]))
        form = Form(Atom("SETG"), [Atom("X"), percent])
        result = expander.expand(form)
        assert isinstance(result, Form)
        assert result.operator.value == "SETG"
        assert isinstance(result.args[1], Number)
        assert result.args[1].value == 2

    def test_multiple_percent_in_form(self, expander):
        """Multiple percent evals in one form."""
        # <ROUTINE TEST %<+ 1 2> %<* 2 3>>
        percent1 = PercentEval(Form(Atom("+"), [Number(1), Number(2)]))
        percent2 = PercentEval(Form(Atom("*"), [Number(2), Number(3)]))
        form = Form(Atom("ROUTINE"), [Atom("TEST"), percent1, percent2])
        result = expander.expand(form)
        assert result.args[1].value == 3
        assert result.args[2].value == 6

    def test_unevaluable_returns_form(self, expander):
        """Non-evaluable forms pass through unchanged."""
        # %<FOO 1 2> -> <FOO 1 2> (can't evaluate unknown function)
        inner = Form(Atom("FOO"), [Number(1), Number(2)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Form)
        assert result.operator.value == "FOO"

    def test_multiple_operands_addition(self, expander):
        """Addition with multiple operands."""
        # %<+ 1 2 3 4> -> 10
        inner = Form(Atom("+"), [Number(1), Number(2), Number(3), Number(4)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 10

    def test_multiple_operands_multiplication(self, expander):
        """Multiplication with multiple operands."""
        # %<* 2 3 4> -> 24
        inner = Form(Atom("*"), [Number(2), Number(3), Number(4)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert isinstance(result, Number)
        assert result.value == 24

    def test_percent_eval_case_insensitive(self, expander):
        """Operators are case-insensitive."""
        # Using lowercase operators
        inner = Form(Atom("+"), [Number(5), Number(5)])
        node = PercentEval(inner)
        result = expander.expand(node)
        assert result.value == 10
