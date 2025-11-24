"""Advanced ZIL operations for type checking and control flow."""

from typing import Any
from zil_interpreter.engine.operations.base import Operation
from zil_interpreter.parser.ast_nodes import Atom, Form, String, Number


# Exception for AGAIN control flow
class AgainException(Exception):
    """Exception to restart loop."""
    pass


class PrimtypeOperation(Operation):
    """Get primitive type code of a value.

    Syntax: <PRIMTYPE value>
    Returns: Integer type code

    Type codes:
    - LIST = 1
    - ATOM = 2
    - STRING = 3
    - NUMBER = 4
    - FORM = 5
    - OBJECT = 6
    - OTHER = 0

    Usage example:
    <PRIMTYPE ,MYLIST>  ; Returns 1 if MYLIST is a list
    """

    @property
    def name(self) -> str:
        return "PRIMTYPE"

    # Type constants
    TYPE_LIST = 1
    TYPE_ATOM = 2
    TYPE_STRING = 3
    TYPE_NUMBER = 4
    TYPE_FORM = 5
    TYPE_OBJECT = 6
    TYPE_OTHER = 0

    def execute(self, args: list, evaluator) -> int:
        """Get primitive type code of value."""
        if not args:
            return self.TYPE_OTHER

        value = evaluator.evaluate(args[0])

        if isinstance(value, list):
            return self.TYPE_LIST
        elif isinstance(value, str):
            return self.TYPE_STRING
        elif isinstance(value, int):
            return self.TYPE_NUMBER
        elif isinstance(value, Atom):
            return self.TYPE_ATOM
        elif isinstance(value, Form):
            return self.TYPE_FORM
        elif hasattr(value, 'name') and hasattr(value, 'properties'):
            return self.TYPE_OBJECT
        else:
            return self.TYPE_OTHER


class PrintbOperation(Operation):
    """Print buffered text.

    Syntax: <PRINTB buffer>
    Returns: TRUE

    Prints text from a buffer (string, bytes, or byte array).
    Always returns TRUE.

    Usage example:
    <PRINTB ,TEXT-BUFFER>  ; Print buffer contents
    """

    @property
    def name(self) -> str:
        return "PRINTB"

    def execute(self, args: list, evaluator) -> bool:
        """Print buffered text."""
        if not args:
            return True

        buffer = evaluator.evaluate(args[0])

        if isinstance(buffer, str):
            evaluator.output.write(buffer)
        elif isinstance(buffer, (bytes, bytearray)):
            # Decode and print
            try:
                text = buffer.decode('utf-8')
                evaluator.output.write(text)
            except Exception:
                evaluator.output.write(str(buffer))
        elif isinstance(buffer, list):
            # List of byte values - convert to string
            try:
                text = ''.join(chr(b) for b in buffer if isinstance(b, int))
                evaluator.output.write(text)
            except Exception:
                pass

        return True


class IgrtrQuestionOperation(Operation):
    """Integer greater than comparison.

    Syntax: <IGRTR? a b>
    Returns: TRUE if a > b, FALSE otherwise

    Compares two integers. May be unsigned variant or alias for G?.

    Usage example:
    <IGRTR? ,SCORE 100>  ; TRUE if SCORE > 100
    """

    @property
    def name(self) -> str:
        return "IGRTR?"

    def execute(self, args: list, evaluator) -> bool:
        """Integer greater than comparison."""
        if len(args) < 2:
            return False

        val1 = evaluator.evaluate(args[0])
        val2 = evaluator.evaluate(args[1])

        if not isinstance(val1, int) or not isinstance(val2, int):
            return False

        return val1 > val2


class AgainOperation(Operation):
    """Restart current loop.

    Syntax: <AGAIN>

    Restarts the current REPEAT loop from the beginning.
    Like 'continue' in C. Raises AgainException which should
    be caught by REPEAT operation.

    Usage example:
    <REPEAT ()
        <COND (<SPECIAL-CASE> <AGAIN>)>
        ... normal processing ...
    >
    """

    @property
    def name(self) -> str:
        return "AGAIN"

    def execute(self, args: list, evaluator) -> None:
        """Restart current loop."""
        # Raise exception to signal loop restart
        # The REPEAT operation should catch this
        raise AgainException()


class TypeQuestionOperation(Operation):
    """Check if value is of given type(s).

    Syntax: <TYPE? value type1 [type2 ...]>
    Returns: TRUE if value matches any type, FALSE otherwise

    Can check multiple types with OR semantics.

    Type names:
    - LIST, VECTOR: List types
    - STRING, ZSTRING: String types
    - ATOM: Atom type
    - NUMBER, FIX: Integer types
    - FORM: Form type
    - OBJECT: Object type

    Usage example:
    <TYPE? ,VAL STRING NUMBER>  ; TRUE if VAL is string or number
    """

    @property
    def name(self) -> str:
        return "TYPE?"

    def execute(self, args: list, evaluator) -> bool:
        """Check if value is of given type(s)."""
        if len(args) < 2:
            return False

        value = evaluator.evaluate(args[0])

        # Check each type argument
        for type_arg in args[1:]:
            type_name = type_arg.value if isinstance(type_arg, Atom) else str(evaluator.evaluate(type_arg))
            type_name = type_name.upper()

            # Check type
            if type_name in ("LIST", "VECTOR"):
                if isinstance(value, list):
                    return True
            elif type_name in ("STRING", "ZSTRING"):
                if isinstance(value, str):
                    return True
            elif type_name == "ATOM":
                if isinstance(value, Atom):
                    return True
            elif type_name in ("NUMBER", "FIX"):
                if isinstance(value, int):
                    return True
            elif type_name == "FORM":
                if isinstance(value, Form):
                    return True
            elif type_name == "OBJECT":
                if hasattr(value, 'name') and hasattr(value, 'properties'):
                    return True

        return False


class ValueOperation(Operation):
    """Get variable value by name.

    Syntax: <VALUE symbol>
    Returns: Variable value, or None if not found

    Dynamic variable lookup by name. The argument is evaluated to get
    the name of the variable to look up. This allows indirect variable access.

    Usage example:
    <SET TABLE-NAME "LAMP-TABLE">
    <SET TBL <VALUE ,TABLE-NAME>>  ; Get value of variable named in TABLE-NAME
    """

    @property
    def name(self) -> str:
        return "VALUE"

    def execute(self, args: list, evaluator) -> Any:
        """Get variable value by name."""
        if not args:
            return None

        # Evaluate the argument to get the variable name
        # This could be a string or an atom that resolves to a string
        var_name_source = evaluator.evaluate(args[0])

        # Convert to variable name
        if isinstance(var_name_source, str):
            var_name = var_name_source.upper()
        elif isinstance(var_name_source, Atom):
            var_name = var_name_source.value.upper()
        elif isinstance(var_name_source, int):
            # If it's an integer, can't look up
            return None
        else:
            return None

        # Look up variable (try local scope first, then global)
        if hasattr(evaluator, 'local_scope') and var_name in evaluator.local_scope:
            return evaluator.local_scope[var_name]

        return evaluator.world.get_global(var_name)
