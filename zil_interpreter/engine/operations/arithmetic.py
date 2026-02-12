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
            val = evaluator.evaluate(args[0])
            return -(val if isinstance(val, (int, float)) else 0)
        # Binary subtraction (multiple args)
        first = evaluator.evaluate(args[0])
        result = first if isinstance(first, (int, float)) else 0
        for arg in args[1:]:
            val = evaluator.evaluate(arg)
            result -= val if isinstance(val, (int, float)) else 0
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
            val = evaluator.evaluate(arg)
            result *= val if isinstance(val, (int, float)) else 0
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
        first = evaluator.evaluate(args[0])
        result = first if isinstance(first, (int, float)) else 0
        for arg in args[1:]:
            divisor = evaluator.evaluate(arg)
            if isinstance(divisor, (int, float)) and divisor != 0:
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
        raw_dividend = evaluator.evaluate(args[0])
        raw_divisor = evaluator.evaluate(args[1])
        dividend = raw_dividend if isinstance(raw_dividend, (int, float)) else 0
        divisor = raw_divisor if isinstance(raw_divisor, (int, float)) else 0
        if divisor == 0:
            return dividend
        return dividend % divisor
