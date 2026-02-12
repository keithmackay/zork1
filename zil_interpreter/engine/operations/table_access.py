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
                return self._index_prop_value(prop_value, index)

        # Regular table access
        try:
            table = evaluator.world.get_table(table_ref)
            return table.get_word(index)
        except (KeyError, TypeError):
            return None

    @staticmethod
    def _index_prop_value(prop_value, index):
        """Index into a property value, handling typed exit tuples."""
        # Typed exit tuple: (exit_type, data_list)
        if isinstance(prop_value, tuple) and len(prop_value) == 2 and isinstance(prop_value[0], int):
            data = prop_value[1]
            if isinstance(data, list) and 0 <= index < len(data):
                return data[index]
            return None
        # Simple string (UEXIT room name or NEXIT message)
        if isinstance(prop_value, str):
            return prop_value if index == 0 else None
        # List
        if isinstance(prop_value, list) and 0 <= index < len(prop_value):
            return prop_value[index]
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
                return GetOp._index_prop_value(prop_value, byte_index)

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
