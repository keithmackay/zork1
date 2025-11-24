from .base import Operation, OperationRegistry
from .comparison import EqualOperation


def create_default_registry() -> OperationRegistry:
    """Create registry with all standard operations."""
    registry = OperationRegistry()

    # Comparison
    registry.register(EqualOperation())

    return registry


__all__ = ['Operation', 'OperationRegistry', 'create_default_registry']
