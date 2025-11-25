"""Tests for TableData class."""
import pytest
from zil_interpreter.world.table_data import TableData


class TestTableData:
    """Tests for TableData word operations."""

    def test_create_table_with_words(self):
        """Table created with initial word values."""
        table = TableData(name="TEST", data=[10, 20, 30])
        assert table.name == "TEST"
        assert len(table.data) == 3

    def test_get_word_returns_value_at_index(self):
        """GET retrieves word at specified index."""
        table = TableData(name="TEST", data=[100, 200, 300])
        assert table.get_word(0) == 100
        assert table.get_word(1) == 200
        assert table.get_word(2) == 300

    def test_put_word_sets_value_at_index(self):
        """PUT sets word at specified index."""
        table = TableData(name="TEST", data=[0, 0, 0])
        table.put_word(1, 999)
        assert table.get_word(1) == 999

    def test_get_word_out_of_bounds_raises(self):
        """GET with invalid index raises IndexError."""
        table = TableData(name="TEST", data=[1, 2])
        with pytest.raises(IndexError):
            table.get_word(5)
