# Chunk 2: File Processing - TDD Implementation Plan

**Goal:** Parse all 10 Zork I files and merge them via INSERT-FILE
**Branch:** `feature/zork1-compiler`
**Approach:** TDD (Red → Green → Refactor)

---

## Current State

**Files that parse (4/10):**
- ✓ zork1.zil (625 bytes)
- ✓ gmacros.zil (3,945 bytes)
- ✓ gsyntax.zil (17,933 bytes)
- ✓ gclock.zil (1,596 bytes)

**Files that fail (6/10):**
- ✗ gparser.zil - Line 130: Inline comment in nested form
- ✗ gverbs.zil - Line 570: Inline comment pattern
- ✗ gglobals.zil - Line 50: Inline comment `;"[not here]"`
- ✗ gmain.zil - Line 161: `==?` operator
- ✗ 1dungeon.zil - Line 68: Inline comment `;"-TOSSED"`
- ✗ 1actions.zil - Line 1784: Inline comment pattern

---

## Part A: Grammar Completion (Tasks 2.1-2.5)

Fix remaining syntax patterns to parse all Zork files.

### Task 2.1: Inline Comments in Property Lists

**Problem:** ZIL uses `;` comments mid-expression:
```zil
(ADJECTIVE LARGE STORM ;"-TOSSED")
(DESC "such thing" ;"[not here]")
```

**Solution:** Allow semicolon comments as expression alternatives.

**Test file:** `tests/parser/test_inline_comments.py`

```python
"""Tests for inline comment handling in ZIL grammar."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestInlineComments:
    """Tests for semicolon comments within expressions."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_inline_comment_in_list(self, parser):
        """Inline comment within parenthesized list."""
        code = '(ADJECTIVE LARGE STORM ;"-TOSSED")'
        tree = parser.parse(code)
        assert tree is not None

    def test_inline_comment_in_property(self, parser):
        """Inline comment after string in property."""
        code = '(DESC "such thing" ;"[not here]")'
        tree = parser.parse(code)
        assert tree is not None

    def test_inline_comment_before_close_paren(self, parser):
        """Comment immediately before closing paren."""
        code = '(A B ;comment\n)'
        tree = parser.parse(code)
        assert tree is not None

    def test_inline_comment_before_close_angle(self, parser):
        """Comment immediately before closing angle bracket."""
        code = '<FOO BAR ;comment\n>'
        tree = parser.parse(code)
        assert tree is not None

    def test_commented_out_form(self, parser):
        """Entire form commented out within expression."""
        code = '<COND (T ;<OLD-CODE> <NEW-CODE>)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_multiple_inline_comments(self, parser):
        """Multiple inline comments in one expression."""
        code = '(A ;first\n B ;second\n C)'
        tree = parser.parse(code)
        assert tree is not None
```

**Implementation:** Modify grammar to treat inline comments as whitespace within expressions.

```python
# In grammar.py, update COMMENT handling
COMMENT: /;[^\n]*/
%ignore COMMENT  # This already ignores, but need to verify placement
```

**Verification:** `pytest tests/parser/test_inline_comments.py -v`

---

### Task 2.2: Equality Operator ==?

**Problem:** `==?` operator not recognized:
```zil
<==? .V ,M-FATAL>
```

**Solution:** Add `==?` to OPERATOR terminal.

**Test file:** `tests/parser/test_equality_operator.py`

```python
"""Tests for ==? equality operator."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestEqualityOperator:
    """Tests for ==? operator in ZIL grammar."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_double_equal_question(self, parser):
        """==? operator is recognized."""
        code = '<==? .V ,M-FATAL>'
        tree = parser.parse(code)
        assert tree is not None

    def test_double_equal_question_in_cond(self, parser):
        """==? in COND clause."""
        code = '<COND (<==? .X 5> <PRINT "five">)>'
        tree = parser.parse(code)
        assert tree is not None

    def test_not_equal_question(self, parser):
        """N==? operator (not equal)."""
        code = '<N==? .A .B>'
        tree = parser.parse(code)
        assert tree is not None
```

**Implementation:** Add `==?` and `N==?` to operator pattern:

```python
OPERATOR.2: /N?==\?|<=\?|=\?|>\?|<\?|G=\?|L=\?/
```

