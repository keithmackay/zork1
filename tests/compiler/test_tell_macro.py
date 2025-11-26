"""Tests for TELL macro expansion - Task 3.3 (Basic strings)."""
import pytest
from zil_interpreter.compiler.tell_macro import expand_tell
from zil_interpreter.parser.ast_nodes import Form, Atom, String


class TestTellMacroBasic:
    """Tests for basic TELL expansion (Task 3.3)."""

    def test_single_string(self):
        """TELL with single string expands to PRINTI."""
        # <TELL "Hello">
        args = [String("Hello")]
        result = expand_tell(args)
        # Should expand to <PROG () <PRINTI "Hello">>
        assert isinstance(result, Form)
        assert result.operator.value == "PROG"
        assert len(result.args) == 2  # () and one PRINTI
        assert result.args[0] == []  # Empty param list
        body = result.args[1]
        assert isinstance(body, Form)
        assert body.operator.value == "PRINTI"
        assert len(body.args) == 1
        assert isinstance(body.args[0], String)
        assert body.args[0].value == "Hello"

    def test_multiple_strings(self):
        """TELL with multiple strings creates multiple PRINTI."""
        # <TELL "Hello " "World">
        args = [String("Hello "), String("World")]
        result = expand_tell(args)
        # <PROG () <PRINTI "Hello "> <PRINTI "World">>
        assert result.operator.value == "PROG"
        assert len(result.args) == 3  # () + 2 PRINTI forms
        assert result.args[0] == []

        # Check first PRINTI
        first_print = result.args[1]
        assert first_print.operator.value == "PRINTI"
        assert first_print.args[0].value == "Hello "

        # Check second PRINTI
        second_print = result.args[2]
        assert second_print.operator.value == "PRINTI"
        assert second_print.args[0].value == "World"

    def test_crlf_indicator(self):
        """CR/CRLF expands to CRLF form."""
        # <TELL "Hi" CR>
        args = [String("Hi"), Atom("CR")]
        result = expand_tell(args)
        # <PROG () <PRINTI "Hi"> <CRLF>>
        assert result.operator.value == "PROG"
        assert len(result.args) == 3  # () + PRINTI + CRLF

        printi = result.args[1]
        assert printi.operator.value == "PRINTI"

        crlf = result.args[2]
        assert crlf.operator.value == "CRLF"
        assert len(crlf.args) == 0  # CRLF takes no arguments

    def test_crlf_standalone(self):
        """CRLF (not just CR) also expands correctly."""
        # <TELL CRLF>
        args = [Atom("CRLF")]
        result = expand_tell(args)
        # <PROG () <CRLF>>
        assert result.operator.value == "PROG"
        assert len(result.args) == 2
        assert result.args[1].operator.value == "CRLF"

    def test_empty_tell(self):
        """Empty TELL expands to empty PROG."""
        args = []
        result = expand_tell(args)
        assert result.operator.value == "PROG"
        assert len(result.args) == 1  # Just the ()
        assert result.args[0] == []

    def test_three_strings_with_cr(self):
        """Multiple strings followed by CR."""
        # <TELL "One" "Two" "Three" CR>
        args = [String("One"), String("Two"), String("Three"), Atom("CR")]
        result = expand_tell(args)
        # <PROG () <PRINTI "One"> <PRINTI "Two"> <PRINTI "Three"> <CRLF>>
        assert result.operator.value == "PROG"
        assert len(result.args) == 5  # () + 3 PRINTI + CRLF
        assert result.args[1].args[0].value == "One"
        assert result.args[2].args[0].value == "Two"
        assert result.args[3].args[0].value == "Three"
        assert result.args[4].operator.value == "CRLF"
