"""Load ZIL files and build game world."""

from pathlib import Path
from typing import List, Tuple
from zil_interpreter.parser.loader import ZILLoader
from zil_interpreter.parser.ast_nodes import Global, Routine, Object as ObjectNode, Number, String, Atom
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.world.game_object import GameObject
from zil_interpreter.engine.routine_executor import RoutineExecutor
from zil_interpreter.runtime.output_buffer import OutputBuffer


class WorldLoader:
    """Loads ZIL files and builds game world."""

    def __init__(self):
        self.zil_loader = ZILLoader()

    def load_world(self, main_file: Path, output: OutputBuffer) -> Tuple[WorldState, RoutineExecutor]:
        """Load game world from ZIL files.

        Args:
            main_file: Path to main .zil file
            output: OutputBuffer instance to use for all components

        Returns:
            Tuple of (WorldState, RoutineExecutor)
        """
        # Load and parse main file
        ast = self.zil_loader.load_file(main_file)

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
                game_obj.description = self._eval_value(prop_value)
            elif prop_name == "SYNONYM":
                # Handle synonym list
                if isinstance(prop_value, list):
                    game_obj.synonyms = [self._eval_value(v) for v in prop_value]
                else:
                    # Single synonym
                    game_obj.synonyms = [self._eval_value(prop_value)]
            else:
                game_obj.set_property(prop_name, self._eval_value(prop_value))

        world.add_object(game_obj)