**Verification:** `pytest tests/parser/test_equality_operator.py -v`

---

### Task 2.3: Additional Comparison Operators

**Problem:** ZIL has more comparison operators than currently supported.

**Test file:** `tests/parser/test_comparison_operators.py`

```python
"""Tests for all ZIL comparison operators."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestComparisonOperators:
    """Tests for all comparison operators."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    @pytest.mark.parametrize("op", [
        "=?",      # equal
        "==?",     # identical
        "N==?",    # not identical
        "L?",      # less than
        "L=?",     # less or equal
        "G?",      # greater than
        "G=?",     # greater or equal
        "0?",      # is zero
        "1?",      # is one
    ])
    def test_comparison_operators(self, parser, op):
        """Each comparison operator parses correctly."""
        code = f'<{op} .X .Y>'
        tree = parser.parse(code)
        assert tree is not None

    def test_less_than_question(self, parser):
        """<? less-than operator."""
        code = '<<? .A .B>'
        tree = parser.parse(code)
        assert tree is not None

    def test_greater_than_question(self, parser):
        """>? greater-than operator."""
        code = '<>? .A .B>'
        tree = parser.parse(code)
        assert tree is not None
```

**Implementation:** Expand operator pattern:

```python
OPERATOR.2: /N?==\?|[LG]=\?|[LG01]\?|<=\?|=\?|>=\?|>\?|<\?/
```

**Verification:** `pytest tests/parser/test_comparison_operators.py -v`

---

### Task 2.4: Empty Forms

**Problem:** Some ZIL code may use `<>` (empty form).

**Test file:** `tests/parser/test_empty_forms.py`

```python
"""Tests for empty form handling."""
import pytest
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR


class TestEmptyForms:
    """Tests for empty form <>."""

    @pytest.fixture
    def parser(self):
        return Lark(ZIL_GRAMMAR, start='start')

    def test_empty_form(self, parser):
        """Empty form <> parses."""
        code = '<>'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_form_as_value(self, parser):
        """Empty form as false value."""
        code = '<SETG FLAG <>>'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_list(self, parser):
        """Empty list () parses."""
        code = '()'
        tree = parser.parse(code)
        assert tree is not None

    def test_empty_list_in_routine(self, parser):
        """Empty arg list in ROUTINE."""
        code = '<ROUTINE FOO () <PRINT "hi">>'
        tree = parser.parse(code)
        assert tree is not None
```

**Implementation:** Ensure form rule allows zero expressions:

```python
form: "<" atom? expression* ">"  # Already allows empty, verify
```

**Verification:** `pytest tests/parser/test_empty_forms.py -v`

---

### Task 2.5: Full Zork File Parsing

**Test:** Update integration test to require all 10 files to parse.

**Test file:** `tests/parser/test_zork_files.py` (update)

```python
@pytest.mark.parametrize("filename", [
    "zork1.zil",
    "gmacros.zil",
    "gsyntax.zil",
    "gparser.zil",
    "gverbs.zil",
    "gglobals.zil",
    "gmain.zil",
    "gclock.zil",
    "1dungeon.zil",
    "1actions.zil",
])
def test_parse_all_zork_files(self, parser, zork_dir, filename):
    """ALL Zork I files must parse completely."""
    filepath = zork_dir / filename
    if not filepath.exists():
        pytest.skip(f"zork1/{filename} not found at {filepath}")

    content = filepath.read_text()
    tree = parser.parse(content)
    assert tree is not None, f"{filename} failed to parse"
    print(f"\n✓ {filename} parsed successfully ({len(content)} bytes)")
```

**Verification:** `pytest tests/parser/test_zork_files.py -v` (all 10 pass)

---

## Part B: File Processing (Tasks 2.6-2.12)

Implement INSERT-FILE directive to merge all ZIL files.

### Task 2.6: FileProcessor Base Class

**Test file:** `tests/compiler/test_file_processor.py`

