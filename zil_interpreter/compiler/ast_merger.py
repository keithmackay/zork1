"""AST merger for multi-file ZIL compilation."""
from typing import List, Any


class ASTMerger:
    """Merges ASTs from multiple ZIL files."""

    def merge(self, asts: List[List[Any]]) -> List[Any]:
        """Merge multiple AST lists into one.

        This simple utility concatenates AST lists in order, preserving
        the file order from the compilation process.

        Args:
            asts: List of AST lists from individual files

        Returns:
            Single merged AST list with all nodes in order
        """
        result = []
        for ast in asts:
            result.extend(ast)
        return result
