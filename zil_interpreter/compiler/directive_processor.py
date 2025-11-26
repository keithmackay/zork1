"""Compile-time directive processor for ZIL."""
from typing import Any, Dict, List, Optional, Set
from ..parser.ast_nodes import Form, Atom, Number, String, Global, Object


class DirectiveProcessor:
    """Process ZIL compile-time directives.

    Handles:
    - CONSTANT: Named constant definitions
    - GLOBAL: Global variable declarations
    - PROPDEF: Property default values
    - DIRECTIONS: Direction word definitions
    - BUZZ: Noise words (ignored by parser)
    - SYNONYM: Word aliases
    - SYNTAX: Verb pattern definitions
    """

    def __init__(self):
        """Initialize empty directive storage."""
        # CONSTANT definitions
        self._constants: Dict[str, Any] = {}

        # GLOBAL variable definitions
        self._globals: Dict[str, Any] = {}

        # PROPDEF property defaults
        self._property_defaults: Dict[str, Any] = {}

        # DIRECTIONS list
        self._directions: List[str] = []
        self._direction_set: Set[str] = set()

        # BUZZ noise words
        self._buzz_words: Set[str] = set()

        # SYNONYM mappings (alias -> primary)
        self._synonyms: Dict[str, str] = {}

        # SYNTAX table (initialized lazily)
        self._syntax_table: Optional['SyntaxTable'] = None

    @property
    def constants(self) -> Dict[str, Any]:
        """Get all CONSTANT definitions."""
        return self._constants

    @property
    def globals(self) -> Dict[str, Any]:
        """Get all GLOBAL definitions."""
        return self._globals

    @property
    def property_defaults(self) -> Dict[str, Any]:
        """Get all PROPDEF definitions."""
        return self._property_defaults

    @property
    def directions(self) -> List[str]:
        """Get DIRECTIONS list."""
        return self._directions

    @property
    def buzz_words(self) -> Set[str]:
        """Get BUZZ noise words."""
        return self._buzz_words

    @property
    def syntax_table(self) -> 'SyntaxTable':
        """Get SYNTAX table (lazy initialization)."""
        if self._syntax_table is None:
            from .syntax_table import SyntaxTable
            self._syntax_table = SyntaxTable()
        return self._syntax_table

    def process(self, node: Any) -> None:
        """Process a node that may be a directive.

        Args:
            node: AST node to process
        """
        # Handle Global AST nodes directly
        if isinstance(node, Global):
            self._process_global_node(node)
            return

        if not isinstance(node, Form):
            return

        if not isinstance(node.operator, Atom):
            return

        directive = node.operator.value.upper()

        # Dispatch to specific handler
        handlers = {
            "CONSTANT": self._process_constant,
            "GLOBAL": self._process_global,
            "PROPDEF": self._process_propdef,
            "DIRECTIONS": self._process_directions,
            "BUZZ": self._process_buzz,
            "SYNONYM": self._process_synonym,
            "SYNTAX": self._process_syntax,
        }

        handler = handlers.get(directive)
        if handler:
            handler(node.args)

    def _process_global_node(self, node: Global) -> None:
        """Process a Global AST node.

        Args:
            node: Global AST node
        """
        value = self._evaluate_value(node.value) if node.value is not None else None
        self._globals[node.name.upper()] = value

    def _process_constant(self, args: List[Any]) -> None:
        """Process CONSTANT directive.

        <CONSTANT name value>
        """
        if len(args) < 2:
            return

        name = self._get_atom_value(args[0])
        if name is None:
            return

        value = self._evaluate_value(args[1])
        self._constants[name.upper()] = value

    def _process_global(self, args: List[Any]) -> None:
        """Process GLOBAL directive.

        <GLOBAL name value>
        """
        if len(args) < 2:
            return

        name = self._get_atom_value(args[0])
        if name is None:
            return

        value = self._evaluate_value(args[1])
        self._globals[name.upper()] = value

    def _process_propdef(self, args: List[Any]) -> None:
        """Process PROPDEF directive.

        <PROPDEF property-name default-value>
        """
        if len(args) < 2:
            return

        name = self._get_atom_value(args[0])
        if name is None:
            return

        value = self._evaluate_value(args[1])
        self._property_defaults[name.upper()] = value

    def _process_directions(self, args: List[Any]) -> None:
        """Process DIRECTIONS directive.

        <DIRECTIONS NORTH EAST WEST SOUTH ...>
        """
        for arg in args:
            name = self._get_atom_value(arg)
            if name:
                self._directions.append(name.upper())
                self._direction_set.add(name.upper())

    def _process_buzz(self, args: List[Any]) -> None:
        """Process BUZZ directive.

        <BUZZ word1 word2 ...>
        """
        for arg in args:
            name = self._get_atom_value(arg)
            if name:
                self._buzz_words.add(name.upper())

    def _process_synonym(self, args: List[Any]) -> None:
        """Process SYNONYM directive.

        <SYNONYM primary alias1 alias2 ...>
        First word is primary, rest are aliases.
        """
        if len(args) < 2:
            return

        primary = self._get_atom_value(args[0])
        if primary is None:
            return

        primary = primary.upper()
        # Primary maps to itself
        self._synonyms[primary] = primary

        # Aliases map to primary
        for arg in args[1:]:
            alias = self._get_atom_value(arg)
            if alias:
                self._synonyms[alias.upper()] = primary

    def _process_syntax(self, args: List[Any]) -> None:
        """Process SYNTAX directive.

        <SYNTAX verb [OBJECT [(constraints)]] [prep [OBJECT [(constraints)]]] = action [preaction]>
        """
        # Will be implemented in Task 4.7
        from .syntax_table import parse_syntax_entry
        entry = parse_syntax_entry(args)
        if entry:
            self.syntax_table.add_entry_from_def(entry)

    def _get_atom_value(self, node: Any) -> Optional[str]:
        """Get string value from an Atom node."""
        if isinstance(node, Atom):
            return node.value
        return None

    def _evaluate_value(self, node: Any) -> Any:
        """Evaluate a value node.

        Returns primitive value for Number/String/Atom,
        or the node itself for complex forms.
        """
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Atom):
            # Check for special atoms
            if node.value.upper() == "T":
                return True
            return node.value
        elif isinstance(node, Form):
            # Check for empty form (false)
            if not node.args:
                return False
            if isinstance(node.operator, Atom):
                if node.operator.value.upper() == "<>" or node.operator.value == "":
                    return False
            # Return form for later evaluation
            return node
        else:
            return node

    # Lookup methods

    def get_constant(self, name: str) -> Optional[Any]:
        """Get a CONSTANT value by name (case-insensitive)."""
        return self._constants.get(name.upper())

    def get_global(self, name: str) -> Optional[Any]:
        """Get a GLOBAL value by name (case-insensitive)."""
        return self._globals.get(name.upper())

    def get_property_default(self, name: str) -> Optional[Any]:
        """Get a PROPDEF default value by name (case-insensitive)."""
        return self._property_defaults.get(name.upper())

    def is_direction(self, word: str) -> bool:
        """Check if word is a direction (case-insensitive)."""
        return word.upper() in self._direction_set

    def direction_index(self, word: str) -> int:
        """Get index of direction (case-insensitive).

        Returns -1 if not a direction.
        """
        try:
            return self._directions.index(word.upper())
        except ValueError:
            return -1

    def is_buzz_word(self, word: str) -> bool:
        """Check if word is a BUZZ noise word (case-insensitive)."""
        return word.upper() in self._buzz_words

    def get_canonical(self, word: str) -> str:
        """Get canonical form of a word (case-insensitive).

        If word is a SYNONYM alias, returns the primary.
        Otherwise returns the word itself (uppercased).
        """
        return self._synonyms.get(word.upper(), word.upper())
