"""Macro expansion engine."""
from typing import Any, List
from .macro_registry import MacroRegistry
from .tell_macro import expand_tell
from .builtin_macros import (
    expand_enable, expand_disable, expand_rfatal,
    expand_verb, expand_prso, expand_prsi, expand_room,
    expand_bset, expand_bclear, expand_bset_question,
    expand_flaming, expand_openable, expand_abs, expand_prob
)
from ..parser.ast_nodes import Form, Atom, Routine, Object, Global


class MacroExpander:
    """Expands macros in ZIL AST."""

    def __init__(self, registry: MacroRegistry):
        """Initialize macro expander.

        Args:
            registry: MacroRegistry instance containing macro definitions
        """
        self.registry = registry
        self._builtin_expanders = {
            "TELL": expand_tell,
            # Task 3.7: Simple macros
            "ENABLE": expand_enable,
            "DISABLE": expand_disable,
            "RFATAL": expand_rfatal,
            # Task 3.8: Parser macros
            "VERB?": expand_verb,
            "PRSO?": expand_prso,
            "PRSI?": expand_prsi,
            "ROOM?": expand_room,
            # Task 3.9: Flag macros
            "BSET": expand_bset,
            "BCLEAR": expand_bclear,
            "BSET?": expand_bset_question,
            # Task 3.10: Conditional macros
            "FLAMING?": expand_flaming,
            "OPENABLE?": expand_openable,
            "ABS": expand_abs,
            "PROB": expand_prob,
        }

    def expand(self, node: Any) -> Any:
        """Recursively expand macros in AST node.

        Args:
            node: AST node to expand (Form, Routine, list, or other node type)

        Returns:
            Expanded AST node with all macros replaced
        """
        if isinstance(node, Form):
            return self._expand_form(node)
        elif isinstance(node, list):
            return [self.expand(item) for item in node]
        elif isinstance(node, Routine):
            return self.expand_routine(node)
        else:
            # Atoms, Strings, Numbers, etc. pass through unchanged
            return node

    def _expand_form(self, form: Form) -> Any:
        """Expand macros in a form.

        Args:
            form: Form to expand

        Returns:
            Expanded form or replacement node
        """
        if not isinstance(form.operator, Atom):
            # Operator is not an atom, can't be a macro
            # Just expand the args
            expanded_args = [self.expand(arg) for arg in form.args]
            return Form(form.operator, expanded_args)

        name = form.operator.value.upper()

        # Check for built-in macro
        if name in self._builtin_expanders:
            expanded = self._builtin_expanders[name](form.args)
            return self.expand(expanded)  # Recursively expand result

        # Check for user-defined macro (or built-in without expander yet)
        macro = self.registry.get(name)
        if macro and macro.body is not None:
            # User-defined macros with bodies will be expanded in future tasks
            expanded = self._expand_user_macro(macro, form.args)
            return self.expand(expanded)

        # Not a macro OR macro without expander yet - expand children
        expanded_args = [self.expand(arg) for arg in form.args]
        return Form(form.operator, expanded_args)

    def _expand_user_macro(self, macro, args):
        """Expand user-defined macro (placeholder for future implementation).

        Args:
            macro: MacroDef for the user-defined macro
            args: Arguments passed to the macro call

        Returns:
            Expanded form
        """
        # For now, just return the form unchanged
        # This will be implemented in future tasks
        return Form(Atom(macro.name), args)

    def expand_routine(self, routine: Routine) -> Routine:
        """Expand macros in routine body.

        Args:
            routine: Routine node to expand

        Returns:
            New Routine node with expanded body
        """
        expanded_body = [self.expand(form) for form in routine.body]
        return Routine(routine.name, routine.args, expanded_body)
