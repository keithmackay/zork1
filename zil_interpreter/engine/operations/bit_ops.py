"""Bit manipulation operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation


class BandOperation(Operation):
    """Bitwise AND operation.

    Performs bitwise AND on two integers.
    Arguments: <BAND value1 value2> → result

    Used extensively in parser for bit masking and flag checking (18 uses).
    """

    @property
    def name(self) -> str:
        return "BAND"

    def execute(self, args: list, evaluator) -> int:
        """Bitwise AND operation.

        Args:
            args: Two values to AND together
            evaluator: Evaluator for argument evaluation

        Returns:
            Bitwise AND of the two values, or 0 if invalid
        """
        if len(args) < 2:
            return 0

        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])

        if not isinstance(val1, int) or not isinstance(val2, int):
            return 0

        return val1 & val2


class BorOperation(Operation):
    """Bitwise OR operation.

    Performs bitwise OR on two integers.
    Arguments: <BOR value1 value2> → result

    Used for combining bit flags (6 uses).
    """

    @property
    def name(self) -> str:
        return "BOR"

    def execute(self, args: list, evaluator) -> int:
        """Bitwise OR operation.

        Args:
            args: Two values to OR together
            evaluator: Evaluator for argument evaluation

        Returns:
            Bitwise OR of the two values, or 0 if invalid
        """
        if len(args) < 2:
            return 0

        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])

        if not isinstance(val1, int) or not isinstance(val2, int):
            return 0

        return val1 | val2


class BtstOperation(Operation):
    """Bit test operation.

    Tests if specific bit(s) are set in value.
    Arguments: <BTST value bit-mask> → TRUE/FALSE
    Returns TRUE if (value & mask) != 0

    Very common in parser and flag checking (43 uses).
    """

    @property
    def name(self) -> str:
        return "BTST"

    def execute(self, args: list, evaluator) -> bool:
        """Bit test - returns TRUE if any masked bits are set.

        Args:
            args: Value and bit mask to test
            evaluator: Evaluator for argument evaluation

        Returns:
            True if (value & mask) != 0, False otherwise
        """
        if len(args) < 2:
            return False

        value = evaluator.evaluate(args[0])
        mask = evaluator.evaluate(args[1])

        if not isinstance(value, int) or not isinstance(mask, int):
            return False

        # Returns TRUE if (value & mask) != 0
        return (value & mask) != 0


class MapretOperation(Operation):
    """Return from MAPF iteration.

    Returns a value from current MAPF iteration.
    Arguments: <MAPRET value> → value (special return)

    Allows MAPF to collect results (23 uses).
    """

    @property
    def name(self) -> str:
        return "MAPRET"

    def execute(self, args: list, evaluator) -> Any:
        """Return value from MAPF iteration.

        Args:
            args: Value to return from iteration
            evaluator: Evaluator for argument evaluation

        Returns:
            Evaluated value, or None if no arguments
        """
        if not args:
            return None

        # Evaluate and return the value
        # In a full implementation, this would signal to MAPF
        # For now, we just return the value
        return evaluator.evaluate(args[0])
