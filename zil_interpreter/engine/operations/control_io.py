"""Control flow and I/O operations for ZIL."""

import random
from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom


class PerformOperation(Operation):
    """PERFORM - Execute parser action (simulates player command).

    Usage: <PERFORM verb-action [direct-obj] [indirect-obj]>

    Sets PRSA (action), PRSO (direct object), PRSI (indirect object) globals
    and executes the action handler for the verb.

    Example: <PERFORM ,V?OPEN ,PURPLE-BOOK>
    """

    @property
    def name(self) -> str:
        return "PERFORM"

    def execute(self, args: list, evaluator) -> Any:
        """Execute parser action with given verb and objects."""
        if not args:
            return None

        # Helper to get value from arg (Atom returns its value, not lookup)
        def get_value(arg):
            if hasattr(arg, 'value'):
                return arg.value.upper() if hasattr(arg.value, 'upper') else arg.value
            return evaluator.evaluate(arg)

        # Get verb action and objects
        verb = get_value(args[0])

        # Save old values (not strictly necessary in basic implementation)
        old_prsa = evaluator.world.get_global("PRSA")
        old_prso = evaluator.world.get_global("PRSO")
        old_prsi = evaluator.world.get_global("PRSI")

        # Set new parser globals
        evaluator.world.set_global("PRSA", verb)

        if len(args) > 1:
            prso = get_value(args[1])
            evaluator.world.set_global("PRSO", prso)
        else:
            evaluator.world.set_global("PRSO", None)

        if len(args) > 2:
            prsi = get_value(args[2])
            evaluator.world.set_global("PRSI", prsi)
        else:
            evaluator.world.set_global("PRSI", None)

        # Execute action handler (if routine_executor available)
        result = None
        if hasattr(evaluator, 'routine_executor'):
            executor = evaluator.routine_executor
            # Try to call the verb's action handler
            # In real ZIL, this would dispatch to object/room handlers
            # For now, we simulate basic action execution
            if isinstance(verb, str) and verb in executor.routines:
                result = executor.call_routine(verb, [])

        # Return result or TRUE by default
        return result if result is not None else True


class ApplyOperation(Operation):
    """APPLY - Call function with arguments dynamically.

    Usage: <APPLY function [arg1 arg2 ...]>

    First argument must be a function reference or routine name.
    Remaining arguments are passed to the function.

    Example: <APPLY <GET .C ,C-RTN>>
    """

    @property
    def name(self) -> str:
        return "APPLY"

    def execute(self, args: list, evaluator) -> Any:
        """Call function with arguments dynamically."""
        if not args:
            return None

        func = evaluator.evaluate(args[0])
        func_args = [evaluator.evaluate(arg) for arg in args[1:]] if len(args) > 1 else []

        # If func is a routine name (string/atom), call it
        if hasattr(evaluator, 'routine_executor'):
            executor = evaluator.routine_executor

            func_name = func
            if isinstance(func, str):
                func_name = func.upper()

            if func_name in executor.routines:
                return executor.call_routine(func_name, func_args)

        # If func is callable (Python function), call it
        if callable(func):
            try:
                return func(*func_args)
            except Exception:
                return None

        return None


class GotoOperation(Operation):
    """GOTO - Change current room.

    Usage: <GOTO room>

    Moves player to new room, sets HERE global, and triggers room description
    by performing a LOOK action.

    Example: <GOTO ,VOLCANO-BOTTOM>
    """

    @property
    def name(self) -> str:
        return "GOTO"

    def execute(self, args: list, evaluator) -> Any:
        """Change current room."""
        if not args:
            return None

        # Evaluate room argument
        room_arg = args[0]
        room_val = room_arg.value if isinstance(room_arg, Atom) else evaluator.evaluate(room_arg)
        room_obj = evaluator.world.get_object(room_val)
        if not room_obj:
            return None

        # Set HERE global to room object
        evaluator.world.set_global("HERE", room_obj)
        evaluator.world.set_current_room(room_obj)

        # Move player to room (matches ZIL: <MOVE ,PLAYER ,HERE>)
        player = evaluator.world.get_global("PLAYER")
        if player:
            from zil_interpreter.world.game_object import GameObject
            if isinstance(player, GameObject):
                player.move_to(room_obj)

        # Display room description via V-LOOK
        if hasattr(evaluator, 'routine_executor'):
            executor = evaluator.routine_executor
            if "V-LOOK" in executor.routines:
                try:
                    executor.call_routine("V-LOOK", [])
                except Exception:
                    # Fallback: print room description directly
                    desc = room_obj.description or room_obj.name
                    evaluator.output.write(f"{desc}\n")
                    ldesc = room_obj.get_property("LDESC")
                    if ldesc:
                        evaluator.output.write(f"{ldesc}\n")

        return True


class RandomOperation(Operation):
    """RANDOM - Generate random number.

    Usage: <RANDOM N>

    Returns a random integer from 1 to N (inclusive).
    Range is 1..N, not 0..N-1!

    Example: <RANDOM 7> ; returns 1, 2, 3, 4, 5, 6, or 7
    """

    @property
    def name(self) -> str:
        return "RANDOM"

    def execute(self, args: list, evaluator) -> int:
        """Generate random number from 1 to N."""
        if not args:
            return 1

        n = evaluator.evaluate(args[0])

        if not isinstance(n, int) or n < 1:
            return 1

        # Return random integer from 1 to N (inclusive)
        return random.randint(1, n)


class PrintdOperation(Operation):
    """PRINTD - Print object description.

    Usage: <PRINTD object>

    Prints the short description (DESC property) of an object.
    Always returns TRUE.

    Example: <PRINTD ,LAMP> ; prints "a brass lantern"
    """

    @property
    def name(self) -> str:
        return "PRINTD"

    def execute(self, args: list, evaluator) -> bool:
        """Print object description."""
        if not args:
            return True

        # Get object - evaluate the argument and look up via get_object
        obj_arg = args[0]
        obj_val = obj_arg.value if isinstance(obj_arg, Atom) else evaluator.evaluate(obj_arg)
        obj = evaluator.world.get_object(obj_val)
        if not obj:
            return True

        # Get description: try DESC property first, then object description
        desc = obj.get_property("DESC") or obj.description
        if desc:
            evaluator.output.write(str(desc))

        return True


class CrlfOperation(Operation):
    """CRLF - Print newline.

    Usage: <CRLF>

    Prints a carriage return / line feed (newline).
    Always returns TRUE.

    Example: <CRLF> ; prints "\n"
    """

    @property
    def name(self) -> str:
        return "CRLF"

    def execute(self, args: list, evaluator) -> bool:
        """Print newline."""
        evaluator.output.write("\n")
        return True
