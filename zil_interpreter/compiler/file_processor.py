"""File processor for ZIL multi-file compilation."""
from pathlib import Path
from typing import List, Set
from lark import Lark
from ..parser.grammar import ZIL_GRAMMAR
from ..parser.transformer import ZILTransformer
from ..parser.ast_nodes import InsertFile


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
        self._load_recursive(filename, result)
        return result

    def _load_recursive(self, filename: str, result: List):
        """Recursively load file, expanding INSERT-FILE."""
        forms = self.load_file(filename)
        for form in forms:
            if isinstance(form, InsertFile):
                self._load_recursive(form.filename, result)
            else:
                result.append(form)