```python
"""Tests for ZIL file processor."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor


class TestFileProcessor:
    """Tests for file loading and processing."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_load_single_file(self, processor, tmp_path):
        """Load a single ZIL file."""
        (tmp_path / "test.zil").write_text('<GLOBAL FOO 1>')
        result = processor.load_file("test.zil")
        assert result is not None
        assert len(result) == 1

    def test_file_not_found(self, processor):
        """Missing file raises error."""
        with pytest.raises(FileNotFoundError):
            processor.load_file("nonexistent.zil")

    def test_base_path_resolution(self, tmp_path):
        """Files resolved relative to base path."""
        subdir = tmp_path / "src"
        subdir.mkdir()
        (subdir / "game.zil").write_text('<GLOBAL X 1>')

        processor = FileProcessor(base_path=subdir)
        result = processor.load_file("game.zil")
        assert result is not None
```

**Implementation:** `zil_interpreter/compiler/file_processor.py`

```python
"""File processor for ZIL multi-file compilation."""
from pathlib import Path
from typing import List, Optional, Set
from lark import Lark
from ..parser.grammar import ZIL_GRAMMAR
from ..parser.transformer import ZILTransformer


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
        return self.transformer.transform(tree)
```

**Verification:** `pytest tests/compiler/test_file_processor.py -v`

---

### Task 2.7: INSERT-FILE Detection

**Test file:** `tests/compiler/test_insert_file.py`

```python
"""Tests for INSERT-FILE directive handling."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.parser.ast_nodes import InsertFile


class TestInsertFileDetection:
    """Tests for detecting INSERT-FILE directives."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_detect_insert_file_form(self, processor, tmp_path):
        """INSERT-FILE form is detected."""
        (tmp_path / "main.zil").write_text('<INSERT-FILE "other" T>')
        result = processor.load_file("main.zil")
        # Should contain InsertFile node
        assert any(isinstance(n, InsertFile) for n in result)

    def test_insert_file_extracts_filename(self, processor, tmp_path):
        """INSERT-FILE extracts target filename."""
        (tmp_path / "main.zil").write_text('<INSERT-FILE "GMACROS" T>')
        result = processor.load_file("main.zil")
        insert = next(n for n in result if isinstance(n, InsertFile))
        assert insert.filename == "GMACROS"

    def test_multiple_insert_files(self, processor, tmp_path):
        """Multiple INSERT-FILE directives detected."""
        content = '''
        <INSERT-FILE "A" T>
        <INSERT-FILE "B" T>
        <INSERT-FILE "C" T>
        '''
        (tmp_path / "main.zil").write_text(content)
        result = processor.load_file("main.zil")
        inserts = [n for n in result if isinstance(n, InsertFile)]
        assert len(inserts) == 3
```

**Implementation:** Add InsertFile detection to transformer:

```python
# In transformer.py
def form(self, items):
    if items and str(items[0]).upper() == "INSERT-FILE":
        filename = items[1].value if len(items) > 1 else ""
        return InsertFile(filename=filename)
    # ... existing form handling
```

**Verification:** `pytest tests/compiler/test_insert_file.py -v`

---

### Task 2.8: Recursive File Loading

**Test file:** `tests/compiler/test_recursive_loading.py`

```python
"""Tests for recursive file loading."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor


class TestRecursiveLoading:
    """Tests for following INSERT-FILE directives."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_follow_insert_file(self, processor, tmp_path):
        """INSERT-FILE loads the referenced file."""
        (tmp_path / "main.zil").write_text('''
        <GLOBAL MAIN 1>
        <INSERT-FILE "other" T>
        ''')
        (tmp_path / "other.zil").write_text('<GLOBAL OTHER 2>')

        result = processor.load_all("main.zil")
        # Both globals should be present
        assert len([n for n in result if hasattr(n, 'name')]) >= 2

    def test_deep_nesting(self, processor, tmp_path):
        """Three levels of INSERT-FILE nesting."""
        (tmp_path / "a.zil").write_text('<INSERT-FILE "b" T>')
        (tmp_path / "b.zil").write_text('<INSERT-FILE "c" T>')
        (tmp_path / "c.zil").write_text('<GLOBAL DEEP 3>')

        result = processor.load_all("a.zil")
        assert any(getattr(n, 'name', '') == 'DEEP' for n in result)

    def test_preserves_order(self, processor, tmp_path):
        """Forms appear in correct order."""
        (tmp_path / "main.zil").write_text('''
        <GLOBAL FIRST 1>
        <INSERT-FILE "other" T>
        <GLOBAL LAST 3>
        ''')
        (tmp_path / "other.zil").write_text('<GLOBAL MIDDLE 2>')

        result = processor.load_all("main.zil")
        names = [n.name for n in result if hasattr(n, 'name')]
        assert names.index('FIRST') < names.index('MIDDLE') < names.index('LAST')
```

