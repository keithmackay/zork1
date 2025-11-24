"""List operations for ZIL."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


class LengthOperation(Operation):
    """LENGTH - Get length of list or string."""

    @property
    def name(self) -> str:
        return "LENGTH"

    def execute(self, args: list, evaluator) -> int:
        """Get length of list or string.

        Args:
            args: [collection] - List or string to measure
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Length of the collection, or 0 if no arguments
        """
        if not args:
            return 0

        val = evaluator.evaluate(args[0])

        # Check if value has length
        if hasattr(val, '__len__'):
            return len(val)

        return 0


class NthOperation(Operation):
    """NTH - Get nth element (1-indexed)."""

    @property
    def name(self) -> str:
        return "NTH"

    def execute(self, args: list, evaluator) -> Any:
        """Get nth element from list or string (1-indexed).

        Args:
            args: [collection, index] - Collection and 1-based index
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Element at index, or None if invalid
        """
        if len(args) < 2:
            return None

        collection = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])

        # Validate index
        if not isinstance(index, int) or index < 1:
            return None

        # Check if collection is indexable
        if not hasattr(collection, '__getitem__'):
            return None

        # Convert to 0-indexed
        zero_index = index - 1

        # Bounds check
        try:
            if zero_index >= len(collection):
                return None
            return collection[zero_index]
        except (IndexError, TypeError):
            return None


class RestOperation(Operation):
    """REST - Get tail (all but first element)."""

    @property
    def name(self) -> str:
        return "REST"

    def execute(self, args: list, evaluator) -> Any:
        """Get all elements except the first.

        Args:
            args: [collection] - List or string
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Collection with first element removed, empty if single element or empty
        """
        if not args:
            return []

        collection = evaluator.evaluate(args[0])

        # Handle lists
        if isinstance(collection, list):
            if len(collection) <= 1:
                return []
            return collection[1:]

        # Handle strings
        if isinstance(collection, str):
            if len(collection) <= 1:
                return ""
            return collection[1:]

        # Handle other sequences
        if hasattr(collection, '__getitem__') and hasattr(collection, '__len__'):
            if len(collection) <= 1:
                return [] if not isinstance(collection, str) else ""
            return collection[1:]

        return []


class FirstListOperation(Operation):
    """FIRST - Get first element of list/string."""

    @property
    def name(self) -> str:
        return "FIRST"

    def execute(self, args: list, evaluator) -> Any:
        """Get first element from list or string.

        Args:
            args: [collection] - List or string
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            First element, or None if empty or no arguments
        """
        if not args:
            return None

        collection = evaluator.evaluate(args[0])

        # Check if collection is indexable
        if not hasattr(collection, '__getitem__') or not hasattr(collection, '__len__'):
            return None

        # Check if empty
        if len(collection) == 0:
            return None

        return collection[0]


class NextOperation(Operation):
    """NEXT - Get next sibling object."""

    @property
    def name(self) -> str:
        return "NEXT"

    def execute(self, args: list, evaluator) -> Any:
        """Get next sibling object in parent's children list.

        Args:
            args: [object_name] - Object to find sibling of
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Next sibling object, or None if no siblings or at end
        """
        if not args:
            return None

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        obj = evaluator.world.get_object(obj_name)

        if not obj or not obj.parent:
            return None

        # Get parent's children as a list
        siblings = list(obj.parent.children)

        # Find current object in siblings
        try:
            current_index = siblings.index(obj)
            # Return next sibling if exists
            if current_index + 1 < len(siblings):
                return siblings[current_index + 1]
        except (ValueError, IndexError):
            pass

        return None


class BackOperation(Operation):
    """BACK - Get previous sibling object."""

    @property
    def name(self) -> str:
        return "BACK"

    def execute(self, args: list, evaluator) -> Any:
        """Get previous sibling object in parent's children list.

        Args:
            args: [object_name] - Object to find sibling of
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            Previous sibling object, or None if no siblings or at beginning
        """
        if not args:
            return None

        obj_name = args[0].value if isinstance(args[0], Atom) else str(evaluator.evaluate(args[0]))
        obj = evaluator.world.get_object(obj_name)

        if not obj or not obj.parent:
            return None

        # Get parent's children as a list
        siblings = list(obj.parent.children)

        # Find current object in siblings
        try:
            current_index = siblings.index(obj)
            # Return previous sibling if exists
            if current_index > 0:
                return siblings[current_index - 1]
        except (ValueError, IndexError):
            pass

        return None


class EmptyCheckOperation(Operation):
    """EMPTY? - Check if collection is empty."""

    @property
    def name(self) -> str:
        return "EMPTY?"

    def execute(self, args: list, evaluator) -> bool:
        """Check if collection is empty.

        Args:
            args: [value] - Value to check
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            True if empty/zero/None, False otherwise
        """
        if not args:
            return True

        val = evaluator.evaluate(args[0])

        # Check for None
        if val is None:
            return True

        # Check for zero (numeric empty)
        if isinstance(val, (int, float)) and val == 0:
            return True

        # Check for empty collections
        if hasattr(val, '__len__'):
            return len(val) == 0

        # Non-empty value
        return False


class MemqOperation(Operation):
    """MEMQ - Check membership in list/string."""

    @property
    def name(self) -> str:
        return "MEMQ"

    def execute(self, args: list, evaluator) -> bool:
        """Check if element is in collection.

        Args:
            args: [element, collection] - Element to find and collection to search
            evaluator: Evaluator instance for recursive evaluation

        Returns:
            True if element is in collection, False otherwise
        """
        if len(args) < 2:
            return False

        element = evaluator.evaluate(args[0])
        collection = evaluator.evaluate(args[1])

        # Check if collection is iterable
        if not hasattr(collection, '__iter__'):
            return False

        # For strings, check if element is substring
        if isinstance(collection, str):
            element_str = str(element)
            return element_str in collection

        # For lists and other iterables, check membership
        try:
            return element in collection
        except TypeError:
            return False
