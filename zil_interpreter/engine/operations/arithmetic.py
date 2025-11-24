"""Arithmetic operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation


class AddOperation(Operation):
    """+ - Addition."""

    @property
    def name(self) -> str:
        return "+"

    def execute(self, args: list, evaluator) -> Any:
        result = 0
        for arg in args:
            value = evaluator.evaluate(arg)
            if isinstance(value, (int, float)):
                result += value
        return result
