"""Tests for macro registry."""
import pytest
from zil_interpreter.compiler.macro_registry import MacroRegistry
from zil_interpreter.parser.ast_nodes import MacroDef, MacroParam, Form, Atom


class TestMacroRegistry:
    """Tests for macro storage and lookup."""

    @pytest.fixture
    def registry(self):
        return MacroRegistry()

    def test_register_macro(self, registry):
        """Can register a macro definition."""
        macro = MacroDef(
            name="ENABLE",
            params=[MacroParam("INT", quoted=True)],
            body=Form(Atom("FORM"), [Atom("PUT")])
        )
        registry.register(macro)
        assert registry.has("ENABLE")

    def test_lookup_macro(self, registry):
        """Can retrieve registered macro."""
        macro = MacroDef(name="TEST", params=[], body=None)
        registry.register(macro)
        result = registry.get("TEST")
        assert result.name == "TEST"

    def test_case_insensitive_lookup(self, registry):
        """Macro lookup is case-insensitive."""
        macro = MacroDef(name="ENABLE", params=[], body=None)
        registry.register(macro)
        assert registry.has("enable")
        assert registry.has("Enable")
        assert registry.get("ENABLE") is registry.get("enable")

    def test_not_found_returns_none(self, registry):
        """Unknown macro returns None."""
        assert registry.get("UNKNOWN") is None
        assert not registry.has("UNKNOWN")

    def test_builtin_macros_available(self, registry):
        """Registry has built-in macros."""
        # TELL should be available as built-in
        assert registry.has("TELL")
