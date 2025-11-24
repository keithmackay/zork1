"""Game engine - coordinates parser, executor, and world state."""

from typing import Optional
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.command_parser import CommandParser
from zil_interpreter.engine.routine_executor import RoutineExecutor


class GameEngine:
    """Main game engine coordinating all components."""

    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
        self.parser = CommandParser(world)
        self.executor = RoutineExecutor(world, self.output)

    def execute_command(self, command: str) -> bool:
        """Execute a player command.

        Args:
            command: Player input string

        Returns:
            True if command was recognized and executed
        """
        # Parse command
        parsed = self.parser.parse(command)
        if not parsed:
            self.output.write("I don't understand that.\n")
            return False

        verb = parsed['verb']
        direct_obj = parsed['direct_object']
        indirect_obj = parsed['indirect_object']

        # Set parser state
        self.world.set_parser_state(
            verb=f"V-{verb}",
            direct_obj=direct_obj,
            indirect_obj=indirect_obj
        )

        # Try to call verb routine
        routine_name = f"V-{verb}"
        try:
            self.executor.call_routine(routine_name, [])
            return True
        except ValueError:
            # Routine not found
            self.output.write(f"I don't know how to {verb.lower()}.\n")
            return False
