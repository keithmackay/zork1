"""Load ZIL files and build game world."""

from pathlib import Path
from typing import List, Tuple
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.parser.ast_nodes import Global, Routine, Object as ObjectNode, Number, String, Atom, Form
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.engine.routine_executor import RoutineExecutor
from zil_interpreter.runtime.output_buffer import OutputBuffer


class WorldLoader:
    """Loads ZIL files and builds game world."""

    def __init__(self):
        pass

    def load_world(self, main_file: Path, output: OutputBuffer) -> Tuple[WorldState, RoutineExecutor]:
        """Load game world from ZIL files.

        Args:
            main_file: Path to main .zil file
            output: OutputBuffer instance to use for all components

        Returns:
            Tuple of (WorldState, RoutineExecutor)
        """
        # Use FileProcessor to load with INSERT-FILE expansion
        processor = FileProcessor(base_path=main_file.parent)
        ast = processor.load_all(main_file.name)

        # Process raw AST into semantic nodes
        ast = self._process_top_level(ast)

        # Create world and executor with provided output buffer
        world = WorldState()
        executor = RoutineExecutor(world, output)  # Use provided buffer, don't create new one

        # Process AST nodes
        for node in ast:
            if isinstance(node, Global):
                world.set_global(node.name, self._eval_value(node.value))

            elif isinstance(node, Routine):
                executor.register_routine(node)

            elif isinstance(node, ObjectNode):
                self._create_object(world, node)

        return world, executor

    def _eval_value(self, value):
        """Evaluate a simple value (Number, String, Atom)."""
        if isinstance(value, Number):
            return value.value
        elif isinstance(value, String):
            return value.value
        elif isinstance(value, Atom):
            return value.value
        return value

    def _create_object(self, world: WorldState, obj_node: ObjectNode):
        """Create GameObject from Object AST node."""
        # Create game object
        game_obj = GameObject(name=obj_node.name)

        # Set properties from AST
        for prop_name, prop_value in obj_node.properties.items():
            if prop_name == "DESC":
                # DESC property value is a list, extract first element
                if isinstance(prop_value, list) and len(prop_value) > 0:
                    game_obj.description = self._eval_value(prop_value[0])
                else:
                    game_obj.description = self._eval_value(prop_value)
            elif prop_name == "SYNONYM":
                # Handle synonym list - prop_value is already a list from transformer
                if isinstance(prop_value, list):
                    game_obj.synonyms = [self._eval_value(v) for v in prop_value]
                else:
                    # Single synonym (shouldn't happen with new transformer)
                    game_obj.synonyms = [self._eval_value(prop_value)]
            else:
                # For other properties, handle both list and single values
                if isinstance(prop_value, list) and len(prop_value) > 0:
                    # If it's a single-element list, unwrap it
                    if len(prop_value) == 1:
                        game_obj.set_property(prop_name, self._eval_value(prop_value[0]))
                    else:
                        # Multiple values, keep as list
                        game_obj.set_property(prop_name, [self._eval_value(v) for v in prop_value])
                else:
                    game_obj.set_property(prop_name, self._eval_value(prop_value))

        world.add_object(game_obj)

    def _process_top_level(self, nodes: List) -> List:
        """Process top-level forms into semantic nodes.

        Args:
            nodes: Raw AST nodes from FileProcessor

        Returns:
            Processed nodes with ROUTINE, GLOBAL, OBJECT recognized
        """
        processed = []

        for node in nodes:
            if isinstance(node, Form):
                # Check if operator exists and is an Atom
                if not hasattr(node, 'operator') or node.operator is None:
                    continue

                op = node.operator.value.upper() if hasattr(node.operator, 'value') else str(node.operator).upper()

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
                            prop_name = arg[0].value.upper() if isinstance(arg[0], Atom) else str(arg[0])
                            prop_value = arg[1] if len(arg) == 2 else arg[1:]
                            properties[prop_name] = prop_value
                        elif isinstance(arg, Form):
                            prop_name = arg.operator.value.upper()
                            prop_value = arg.args[0] if len(arg.args) == 1 else arg.args
                            properties[prop_name] = prop_value

                    processed.append(ObjectNode(name=name, properties=properties))

                elif op == "ROOM" and len(node.args) >= 1:
                    # ROOM is similar to OBJECT but for rooms
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    properties = {"IS-ROOM": True}

                    for arg in node.args[1:]:
                        if isinstance(arg, list) and len(arg) > 0:
                            prop_name = arg[0].value.upper() if isinstance(arg[0], Atom) else str(arg[0])
                            prop_value = arg[1] if len(arg) == 2 else arg[1:]
                            properties[prop_name] = prop_value
                        elif isinstance(arg, Form):
                            prop_name = arg.operator.value.upper()
                            prop_value = arg.args[0] if len(arg.args) == 1 else arg.args
                            properties[prop_name] = prop_value

                    processed.append(ObjectNode(name=name, properties=properties))

                else:
                    # Keep as generic form (might be needed for evaluation)
                    processed.append(node)
            elif isinstance(node, (Global, Routine, ObjectNode)):
                # Already processed
                processed.append(node)
            elif node is not None:
                processed.append(node)

        return processed
