"""Table access operations: GET, PUT, GETB, PUTB."""
from typing import Any, List
from zil_interpreter.engine.operations.base import Operation


class GetOp(Operation):
    """GET - retrieve word from table by index."""

    @property
    def name(self) -> str:
        return "GET"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("GET requires table and index")
        table_ref = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])

        # Handle property reference tuples from GETPT
        if isinstance(table_ref, tuple) and len(table_ref) == 2:
            obj, prop_name = table_ref
            if hasattr(obj, 'get_property'):
                prop_value = obj.get_property(prop_name)
                # If prop_value is a string (simple UEXIT room name), return it at index 0
                if isinstance(prop_value, str):
                    if index == 0:
                        return prop_value
                    return None
                # Index into the property value list
                if isinstance(prop_value, list) and 0 <= index < len(prop_value):
                    return prop_value[index]
                return None

        # Regular table access
        try:
            table = evaluator.world.get_table(table_ref)
            return table.get_word(index)
        except (KeyError, TypeError):
            return None


class PutOp(Operation):
    """PUT - set word in table by index."""

    @property
    def name(self) -> str:
        return "PUT"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 3:
            raise ValueError("PUT requires table, index, and value")
        table_name = evaluator.evaluate(args[0])
        index = evaluator.evaluate(args[1])
        value = evaluator.evaluate(args[2])
        table = evaluator.world.get_table(table_name)
        table.put_word(index, value)
        return value


class GetBOp(Operation):
    """GETB - retrieve byte from table by byte index."""

    @property
    def name(self) -> str:
        return "GETB"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 2:
            raise ValueError("GETB requires table and byte index")
        table_ref = evaluator.evaluate(args[0])
        byte_index = evaluator.evaluate(args[1])

        # Handle property reference tuples from GETPT
        if isinstance(table_ref, tuple) and len(table_ref) == 2:
            obj, prop_name = table_ref
            if hasattr(obj, 'get_property'):
                prop_value = obj.get_property(prop_name)
                # If prop_value is a string (simple UEXIT room name), return it at index 0
                if isinstance(prop_value, str):
                    if byte_index == 0:
                        return prop_value
                    return None
                # Index into the property value list
                if isinstance(prop_value, list) and 0 <= byte_index < len(prop_value):
                    return prop_value[byte_index]
                return None

        # Regular table access
        table = evaluator.world.get_table(table_ref)
        return table.get_byte(byte_index)


class PutBOp(Operation):
    """PUTB - set byte in table by byte index."""

    @property
    def name(self) -> str:
        return "PUTB"

    def execute(self, args: List[Any], evaluator: Any) -> Any:
        if len(args) < 3:
            raise ValueError("PUTB requires table, byte index, and value")
        table_name = evaluator.evaluate(args[0])
        byte_index = evaluator.evaluate(args[1])
        value = evaluator.evaluate(args[2])
        table = evaluator.world.get_table(table_name)
        table.put_byte(byte_index, value)
        return value
