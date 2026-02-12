"""Game engine - coordinates parser, executor, and world state."""

from typing import Optional
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.command_parser import CommandParser
from zil_interpreter.engine.routine_executor import RoutineExecutor


class GameEngine:
    """Main game engine coordinating all components."""

    # Directions map to V-WALK with direction as PRSO
    DIRECTIONS = {'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN',
                  'NE', 'NW', 'SE', 'SW', 'NORTHEAST', 'NORTHWEST',
                  'SOUTHEAST', 'SOUTHWEST', 'IN', 'OUT', 'LAND'}

    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
        self.parser = CommandParser(world)
        self.executor = RoutineExecutor(world, self.output)

    # Direction word aliases
    DIRECTION_ALIASES = {
        'N': 'NORTH', 'S': 'SOUTH', 'E': 'EAST', 'W': 'WEST',
        'U': 'UP', 'D': 'DOWN',
        'NORTHEAST': 'NE', 'NORTHWEST': 'NW',
        'SOUTHEAST': 'SE', 'SOUTHWEST': 'SW',
        'ENTER': 'IN', 'EXIT': 'OUT', 'LEAVE': 'OUT',
    }

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

        # Handle direction commands - they use V-WALK
        if verb in self.DIRECTIONS:
            direct_obj = verb  # Direction becomes PRSO
            verb = 'WALK'
            # Set P-WALK-DIR to indicate this is a direction-based walk
            self.world.set_global('P-WALK-DIR', True)
        elif verb in self.DIRECTION_ALIASES:
            # ENTER→IN, EXIT→OUT, etc.
            direct_obj = self.DIRECTION_ALIASES[verb]
            verb = 'WALK'
            self.world.set_global('P-WALK-DIR', True)
        elif verb == 'GO':
            # Handle "go <direction>" - look for direction in command
            words = command.upper().split()
            for word in words[1:]:  # Skip the "go" verb
                # Check if word is a direction or direction alias
                if word in self.DIRECTIONS:
                    direct_obj = word
                    verb = 'WALK'
                    self.world.set_global('P-WALK-DIR', True)
                    break
                elif word in self.DIRECTION_ALIASES:
                    direct_obj = self.DIRECTION_ALIASES[word]
                    verb = 'WALK'
                    self.world.set_global('P-WALK-DIR', True)
                    break
            else:
                # No direction found, clear P-WALK-DIR
                self.world.set_global('P-WALK-DIR', False)
        else:
            # Clear P-WALK-DIR for non-direction commands
            self.world.set_global('P-WALK-DIR', False)

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
        except Exception as e:
            # Other execution errors - log for debugging
            self.output.write(f"Error: {e}\n")
            return False
