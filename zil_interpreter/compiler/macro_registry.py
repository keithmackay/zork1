"""Macro registry for ZIL compilation."""
from typing import Dict, Optional
from ..parser.ast_nodes import MacroDef, MacroParam


class MacroRegistry:
    """Registry for macro definitions."""

    def __init__(self):
        self._macros: Dict[str, MacroDef] = {}
        self._register_builtins()

    def _register_builtins(self):
        """Register built-in macros like TELL.

        For now, we register placeholder MacroDef objects.
        Actual expansion logic will be implemented in later tasks.
        """
        # TELL - Text output macro (Task 3.3-3.5)
        self._macros["TELL"] = MacroDef(
            name="TELL",
            params=[MacroParam("ARGS", type="args")],
            body=None  # Expansion logic in tell_macro.py
        )

        # VERB? - Check parser action (Task 3.8)
        self._macros["VERB?"] = MacroDef(
            name="VERB?",
            params=[MacroParam("ATMS", type="args")],
            body=None
        )

        # PRSO? - Check direct object (Task 3.8)
        self._macros["PRSO?"] = MacroDef(
            name="PRSO?",
            params=[MacroParam("ATMS", type="args")],
            body=None
        )

        # PRSI? - Check indirect object (Task 3.8)
        self._macros["PRSI?"] = MacroDef(
            name="PRSI?",
            params=[MacroParam("ATMS", type="args")],
            body=None
        )

        # ROOM? - Check current room (Task 3.8)
        self._macros["ROOM?"] = MacroDef(
            name="ROOM?",
            params=[MacroParam("ATMS", type="args")],
            body=None
        )

        # BSET - Set flags (Task 3.9)
        self._macros["BSET"] = MacroDef(
            name="BSET",
            params=[MacroParam("OBJ"), MacroParam("FLAGS", type="args")],
            body=None
        )

        # BCLEAR - Clear flags (Task 3.9)
        self._macros["BCLEAR"] = MacroDef(
            name="BCLEAR",
            params=[MacroParam("OBJ"), MacroParam("FLAGS", type="args")],
            body=None
        )

        # BSET? - Test flags (Task 3.9)
        self._macros["BSET?"] = MacroDef(
            name="BSET?",
            params=[MacroParam("OBJ"), MacroParam("FLAGS", type="args")],
            body=None
        )

        # ENABLE - Enable interrupt (Task 3.7)
        self._macros["ENABLE"] = MacroDef(
            name="ENABLE",
            params=[MacroParam("INT", quoted=True)],
            body=None
        )

        # DISABLE - Disable interrupt (Task 3.7)
        self._macros["DISABLE"] = MacroDef(
            name="DISABLE",
            params=[MacroParam("INT", quoted=True)],
            body=None
        )

        # PROB - Probability check (Task 3.10)
        self._macros["PROB"] = MacroDef(
            name="PROB",
            params=[MacroParam("BASE", quoted=True), MacroParam("LOSER", quoted=True, type="optional")],
            body=None
        )

        # RFATAL - Restore fatal stack (Task 3.7)
        self._macros["RFATAL"] = MacroDef(
            name="RFATAL",
            params=[],
            body=None
        )

        # FLAMING? - Check if object is flaming (Task 3.10)
        self._macros["FLAMING?"] = MacroDef(
            name="FLAMING?",
            params=[MacroParam("OBJ")],
            body=None
        )

        # OPENABLE? - Check if object is openable (Task 3.10)
        self._macros["OPENABLE?"] = MacroDef(
            name="OPENABLE?",
            params=[MacroParam("OBJ")],
            body=None
        )

        # ABS - Absolute value (Task 3.10)
        self._macros["ABS"] = MacroDef(
            name="ABS",
            params=[MacroParam("NUM")],
            body=None
        )

    def register(self, macro: MacroDef) -> None:
        """Register a macro definition.

        Args:
            macro: MacroDef instance to register
        """
        self._macros[macro.name.upper()] = macro

    def get(self, name: str) -> Optional[MacroDef]:
        """Get macro by name (case-insensitive).

        Args:
            name: Name of the macro to retrieve

        Returns:
            MacroDef if found, None otherwise
        """
        return self._macros.get(name.upper())

    def has(self, name: str) -> bool:
        """Check if macro exists.

        Args:
            name: Name of the macro to check

        Returns:
            True if macro exists, False otherwise
        """
        return name.upper() in self._macros
