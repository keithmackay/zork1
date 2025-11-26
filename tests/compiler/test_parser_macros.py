"""Tests for parser-related macros (Task 3.8)."""
import pytest
from zil_interpreter.compiler.macro_expander import MacroExpander
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import Form, Atom, GlobalRef


class TestParserMacros:
    """Tests for VERB?, PRSO?, PRSI?, ROOM? macros."""

    @pytest.fixture
    def expander(self):
        return MacroExpander(MacroRegistry())

    def test_verb_single(self, expander):
        """VERB? with single verb."""
        # <VERB? TAKE>
        form = Form(Atom("VERB?"), [Atom("TAKE")])
        result = expander.expand(form)
        # <EQUAL? ,PRSA ,V?TAKE>
        assert isinstance(result, Form)
        assert result.operator.value == "EQUAL?"
        assert len(result.args) == 2
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "PRSA"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "V?TAKE"

    def test_verb_multiple(self, expander):
        """VERB? with multiple verbs creates OR."""
        # <VERB? TAKE DROP>
        form = Form(Atom("VERB?"), [Atom("TAKE"), Atom("DROP")])
        result = expander.expand(form)
        # <OR <EQUAL? ,PRSA ,V?TAKE> <EQUAL? ,PRSA ,V?DROP>>
        assert isinstance(result, Form)
        assert result.operator.value == "OR"
        assert len(result.args) == 2
        # First EQUAL?
        eq1 = result.args[0]
        assert isinstance(eq1, Form)
        assert eq1.operator.value == "EQUAL?"
        assert eq1.args[1].name == "V?TAKE"
        # Second EQUAL?
        eq2 = result.args[1]
        assert isinstance(eq2, Form)
        assert eq2.operator.value == "EQUAL?"
        assert eq2.args[1].name == "V?DROP"

    def test_verb_three_verbs(self, expander):
        """VERB? with three verbs."""
        # <VERB? TAKE DROP PUT>
        form = Form(Atom("VERB?"), [Atom("TAKE"), Atom("DROP"), Atom("PUT")])
        result = expander.expand(form)
        # <OR <EQUAL? ...> <EQUAL? ...> <EQUAL? ...>>
        assert result.operator.value == "OR"
        assert len(result.args) == 3

    def test_prso_check(self, expander):
        """PRSO? checks direct object."""
        # <PRSO? LAMP>
        form = Form(Atom("PRSO?"), [Atom("LAMP")])
        result = expander.expand(form)
        # <EQUAL? ,PRSO ,LAMP>
        assert isinstance(result, Form)
        assert result.operator.value == "EQUAL?"
        assert len(result.args) == 2
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "PRSO"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "LAMP"

    def test_prsi_check(self, expander):
        """PRSI? checks indirect object."""
        # <PRSI? SWORD>
        form = Form(Atom("PRSI?"), [Atom("SWORD")])
        result = expander.expand(form)
        # <EQUAL? ,PRSI ,SWORD>
        assert isinstance(result, Form)
        assert result.operator.value == "EQUAL?"
        assert len(result.args) == 2
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "PRSI"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "SWORD"

    def test_room_check(self, expander):
        """ROOM? checks current room."""
        # <ROOM? LIVING-ROOM>
        form = Form(Atom("ROOM?"), [Atom("LIVING-ROOM")])
        result = expander.expand(form)
        # <EQUAL? ,HERE ,LIVING-ROOM>
        assert isinstance(result, Form)
        assert result.operator.value == "EQUAL?"
        assert len(result.args) == 2
        assert isinstance(result.args[0], GlobalRef)
        assert result.args[0].name == "HERE"
        assert isinstance(result.args[1], GlobalRef)
        assert result.args[1].name == "LIVING-ROOM"

    def test_verb_case_insensitive(self, expander):
        """VERB? works regardless of case."""
        form = Form(Atom("verb?"), [Atom("TAKE")])
        result = expander.expand(form)
        assert result.operator.value == "EQUAL?"

    def test_prso_case_insensitive(self, expander):
        """PRSO? works regardless of case."""
        form = Form(Atom("prso?"), [Atom("LAMP")])
        result = expander.expand(form)
        assert result.operator.value == "EQUAL?"

    def test_prsi_case_insensitive(self, expander):
        """PRSI? works regardless of case."""
        form = Form(Atom("prsi?"), [Atom("SWORD")])
        result = expander.expand(form)
        assert result.operator.value == "EQUAL?"

    def test_room_case_insensitive(self, expander):
        """ROOM? works regardless of case."""
        form = Form(Atom("room?"), [Atom("LIVING-ROOM")])
        result = expander.expand(form)
        assert result.operator.value == "EQUAL?"