**Implementation:** Add `load_all` method:

```python
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
```

**Verification:** `pytest tests/compiler/test_recursive_loading.py -v`

---

### Task 2.9: Cycle Detection

**Test file:** `tests/compiler/test_cycle_detection.py`

```python
"""Tests for circular reference detection."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor, CircularDependencyError


class TestCycleDetection:
    """Tests for detecting circular INSERT-FILE chains."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_direct_cycle(self, processor, tmp_path):
        """File including itself raises error."""
        (tmp_path / "self.zil").write_text('<INSERT-FILE "self" T>')

        with pytest.raises(CircularDependencyError):
            processor.load_all("self.zil")

    def test_indirect_cycle(self, processor, tmp_path):
        """A → B → A raises error."""
        (tmp_path / "a.zil").write_text('<INSERT-FILE "b" T>')
        (tmp_path / "b.zil").write_text('<INSERT-FILE "a" T>')

        with pytest.raises(CircularDependencyError):
            processor.load_all("a.zil")

    def test_diamond_ok(self, processor, tmp_path):
        """Diamond pattern (A→B,C; B→D; C→D) is OK."""
        (tmp_path / "a.zil").write_text('''
        <INSERT-FILE "b" T>
        <INSERT-FILE "c" T>
        ''')
        (tmp_path / "b.zil").write_text('<INSERT-FILE "d" T>')
        (tmp_path / "c.zil").write_text('<INSERT-FILE "d" T>')
        (tmp_path / "d.zil").write_text('<GLOBAL SHARED 1>')

        # Should not raise (d included twice is OK)
        result = processor.load_all("a.zil")
        assert result is not None

    def test_no_duplicate_loading(self, processor, tmp_path):
        """Same file included twice is loaded once."""
        (tmp_path / "main.zil").write_text('''
        <INSERT-FILE "common" T>
        <INSERT-FILE "common" T>
        ''')
        (tmp_path / "common.zil").write_text('<GLOBAL X 1>')

        result = processor.load_all("main.zil")
        # X should appear only once
        x_count = sum(1 for n in result if getattr(n, 'name', '') == 'X')
        assert x_count == 1
```

**Implementation:** Track loading stack for cycles, loaded set for duplicates:

```python
class CircularDependencyError(Exception):
    """Raised when circular INSERT-FILE detected."""
    pass

def _load_recursive(self, filename: str, result: List, stack: List[str] = None):
    """Recursively load with cycle detection."""
    if stack is None:
        stack = []

    normalized = self._normalize_filename(filename)

    if normalized in stack:
        raise CircularDependencyError(f"Circular: {' → '.join(stack + [normalized])}")

    if normalized in self.loaded_files:
        return  # Already loaded

    self.loaded_files.add(normalized)
    stack.append(normalized)

    forms = self.load_file(filename)
    for form in forms:
        if isinstance(form, InsertFile):
            self._load_recursive(form.filename, result, stack)
        else:
            result.append(form)

    stack.pop()
```

**Verification:** `pytest tests/compiler/test_cycle_detection.py -v`

---

### Task 2.10: Path Resolution

**Test file:** `tests/compiler/test_path_resolution.py`

```python
"""Tests for file path resolution."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor


class TestPathResolution:
    """Tests for resolving INSERT-FILE paths."""

    @pytest.fixture
    def processor(self, tmp_path):
        return FileProcessor(base_path=tmp_path)

    def test_lowercase_extension(self, processor, tmp_path):
        """GMACROS resolves to gmacros.zil."""
        (tmp_path / "gmacros.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("GMACROS")
        assert result is not None

    def test_uppercase_extension(self, processor, tmp_path):
        """Handle .ZIL extension."""
        (tmp_path / "TEST.ZIL").write_text('<GLOBAL X 1>')
        result = processor.load_file("TEST")
        assert result is not None

    def test_with_extension(self, processor, tmp_path):
        """Explicit extension works."""
        (tmp_path / "test.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("test.zil")
        assert result is not None

    def test_case_insensitive(self, processor, tmp_path):
        """Case-insensitive filename matching."""
        (tmp_path / "GmAcRoS.zil").write_text('<GLOBAL X 1>')
        result = processor.load_file("gmacros")
        assert result is not None
```

