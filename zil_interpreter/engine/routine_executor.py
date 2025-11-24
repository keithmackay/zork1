"""ZIL routine executor."""

from typing import Any, Dict, List, Optional
from zil_interpreter.parser.ast_nodes import Routine
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.evaluator import Evaluator


class RoutineExecutor:
    """Executes ZIL routines."""

    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
        self.evaluator = Evaluator(world, self.output)
        self.routines: Dict[str, Routine] = {}

    def register_routine(self, routine: Routine) -> None:
        """Register a routine for execution.

        Args:
            routine: Routine AST node
        """
        self.routines[routine.name.upper()] = routine

    def call_routine(self, name: str, args: List[Any]) -> Any:
        """Call a routine by name with arguments.

        Args:
            name: Routine name
            args: Argument values

        Returns:
            Return value from routine (last expression or explicit return)
        """
        routine = self.routines.get(name.upper())
        if not routine:
            raise ValueError(f"Unknown routine: {name}")

        # Execute routine body
        result = None
        for expr in routine.body:
            result = self.evaluator.evaluate(expr)

        return result
