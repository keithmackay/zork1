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


class TestTableDataBytes:
    """Tests for TableData byte operations."""

    def test_get_byte_from_word_table(self):
        """GETB retrieves byte from word-based table."""
        # Word 0x0102 stored, get individual bytes
        table = TableData(name="TEST", data=[0x0102, 0x0304])
        # Byte 0 = high byte of word 0, Byte 1 = low byte of word 0
        assert table.get_byte(0) == 0x01
        assert table.get_byte(1) == 0x02
        assert table.get_byte(2) == 0x03
        assert table.get_byte(3) == 0x04

    def test_put_byte_modifies_word(self):
        """PUTB modifies specific byte within word."""
        table = TableData(name="TEST", data=[0x0000])
        table.put_byte(0, 0xAB)  # High byte
        assert table.get_word(0) == 0xAB00
        table.put_byte(1, 0xCD)  # Low byte
        assert table.get_word(0) == 0xABCD

    def test_get_byte_out_of_bounds_raises(self):
        """GETB with invalid byte index raises IndexError."""
        table = TableData(name="TEST", data=[0x0102])  # 2 bytes
        with pytest.raises(IndexError):
            table.get_byte(5)
