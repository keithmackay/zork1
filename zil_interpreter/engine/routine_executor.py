"""ZIL routine executor."""

from typing import Any, Dict, List, Optional, Tuple
from zil_interpreter.parser.ast_nodes import Routine, Atom, String, Form
from zil_interpreter.world.world_state import WorldState
from zil_interpreter.runtime.output_buffer import OutputBuffer
from zil_interpreter.engine.evaluator import Evaluator, ReturnValue


class RoutineExecutor:
    """Executes ZIL routines."""

    def __init__(self, world: WorldState, output: Optional[OutputBuffer] = None):
        self.world = world
        self.output = output or OutputBuffer()
        self.evaluator = Evaluator(world, self.output)
        self.evaluator.routine_executor = self  # Link back for routine calls
        self.routines: Dict[str, Routine] = {}
        self._parsed_args: Dict[str, List[Tuple[str, Any, bool, bool]]] = {}

    def register_routine(self, routine: Routine) -> None:
        """Register a routine for execution.

        Args:
            routine: Routine AST node
        """
        self.routines[routine.name.upper()] = routine
        # Parse args into proper format
        self._parsed_args[routine.name.upper()] = self._parse_args(routine.args)

    def _parse_args(self, args: list) -> List[Tuple[str, Any, bool, bool]]:
        """Parse routine args, handling OPTIONAL and AUX markers.

        Returns:
            List of tuples: (name, default, is_optional, is_aux)
        """
        result = []
        mode = "required"

        for arg in args:
            # Handle already-parsed tuples
            if isinstance(arg, tuple):
                result.append(arg)
                continue

            # Handle string markers and string representations
            if isinstance(arg, str):
                upper = arg.upper()
                if "OPTIONAL" in upper:
                    mode = "optional"
                    continue
                elif "AUX" in upper:
                    mode = "aux"
                    continue

                # Check if it's a string representation of a list
                # e.g., "[Atom(value='LOOK?'), Form(operator=Atom(value='FALSE'), args=[])]"
                if arg.startswith("[") and "Atom(value=" in arg:
                    # Extract parameter name from list representation
                    import re
                    match = re.search(r"Atom\(value='([^']+)'\)", arg)
                    if match:
                        name = match.group(1)
                        # Default value would be complex to extract, use None for now
                        result.append((name, None, mode == "optional", mode == "aux"))
                        continue

                # Regular string parameter name
                result.append((arg, None, mode == "optional", mode == "aux"))
                continue

            # Handle String AST node
            if isinstance(arg, String):
                upper = arg.value.upper()
                if upper == "OPTIONAL":
                    mode = "optional"
                    continue
                elif upper == "AUX":
                    mode = "aux"
                    continue

            # Handle Atom (parameter name)
            if isinstance(arg, Atom):
                result.append((arg.value, None, mode == "optional", mode == "aux"))
                continue

            # Handle list (parameter with default)
            if isinstance(arg, list) and len(arg) >= 1:
                first = arg[0]
                name = first.value if isinstance(first, Atom) else str(first)
                default = arg[1] if len(arg) > 1 else None
                result.append((name, default, mode == "optional", mode == "aux"))

        return result

    def call_routine(self, name: str, args: List[Any]) -> Any:
        """Call a routine by name with arguments.

        Args:
            name: Routine name
            args: Argument values (passed by caller)

        Returns:
            Return value from routine (last expression or explicit return)
        """
        routine_name = name.upper()
        routine = self.routines.get(routine_name)
        if not routine:
            raise ValueError(f"Unknown routine: {name}")

        # Create local variable scope
        local_scope: Dict[str, Any] = {}

        # Get parsed args
        parsed_args = self._parsed_args.get(routine_name, [])

        # Bind arguments to parameters
        arg_index = 0
        for param_name, default_value, is_optional, is_aux in parsed_args:
            if is_aux:
                # AUX variables - initialize to default or None
                if default_value is not None:
                    local_scope[param_name.upper()] = self.evaluator.evaluate(default_value)
                else:
                    local_scope[param_name.upper()] = None
            elif arg_index < len(args):
                # Positional argument provided
                local_scope[param_name.upper()] = args[arg_index]
                arg_index += 1
            elif default_value is not None:
                # Optional parameter with default - evaluate default
                local_scope[param_name.upper()] = self.evaluator.evaluate(default_value)
            else:
                # No argument provided and no default
                local_scope[param_name.upper()] = None

        # Save evaluator's current scope and set new scope
        old_scope = getattr(self.evaluator, 'local_scope', None)
        self.evaluator.local_scope = local_scope

        try:
            # Execute routine body
            result = None
            for expr in routine.body:
                result = self.evaluator.evaluate(expr)
            return result
        except ReturnValue as rv:
            return rv.value
        finally:
            # Restore previous scope
            if old_scope is not None:
                self.evaluator.local_scope = old_scope
            else:
                delattr(self.evaluator, 'local_scope')