**Implementation:**

```python
def _normalize_filename(self, filename: str) -> str:
    """Normalize filename for comparison."""
    name = filename.upper()
    if not name.endswith('.ZIL'):
        name += '.ZIL'
    return name

def _resolve_path(self, filename: str) -> Path:
    """Resolve filename to actual path."""
    # Try exact match
    path = self.base_path / filename
    if path.exists():
        return path

    # Try with .zil extension
    path = self.base_path / f"{filename}.zil"
    if path.exists():
        return path

    # Try lowercase
    path = self.base_path / f"{filename.lower()}.zil"
    if path.exists():
        return path

    # Case-insensitive search
    for p in self.base_path.iterdir():
        if p.name.upper() == self._normalize_filename(filename):
            return p

    raise FileNotFoundError(f"ZIL file not found: {filename}")
```

**Verification:** `pytest tests/compiler/test_path_resolution.py -v`

---

### Task 2.11: AST Merger

**Test file:** `tests/compiler/test_ast_merger.py`

```python
"""Tests for AST merger."""
import pytest
from zil_interpreter.compiler.ast_merger import ASTMerger
from zil_interpreter.parser.ast_nodes import Global, Routine, Object


class TestASTMerger:
    """Tests for merging multiple file ASTs."""

    @pytest.fixture
    def merger(self):
        return ASTMerger()

    def test_merge_globals(self, merger):
        """Merge globals from multiple files."""
        ast1 = [Global('A', 1)]
        ast2 = [Global('B', 2)]
        result = merger.merge([ast1, ast2])
        names = [n.name for n in result if isinstance(n, Global)]
        assert 'A' in names
        assert 'B' in names

    def test_merge_preserves_order(self, merger):
        """Merged AST preserves file order."""
        ast1 = [Global('FIRST', 1)]
        ast2 = [Global('SECOND', 2)]
        result = merger.merge([ast1, ast2])
        names = [n.name for n in result if isinstance(n, Global)]
        assert names.index('FIRST') < names.index('SECOND')

    def test_merge_mixed_types(self, merger):
        """Merge handles different node types."""
        ast1 = [Global('G', 1), Routine('R', [], [])]
        ast2 = [Object('O', {})]
        result = merger.merge([ast1, ast2])
        assert len(result) == 3

    def test_empty_merge(self, merger):
        """Merging empty list returns empty."""
        assert merger.merge([]) == []

    def test_single_file_merge(self, merger):
        """Single file returns its AST."""
        ast = [Global('X', 1)]
        result = merger.merge([ast])
        assert result == ast
```

**Implementation:** `zil_interpreter/compiler/ast_merger.py`

```python
"""AST merger for multi-file ZIL compilation."""
from typing import List, Any


class ASTMerger:
    """Merges ASTs from multiple ZIL files."""

    def merge(self, asts: List[List[Any]]) -> List[Any]:
        """Merge multiple AST lists into one."""
        result = []
        for ast in asts:
            result.extend(ast)
        return result
```

**Verification:** `pytest tests/compiler/test_ast_merger.py -v`

---

### Task 2.12: Zork I Integration Test

**Test file:** `tests/integration/test_zork_loading.py`

