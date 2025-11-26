"""File processor for ZIL multi-file compilation."""
from pathlib import Path
from typing import List, Set
from lark import Lark
from ..parser.grammar import ZIL_GRAMMAR
from ..parser.transformer import ZILTransformer
from ..parser.ast_nodes import InsertFile


class CircularDependencyError(Exception):
    """Raised when circular INSERT-FILE detected."""
    pass


class FileProcessor:
    """Processes ZIL files with INSERT-FILE support."""

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.parser = Lark(ZIL_GRAMMAR, start='start')
        self.transformer = ZILTransformer()
        self.loaded_files: Set[str] = set()

    def load_file(self, filename: str) -> List:
        """Load and parse a single ZIL file."""
        filepath = self.base_path / filename
        if not filepath.exists():
            # Try with .zil extension
            filepath = self.base_path / f"{filename.lower()}.zil"
        if not filepath.exists():
            raise FileNotFoundError(f"ZIL file not found: {filename}")

        content = filepath.read_text()
        tree = self.parser.parse(content)
        result = self.transformer.transform(tree)

        # Grammar uses ?start: which inlines single expressions
        # Ensure we always return a list
        if not isinstance(result, list):
            return [result]
        return result

    def load_all(self, filename: str) -> List:
        """Load file and recursively process INSERT-FILE directives."""
        result = []
        self.loaded_files.clear()  # Reset for fresh load_all() call
        self._load_recursive(filename, result)
        return result

    def _normalize_filename(self, filename: str) -> str:
        """Normalize filename for comparison (uppercase, with .ZIL extension)."""
        name = filename.upper()
        if not name.endswith('.ZIL'):
            name += '.ZIL'
        return name

    def _load_recursive(self, filename: str, result: List, stack: List[str] = None):
        """Recursively load file with cycle detection, expanding INSERT-FILE."""
        if stack is None:
            stack = []

        normalized = self._normalize_filename(filename)

        # Check for circular dependency (file in current loading stack)
        if normalized in stack:
            cycle_path = ' → '.join(stack + [normalized])
            raise CircularDependencyError(f"Circular dependency detected: {cycle_path}")

        # Skip if already loaded (prevents duplicate loading in diamond patterns)
        if normalized in self.loaded_files:
            return

        # Mark as loaded and add to stack
        self.loaded_files.add(normalized)
        stack.append(normalized)

        # Load and process the file
        forms = self.load_file(filename)
        for form in forms:
            if isinstance(form, InsertFile):
                self._load_recursive(form.filename, result, stack)
            else:
                result.append(form)

        # Remove from stack after processing
        stack.pop()
