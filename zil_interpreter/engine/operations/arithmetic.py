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


class SubtractOperation(Operation):
    """- - Subtraction or negation."""

    @property
    def name(self) -> str:
        return "-"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return 0
        if len(args) == 1:
            # Unary negation
            return -evaluator.evaluate(args[0])
        # Binary subtraction (multiple args)
        result = evaluator.evaluate(args[0])
        for arg in args[1:]:
            result -= evaluator.evaluate(arg)
        return result


class MultiplyOperation(Operation):
    """* - Multiplication."""

    @property
    def name(self) -> str:
        return "*"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return 1  # Identity element for multiplication
        result = 1
        for arg in args:
            result *= evaluator.evaluate(arg)
        return result


class DivideOperation(Operation):
    """/ - Integer division."""

    @property
    def name(self) -> str:
        return "/"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return 0
        if len(args) == 1:
            return evaluator.evaluate(args[0])
        # Integer division (successive division)
        result = evaluator.evaluate(args[0])
        for arg in args[1:]:
            divisor = evaluator.evaluate(arg)
            if divisor != 0:
                result = int(result / divisor)  # Integer division
        return result


class ModOperation(Operation):
    """MOD - Modulo (remainder)."""

    @property
    def name(self) -> str:
        return "MOD"

    def execute(self, args: list, evaluator) -> Any:
        if not args:
            return 0
        if len(args) == 1:
            return evaluator.evaluate(args[0])
        # Modulo operation
        dividend = evaluator.evaluate(args[0])
        divisor = evaluator.evaluate(args[1])
        if divisor == 0:
            return dividend
        return dividend % divisor
