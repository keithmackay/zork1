"""Comparison operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom
from zil_interpreter.world.game_object import ObjectFlag


class EqualOperation(Operation):
    """EQUAL? - Value equality check."""

    @property
    def name(self) -> str:
        return "EQUAL?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False
        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])
        return val1 == val2


class FsetCheckOperation(Operation):
    """FSET? - Check if object has flag set."""

    # Map ZIL flag names to ObjectFlag enum
    FLAG_MAP = {
        "OPENBIT": ObjectFlag.OPEN,
        "CONTAINERBIT": ObjectFlag.CONTAINER,
        "TAKEABLEBIT": ObjectFlag.TAKEABLE,
        "LOCKEDBIT": ObjectFlag.LOCKED,
        "NDESCBIT": ObjectFlag.NDESCBIT,
        "LIGHTBIT": ObjectFlag.LIGHTBIT,
        "ONBIT": ObjectFlag.ONBIT,
    }

    @property
    def name(self) -> str:
        return "FSET?"

    def execute(self, args: list, evaluator) -> bool:
        if len(args) < 2:
            return False

        # Get object name - if it's an Atom, use its value directly
        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        # Get flag name - same pattern
        flag_name = args[1].value if isinstance(args[1], Atom) else str(evaluator.evaluate(args[1]))

        obj = evaluator.world.get_object(obj_name)
        if not obj:
            return False

        flag = self.FLAG_MAP.get(flag_name.upper())
        if not flag:
            return False

        return obj.has_flag(flag)
