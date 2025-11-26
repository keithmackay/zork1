"""Tests for macro expansion engine."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, String, GlobalRef, Routine


class TestMacroExpander:
    """Tests for AST-to-AST macro expansion."""

    @pytest.fixture
    def expander(self):
        """Create a macro expander with a registry."""
        registry = MacroRegistry()
        return MacroExpander(registry)

    def test_expand_tell(self, expander):
        """TELL macro is expanded."""
        # <TELL "Hello" CR>
        form = Form(Atom("TELL"), [String("Hello"), Atom("CR")])
        result = expander.expand(form)
        assert result.operator.value == "PROG"
        # Check that PROG has empty param list and body
        assert result.args[0] == []  # Empty parameter list
        assert len(result.args) > 1  # Has body forms

    def test_non_macro_unchanged(self, expander):
        """Non-macro forms pass through unchanged."""
        form = Form(Atom("PRINT"), [String("Hello")])
        result = expander.expand(form)
        assert result.operator.value == "PRINT"
        assert isinstance(result.args[0], String)
        assert result.args[0].value == "Hello"

    def test_nested_expansion(self, expander):
        """Macros in nested forms are expanded."""
        # <COND (T <TELL "Yes" CR>)>
        inner = Form(Atom("TELL"), [String("Yes"), Atom("CR")])
        form = Form(Atom("COND"), [[Atom("T"), inner]])
        result = expander.expand(form)

        # Outer form should still be COND
        assert result.operator.value == "COND"

        # Inner TELL should be expanded to PROG
        cond_clause = result.args[0]
        assert isinstance(cond_clause, list)
        expanded_inner = cond_clause[1]
        assert isinstance(expanded_inner, Form)
        assert expanded_inner.operator.value == "PROG"

    def test_expand_routine_body(self, expander):
        """Routine bodies have macros expanded."""
        routine = Routine(
            name="TEST",
            args=[],
            body=[Form(Atom("TELL"), [String("Test"), Atom("CR")])]
        )
        result = expander.expand_routine(routine)

        # Routine structure preserved
        assert result.name == "TEST"
        assert result.args == []

        # Body expanded
        assert len(result.body) == 1
        assert result.body[0].operator.value == "PROG"

    def test_expand_with_list(self, expander):
        """Lists of nodes are expanded recursively."""
        nodes = [
            Form(Atom("TELL"), [String("First"), Atom("CR")]),
            Form(Atom("PRINT"), [String("Second")]),
            Form(Atom("TELL"), [String("Third")])
        ]
        result = expander.expand(nodes)

        assert len(result) == 3
        # First TELL expanded
        assert result[0].operator.value == "PROG"
        # PRINT unchanged
        assert result[1].operator.value == "PRINT"
        # Last TELL expanded
        assert result[2].operator.value == "PROG"

    def test_atom_unchanged(self, expander):
        """Plain atoms pass through unchanged."""
        atom = Atom("FOO")
        result = expander.expand(atom)
        assert result is atom

    def test_string_unchanged(self, expander):
        """Strings pass through unchanged."""
        string = String("Hello")
        result = expander.expand(string)
        assert result is string

    def test_deeply_nested_expansion(self, expander):
        """Macros nested multiple levels deep are expanded."""
        # <COND (<VERB? TAKE> <PROG () <TELL "You take it." CR>>)>
        innermost_tell = Form(Atom("TELL"), [String("You take it."), Atom("CR")])
        prog = Form(Atom("PROG"), [[], innermost_tell])
        verb_check = Form(Atom("VERB?"), [Atom("TAKE")])
        cond_form = Form(Atom("COND"), [[verb_check, prog]])

        result = expander.expand(cond_form)

        # COND preserved
        assert result.operator.value == "COND"

        # Get the innermost TELL (now expanded to PROG)
        clause = result.args[0]
        outer_prog = clause[1]
        inner_tell_expanded = outer_prog.args[1]

        # The TELL inside PROG should be expanded
        assert isinstance(inner_tell_expanded, Form)
        assert inner_tell_expanded.operator.value == "PROG"

    def test_multiple_tells_in_routine(self, expander):
        """Routine with multiple TELL calls all expanded."""
        routine = Routine(
            name="GREET",
            args=["NAME"],
            body=[
                Form(Atom("TELL"), [String("Hello, ")]),
                Form(Atom("TELL"), [String("Welcome!"), Atom("CR")])
            ]
        )
        result = expander.expand_routine(routine)

        assert len(result.body) == 2
        assert all(form.operator.value == "PROG" for form in result.body)

    def test_non_atom_operator(self, expander):
        """Forms with non-atom operators are handled gracefully."""
        # Edge case: <(FOO) "arg">  - operator is a form, not an atom
        weird_form = Form(Form(Atom("FOO"), []), [String("arg")])
        result = expander.expand(weird_form)

        # Should not crash, just expand args
        assert isinstance(result, Form)
        assert isinstance(result.args[0], String)
