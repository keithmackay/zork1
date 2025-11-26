"""System operations: SAVE, RESTORE, RESTART, VERIFY, PRINC, DIRIN, DIROUT."""
import json
from typing import Any, List
from zil_interpreter.engine.operations.base import Operation


class SaveOp(Operation):
    """SAVE - save game state to file.

    Usage: <SAVE>

    Prompts for filename and saves game state.
    Returns True on success, False on failure.

    Example: <COND (<SAVE> <TELL "Ok.">)>
    """

    @property
    def name(self) -> str:
        return "SAVE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        try:
            filename = input("Save game to file: ")
            if not filename:
                filename = "game.sav"
            if not filename.endswith(".sav"):
                filename += ".sav"

            game_state = evaluator.world.serialize()
            with open(filename, "w") as f:
                json.dump(game_state, f)

            evaluator.output.write(f"Game saved to {filename}.\n")
            return True
        except (IOError, OSError, AttributeError) as e:
            evaluator.output.write(f"Save failed: {e}\n")
            return False


class RestoreOp(Operation):
    """RESTORE - restore game state from file.

    Usage: <RESTORE>

    Prompts for filename and restores game state.
    Returns True on success, False on failure.

    Example: <COND (<RESTORE> <TELL "Ok.">)>
    """

    @property
    def name(self) -> str:
        return "RESTORE"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        try:
            filename = input("Restore game from file: ")
            if not filename:
                filename = "game.sav"
            if not filename.endswith(".sav"):
                filename += ".sav"

            with open(filename, "r") as f:
                game_state = json.load(f)

            evaluator.world.deserialize(game_state)
            evaluator.output.write(f"Game restored from {filename}.\n")
            return True
        except FileNotFoundError:
            evaluator.output.write("Save file not found.\n")
            return False
        except (IOError, OSError, json.JSONDecodeError) as e:
            evaluator.output.write(f"Restore failed: {e}\n")
            return False


class RestartOp(Operation):
    """RESTART - restart game from beginning.

    Usage: <RESTART>

    Resets all game state to initial values.
    Returns True after restart.

    Example: <RESTART>
    """

    @property
    def name(self) -> str:
        return "RESTART"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        evaluator.world.reset()
        evaluator.output.write("Game restarted.\n")
        return True


class VerifyOp(Operation):
    """VERIFY - verify story file integrity.

    Usage: <VERIFY>

    In a compiled Z-machine, this checks the story file checksum.
    In our interpreter, we always return True (no checksum needed).

    Example: <COND (<VERIFY> <TELL "Ok.">) (T <TELL "Corrupted!">)>
    """

    @property
    def name(self) -> str:
        return "VERIFY"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        # Always succeeds in interpreter - no compiled story file to verify
        return True


class PrincOp(Operation):
    """PRINC - print character or atom without quotes.

    Usage: <PRINC value>

    Prints the value without any formatting or quotes.
    Unlike PRINT, doesn't add quotes around strings.

    Example: <PRINC "HELLO"> ; prints HELLO (no quotes)
    Example: <PRINC 42>      ; prints 42
    """

    @property
    def name(self) -> str:
        return "PRINC"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return None

        value = evaluator.evaluate(args[0])
        evaluator.output.write(str(value))
        return value


class DirinOp(Operation):
    """DIRIN - set input stream direction.

    Usage: <DIRIN stream-number>

    Sets the input stream:
    - 0: Keyboard (default)
    - 1: Script/file input

    Example: <DIRIN 1> ; read from script
    """

    @property
    def name(self) -> str:
        return "DIRIN"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return False

        stream = evaluator.evaluate(args[0])
        evaluator.world.set_global("INPUT-STREAM", stream)
        return True


class DiroutOp(Operation):
    """DIROUT - enable/disable output stream.

    Usage: <DIROUT stream-number>

    Positive enables, negative disables:
    - 1: Screen (default, always on)
    - 2: Transcript
    - 3: Memory table
    - 4: Script file

    Example: <DIROUT 4>  ; enable script output
    Example: <DIROUT -4> ; disable script output
    """

    @property
    def name(self) -> str:
        return "DIROUT"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if not args:
            return False

        stream = evaluator.evaluate(args[0])
        enable = stream > 0
        stream_num = abs(stream)

        evaluator.world.set_global(f"OUTPUT-STREAM-{stream_num}", enable)
        return True