```python
"""Integration tests for loading Zork I."""
import pytest
from pathlib import Path
from zil_interpreter.compiler.file_processor import FileProcessor


class TestZorkLoading:
    """Integration tests for loading all Zork I files."""

    @pytest.fixture
    def zork_dir(self):
        # Find zork1 directory
        current = Path(__file__).parent
        while current != current.parent:
            candidate = current / "zork1"
            if candidate.exists():
                return candidate
            current = current.parent
        pytest.skip("zork1 directory not found")

    @pytest.fixture
    def processor(self, zork_dir):
        return FileProcessor(base_path=zork_dir)

    def test_load_all_zork_files(self, processor):
        """Load zork1.zil with all INSERT-FILE expansions."""
        result = processor.load_all("zork1.zil")
        assert result is not None
        assert len(result) > 100  # Expect many forms

    def test_all_nine_files_loaded(self, processor):
        """All 9 INSERT-FILE targets are loaded."""
        processor.load_all("zork1.zil")
        expected = {'GMACROS', 'GSYNTAX', '1DUNGEON', 'GGLOBALS',
                    'GCLOCK', 'GMAIN', 'GPARSER', 'GVERBS', '1ACTIONS'}
        loaded = {f.upper().replace('.ZIL', '') for f in processor.loaded_files}
        # Main file + 9 includes
        for exp in expected:
            assert any(exp in f for f in loaded), f"Missing {exp}"

    def test_no_circular_dependencies(self, processor):
        """Zork I has no circular INSERT-FILE."""
        # Should complete without CircularDependencyError
        result = processor.load_all("zork1.zil")
        assert result is not None

    def test_routine_count(self, processor):
        """Zork I has expected number of routines."""
        from zil_interpreter.parser.ast_nodes import Routine
        result = processor.load_all("zork1.zil")
        routines = [n for n in result if isinstance(n, Routine)]
        assert len(routines) > 50  # Many routines expected

    def test_object_count(self, processor):
        """Zork I has expected number of objects."""
        from zil_interpreter.parser.ast_nodes import Object
        result = processor.load_all("zork1.zil")
        objects = [n for n in result if isinstance(n, Object)]
        assert len(objects) > 100  # ~180 objects expected
```

**Verification:** `pytest tests/integration/test_zork_loading.py -v`

---

## File Structure

```
zil_interpreter/
├── compiler/
│   ├── __init__.py           # NEW
│   ├── file_processor.py     # NEW (Task 2.6-2.10)
│   └── ast_merger.py         # NEW (Task 2.11)
├── parser/
│   ├── grammar.py            # MODIFY (Tasks 2.1-2.4)
│   └── transformer.py        # MODIFY (Task 2.7)
└── ...

tests/
├── parser/
│   ├── test_inline_comments.py    # NEW (Task 2.1)
│   ├── test_equality_operator.py  # NEW (Task 2.2)
│   ├── test_comparison_operators.py # NEW (Task 2.3)
│   ├── test_empty_forms.py        # NEW (Task 2.4)
│   └── test_zork_files.py         # MODIFY (Task 2.5)
├── compiler/
│   ├── test_file_processor.py     # NEW (Task 2.6)
│   ├── test_insert_file.py        # NEW (Task 2.7)
│   ├── test_recursive_loading.py  # NEW (Task 2.8)
│   ├── test_cycle_detection.py    # NEW (Task 2.9)
│   ├── test_path_resolution.py    # NEW (Task 2.10)
│   └── test_ast_merger.py         # NEW (Task 2.11)
└── integration/
    └── test_zork_loading.py       # NEW (Task 2.12)
```

---

## Task Summary

| Task | Description | Test File | Impl File |
|------|-------------|-----------|-----------|
| 2.1 | Inline comments | test_inline_comments.py | grammar.py |
| 2.2 | ==? operator | test_equality_operator.py | grammar.py |
| 2.3 | All comparison ops | test_comparison_operators.py | grammar.py |
| 2.4 | Empty forms | test_empty_forms.py | grammar.py |
| 2.5 | All Zork files parse | test_zork_files.py | grammar.py |
| 2.6 | FileProcessor base | test_file_processor.py | file_processor.py |
| 2.7 | INSERT-FILE detection | test_insert_file.py | transformer.py |
| 2.8 | Recursive loading | test_recursive_loading.py | file_processor.py |
| 2.9 | Cycle detection | test_cycle_detection.py | file_processor.py |
| 2.10 | Path resolution | test_path_resolution.py | file_processor.py |
| 2.11 | AST merger | test_ast_merger.py | ast_merger.py |
| 2.12 | Zork integration | test_zork_loading.py | integration |

---

## Success Criteria

- [ ] All 10 Zork I files parse without error
- [ ] FileProcessor.load_all("zork1.zil") returns unified AST
- [ ] No circular dependency errors
- [ ] AST contains all routines, objects, and globals from all files
- [ ] All 12 tasks have passing tests
- [ ] Code committed with descriptive messages

---

## Dependencies

```
Chunk 1 (Parser Foundation) ─────► Chunk 2 (File Processing)
                                          │
                                          ▼
                                   Chunk 3 (Macro System)
```
