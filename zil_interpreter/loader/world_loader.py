"""Load ZIL files and build game world."""

from pathlib import Path
from typing import List, Tuple
from zil_interpreter.compiler.file_processor import FileProcessor
from zil_interpreter.parser.ast_nodes import Global, Routine, Object as ObjectNode, Number, String, Atom, Form, CharLiteral
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.engine.routine_executor import RoutineExecutor
from zil_interpreter.runtime.output_buffer import OutputBuffer


class WorldLoader:
    """Loads ZIL files and builds game world."""

    # Direction names for exit property detection
    DIRECTIONS = {'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN',
                  'NE', 'NW', 'SE', 'SW', 'IN', 'OUT', 'LAND'}

    def __init__(self):
        pass

    def _normalize_exit(self, prop_value):
        """Normalize exit property value for proper V-WALK interpretation.

        ZIL exit formats:
        - (DIR TO ROOM) → UEXIT: just store ROOM at index 0
        - (DIR "message") → NEXIT: store message
        - (DIR TO ROOM IF FLAG) → CEXIT: store [ROOM, FLAG]
        - (DIR TO ROOM IF DOOR IS OPEN) → DEXIT: store [ROOM, DOOR]

        Returns normalized value for storage.
        """
        if isinstance(prop_value, str):
            # Already a string (NEXIT message)
            return prop_value

        if isinstance(prop_value, list) and len(prop_value) >= 1:
            # Check if first element is 'TO'
            first = self._eval_value(prop_value[0])
            if isinstance(first, str) and first.upper() == 'TO':
                if len(prop_value) == 2:
                    # Simple exit: (DIR TO ROOM) → just the room name
                    return self._eval_value(prop_value[1])
                elif len(prop_value) >= 4:
                    # Conditional: (DIR TO ROOM IF FLAG ...)
                    # Keep as list but put room first for REXIT indexing
                    room = self._eval_value(prop_value[1])
                    rest = [self._eval_value(v) for v in prop_value[2:]]
                    return [room] + rest
            else:
                # Not starting with TO - return as is
                return [self._eval_value(v) for v in prop_value]

        return prop_value

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

        # Process AST nodes - first pass: create all objects
        for node in ast:
            if isinstance(node, Global):
                world.set_global(node.name, self._eval_value(node.value))

            elif isinstance(node, Routine):
                executor.register_routine(node)

            elif isinstance(node, ObjectNode):
                self._create_object(world, node)

        # Second pass: set up parent-child relationships
        self._setup_parent_relationships(world)

        return world, executor

    def _setup_parent_relationships(self, world: WorldState):
        """Set up parent-child relationships after all objects created."""
        for obj in world.objects.values():
            # Check PARENT property first (set by ROOM handler)
            parent_name = obj.properties.get("PARENT")
            # Fall back to IN property (used by OBJECT definitions)
            if not parent_name:
                parent_name = obj.properties.get("IN")
            if parent_name:
                if isinstance(parent_name, str):
                    parent_obj = world.get_object(parent_name)
                    if parent_obj:
                        obj.move_to(parent_obj)

    def _parse_routine_args(self, raw_args: list) -> list:
        """Parse routine argument list, handling OPTIONAL and AUX markers.

        ZIL routine args can be:
        - (arg1 arg2 ...)  - required args
        - ("OPTIONAL" (arg default) ...)  - optional args with defaults
        - ("AUX" local1 local2 ...)  - local variables

        Returns:
            List of tuples: (name, default, is_optional, is_aux)
        """
        result = []
        mode = "required"  # required, optional, or aux

        for arg in raw_args:
            # Check for mode markers
            if isinstance(arg, String):
                marker = arg.value.upper()
                if marker == "OPTIONAL":
                    mode = "optional"
                    continue
                elif marker == "AUX":
                    mode = "aux"
                    continue

            # Parse the argument based on current mode
            if isinstance(arg, Atom):
                # Simple parameter name
                name = arg.value
                result.append((name, None, mode == "optional", mode == "aux"))
            elif isinstance(arg, list) and len(arg) >= 1:
                # Parameter with default value: (NAME default)
                first = arg[0]
                name = first.value if isinstance(first, Atom) else str(first)
                default = arg[1] if len(arg) > 1 else None
                result.append((name, default, mode == "optional", mode == "aux"))

        return result

    def _eval_value(self, value):
        """Evaluate a simple value (Number, String, Atom, CharLiteral)."""
        if isinstance(value, Number):
            return value.value
        elif isinstance(value, String):
            return value.value
        elif isinstance(value, Atom):
            return value.value
        elif isinstance(value, CharLiteral):
            return value.char
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
                # Handle synonym list
                if isinstance(prop_value, list):
                    game_obj.synonyms = [self._eval_value(v) for v in prop_value]
                else:
                    game_obj.synonyms = [self._eval_value(prop_value)]
            elif prop_name == "ADJECTIVE":
                # Handle adjective list
                if isinstance(prop_value, list):
                    game_obj.adjectives = [self._eval_value(v) for v in prop_value]
                else:
                    game_obj.adjectives = [self._eval_value(prop_value)]
            elif prop_name == "FLAGS":
                # Set object flags from FLAGS property
                if isinstance(prop_value, list):
                    for flag in prop_value:
                        flag_name = self._eval_value(flag)
                        if isinstance(flag_name, str):
                            game_obj.set_flag(flag_name)
                elif isinstance(prop_value, (Atom, str)):
                    flag_name = self._eval_value(prop_value)
                    if isinstance(flag_name, str):
                        game_obj.set_flag(flag_name)
                # Also store as property for reference
                if isinstance(prop_value, list):
                    game_obj.set_property(prop_name, [self._eval_value(v) for v in prop_value])
                else:
                    game_obj.set_property(prop_name, self._eval_value(prop_value))
            elif prop_name == "ACTION":
                # Store action routine name
                if isinstance(prop_value, list) and len(prop_value) > 0:
                    game_obj.action_routine = self._eval_value(prop_value[0])
                else:
                    game_obj.action_routine = self._eval_value(prop_value)
                game_obj.set_property(prop_name, game_obj.action_routine)
            elif prop_name == "IN":
                # Store IN for parent relationship setup
                if isinstance(prop_value, list) and len(prop_value) > 0:
                    game_obj.set_property(prop_name, self._eval_value(prop_value[0]))
                else:
                    game_obj.set_property(prop_name, self._eval_value(prop_value))
            else:
                # For other properties, handle both list and single values
                if isinstance(prop_value, list) and len(prop_value) > 0:
                    if len(prop_value) == 1:
                        game_obj.set_property(prop_name, self._eval_value(prop_value[0]))
                    else:
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

                elif op == "DIRECTIONS":
                    # Generate P?xxx direction constants
                    for i, arg in enumerate(node.args):
                        dir_name = arg.value if isinstance(arg, Atom) else str(arg)
                        processed.append(Global(name=f"P?{dir_name}", value=Number(i)))

                elif op == "CONSTANT" and len(node.args) >= 1:
                    # CONSTANT is like GLOBAL but for compile-time constants
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    value = node.args[1] if len(node.args) > 1 else None
                    processed.append(Global(name=name, value=value))

                elif op == "ROUTINE" and len(node.args) >= 2:
                    name = node.args[0].value if isinstance(node.args[0], Atom) else str(node.args[0])
                    raw_args = node.args[1] if isinstance(node.args[1], list) else []
                    args = self._parse_routine_args(raw_args)
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
                    parent_set = False  # Track if we've set the parent IN

                    for arg in node.args[1:]:
                        if isinstance(arg, list) and len(arg) > 0:
                            prop_name = arg[0].value.upper() if isinstance(arg[0], Atom) else str(arg[0])
                            prop_value = arg[1] if len(arg) == 2 else arg[1:]

                            # Handle IN property specially:
                            # (IN ROOMS) means parent container
                            # (IN TO STONE-BARROW ...) means navigation direction
                            if prop_name == "IN":
                                if len(arg) == 2 and isinstance(arg[1], Atom):
                                    # Single atom like (IN ROOMS) - this is parent
                                    if not parent_set:
                                        properties["PARENT"] = arg[1].value
                                        parent_set = True
                                else:
                                    # Navigation direction like (IN TO ...)
                                    properties["IN"] = self._normalize_exit(prop_value)
                            elif prop_name in self.DIRECTIONS:
                                # Direction property - normalize exit format
                                properties[prop_name] = self._normalize_exit(prop_value)
                            else:
                                properties[prop_name] = prop_value
                        elif isinstance(arg, Form):
                            prop_name = arg.operator.value.upper()
                            prop_value = arg.args[0] if len(arg.args) == 1 else arg.args

                            # Same handling for Form-style properties
                            if prop_name == "IN":
                                if len(arg.args) == 1 and isinstance(arg.args[0], Atom):
                                    if not parent_set:
                                        properties["PARENT"] = arg.args[0].value
                                        parent_set = True
                                else:
                                    properties["IN"] = self._normalize_exit(prop_value)
                            elif prop_name in self.DIRECTIONS:
                                # Direction property - normalize exit format
                                properties[prop_name] = self._normalize_exit(prop_value)
                            else:
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
