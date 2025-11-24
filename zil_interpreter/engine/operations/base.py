from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zil_interpreter.engine.evaluator import Evaluator

class Operation(ABC):
    """Base class for all ZIL operations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Operation name (e.g., 'AND', 'OR', '+', 'EQUAL?')"""
        pass

    @abstractmethod
    def execute(self, args: list, evaluator: 'Evaluator') -> Any:
        """Execute the operation with given arguments.

        Args:
            args: List of unevaluated AST nodes (arguments)
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Result of operation execution
        """
        pass


class OperationRegistry:
    """Registry for all ZIL operations."""

    def __init__(self):
        self._operations: Dict[str, Operation] = {}

    def register(self, operation: Operation) -> None:
        """Register an operation by its name (case-insensitive)."""
        self._operations[operation.name.upper()] = operation

    def get(self, name: str) -> Optional[Operation]:
        """Get operation by name (case-insensitive)."""
        return self._operations.get(name.upper())

    def has(self, name: str) -> bool:
        """Check if operation is registered."""
        return name.upper() in self._operations
