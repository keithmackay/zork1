"""ZIL file loader and parser."""

from pathlib import Path
from typing import List
from lark import Lark
from zil_interpreter.parser.grammar import ZIL_GRAMMAR
from zil_interpreter.parser.transformer import ZILTransformer
from zil_interpreter.parser.ast_nodes import ASTNode, Form, Atom, Global, Routine, Object as ObjectNode


class ZILLoader:
    """Loads and parses ZIL source files."""

    def __init__(self):
        self.parser = Lark(ZIL_GRAMMAR, start='start', parser='lalr')
        self.transformer = ZILTransformer()

    def load_file(self, filepath: Path) -> List[ASTNode]:
        """Load and parse a ZIL file into AST.

        Args:
            filepath: Path to the .zil file

        Returns:
            List of AST nodes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not filepath.exists():
            raise FileNotFoundError(f"ZIL file not found: {filepath}")

        content = filepath.read_text()
        tree = self.parser.parse(content)
        ast = self.transformer.transform(tree)

        # Convert top-level forms to semantic nodes
        return self._process_top_level(ast)

    def _process_top_level(self, nodes: List[ASTNode]) -> List[ASTNode]:
        """Process top-level forms into semantic nodes.

        Args:
            nodes: Raw AST nodes from transformer

        Returns:
            Processed nodes with ROUTINE, GLOBAL, etc. recognized
        """
        processed = []

        for node in nodes:
            if isinstance(node, Form):
                # Recognize special forms
                op = node.operator.value.upper()

                if op == "GLOBAL" and len(node.args) >= 1:
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    value = node.args[1] if len(node.args) > 1 else None
                    processed.append(Global(name=name, value=value))

                elif op == "ROUTINE" and len(node.args) >= 2:
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    raw_args = node.args[1] if isinstance(node.args[1], list) else []
                    args = [arg.value if isinstance(arg, Atom) else str(arg) for arg in raw_args]
                    body = node.args[2:] if len(node.args) > 2 else []
                    processed.append(Routine(name=name, args=args, body=body))

                elif op == "OBJECT" and len(node.args) >= 1:
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    properties = {}

                    # Parse property list from remaining args
                    for arg in node.args[1:]:
                        if isinstance(arg, list) and len(arg) > 0:
                            # Property is a list like (DESC "brass lamp")
                            prop_name = arg[0].value.upper() if isinstance(arg[0], Atom) else str(arg[0])
                            prop_value = arg[1] if len(arg) == 2 else arg[1:]
                            properties[prop_name] = prop_value
                        elif isinstance(arg, Form):
                            prop_name = arg.operator.value.upper()
                            prop_value = arg.args[0] if len(arg.args) == 1 else arg.args
                            properties[prop_name] = prop_value

                    processed.append(ObjectNode(name=name, properties=properties))

                else:
                    # Keep as generic form
                    processed.append(node)
            else:
                # Keep other nodes as-is
                if node is not None:
                    processed.append(node)

        return processed
