# -*- coding:utf-8 -*-

import unittest

from pytidbrep.event import RowsEvent
from pytidbrep.event import read_int32_word


class TestEvent(unittest.TestCase):

    def test_read_int32_word(self):
        row = '112233'.decode("hex")
        v = read_int32_word(row, 3)
        assert 1122867 == v

        row = 'EEDDCC'.decode("hex")
        v = read_int32_word(row, 3)
        v = ~v
        assert 1122867 == v

    def test_parse_int(self):
        pass

    def test_parse_uint(self):
        pass

    def test_read_varint(self):
        pass

    def test_read_uvarint(self):
        pass

    def test_float(self):
        pass

    def test_parse_decimal(self):
        row = '0DFB38D204D2'.decode("hex")
        v = read_int32_word(row, 4)
        assert 234567890 == v

        row = '0E04810DFB38D204D2'.decode("hex")
        v, s = RowsEvent.parse_decimal(row, 0, len(row))
        assert '1234567890.1234' == v
        assert len(row) == s

        row = '0E047EF204C72DFB2D'.decode("hex")
        v, s = RowsEvent.parse_decimal(row, 0, len(row))
        assert '-1234567890.1234' == v
        assert len(row) == s


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
