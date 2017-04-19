# -*- coding: utf-8 -*-

# Copyright (c) 2016 HashData Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from __future__ import unicode_literals

from datetime import timedelta
import struct

from pytidbrep.expcetion import InvalidRowData
from pytidbrep.pb_binlog.binlog_pb2 import DDL
from pytidbrep.pb_binlog.binlog_pb2 import DML
from pytidbrep.pb_binlog.binlog_pb2 import Delete
from pytidbrep.pb_binlog.binlog_pb2 import Insert
from pytidbrep.pb_binlog.binlog_pb2 import Update
from pytidbrep.pb_binlog.binlog_pb2 import column

SIGNMASK = 0x8000000000000000

DIGITS_PER_WORD = 9  # A word holds 9 digits.
WORD_SIZE = 4  # A word is 4 bytes int32.
DIG2BYTES = [0, 1, 1, 2, 2, 3, 3, 4, 4, 4]

TYPE_BIT = 16
TYPE_TINY = 1
TYPE_SHORT = 2
TYPE_INT24 = 9
TYPE_LONG = 3
TYPE_LONGLONG = 8
TYPE_FLOAT = 4
TYPE_DOUBLE = 5
TYPE_DECIMAL = 0
TYPE_NEWDECIMAL = 0xf6

TYPE_DATE = 10
TYPE_NEWDATE = 14
TYPE_DATETIME = 12
TYPE_TIMESTAMP = 7
TYPE_YEAR = 13
TYPE_DURATION = 11

TYPE_VARCHAR = 15
TYPE_VARSTRING = 0xfd
TYPE_STRING = 0xfe
TYPE_TINYBLOB = 0xf9
TYPE_BLOB = 0xfc
TYPE_MEDIUMBLOB = 0xfa
TYPE_LONGBLOB = 0xfb
TYPE_ENUM = 0xf7
TYPE_SET = 0xf8

TYPE_NULL = 6
TYPE_GEOMETRY = 0xff

MYSQL_TYPE_BIT_STR = "bit"
MYSQL_TYPE_TINYINT = "tinyint"
MYSQL_TYPE_SMALLINT = "smallint"
MYSQL_TYPE_MEDIUMINT = "mediumint"
MYSQL_TYPE_INT = "int"
MYSQL_TYPE_BIGINT = "bigint"
MYSQL_TYPE_DECIMAL = "decimal"
MYSQL_TYPE_FLOAT = "float"
MYSQL_TYPE_DOUBLE = "double"

MYSQL_TYPE_DATE = "date"
MYSQL_TYPE_DATETIME = "datetime"
MYSQL_TYPE_TIMESTAMP = "timestamp"
MYSQL_TYPE_TIME = "time"
MYSQL_TYPE_YEAR = "year"

MYSQL_TYPE_CHAR = "char"
MYSQL_TYPE_VARCHAR = "varchar"
MYSQL_TYPE_BINARY = "binary"
MYSQL_TYPE_VARBINARY = "varbinary"
MYSQL_TYPE_TINYBLOB = "tinyblob"
MYSQL_TYPE_TINYTEXT = "tinytext"
MYSQL_TYPE_BLOB = "blob"
MYSQL_TYPE_TEXT = "text"
MYSQL_TYPE_MEDIUMBLOB = "mediumblob"
MYSQL_TYPE_MEDIUMTEXT = "mediumtext"
MYSQL_TYPE_LONGBLOB = "longblob"
MYSQL_TYPE_LONGTEXT = "longtext"
MYSQL_TYPE_ENUM = "enum"

MYSQL_TYPE_GEOMETRY = "geometry"
MYSQL_TYPE_NULL = "null"
MYSQL_TYPE_VARSTRING = "var_string"
MYSQL_TYPE_UNSPECIFIED = "unspecified"


def get_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return s.decode('utf8')


def format_column(t, v):
    _, mysql_type = t

    if v is None:
        return "NULL"
    elif mysql_type in (MYSQL_TYPE_TINYTEXT, MYSQL_TYPE_MEDIUMTEXT,
                        MYSQL_TYPE_LONGTEXT, MYSQL_TYPE_TEXT, MYSQL_TYPE_CHAR,
                        MYSQL_TYPE_VARCHAR):
        return '"%s"' % get_unicode(v)
    elif mysql_type in (MYSQL_TYPE_BINARY, MYSQL_TYPE_VARBINARY,
                        MYSQL_TYPE_TINYBLOB, MYSQL_TYPE_MEDIUMBLOB,
                        MYSQL_TYPE_LONGBLOB, MYSQL_TYPE_BLOB):
        return '"%s"' % v.encode('hex')
    elif mysql_type in (MYSQL_TYPE_DATE, MYSQL_TYPE_DATETIME,
                        MYSQL_TYPE_TIMESTAMP, MYSQL_TYPE_TIME,
                        MYSQL_TYPE_YEAR):
        return '"%s"' % str(v)
    else:
        return str(v)


def int2byte(i):
    return struct.pack(b"!B", i)


def read_be_uint64(buf):
    return struct.unpack(b">Q", buf)[0]


def read_int8(buf):
    return struct.unpack(b">b", buf)[0]


def read_uint8(buf):
    return struct.unpack(b">B", buf)[0]


def read_uvarint(buf):
    '''
     read_uvarint decodes a uint64 from buf and returns that value and the
     number of bytes read (> 0). If an error occurred, the value is 0
     and the number of bytes n is <= 0 meaning:

        n == 0: buf too small
        n  < 0: value larger than 64 bits (overflow)
                  and -n is the number of bytes read
    '''

    x = 0
    s = 0

    for i in range(len(buf)):
        b = read_uint8(buf[i])

        if b < 0x80:
            if i > 9 or i == 9 and b > 1:
                return 0, -(i + 1)  # overflow

            return x | (b << s), i + 1

        x |= (b & 0x7f) << s
        s += 7

    return 0, 0


def read_varint(buf):
    '''
     read_varint decodes an int64 from buf and returns that value and the
     number of bytes read (> 0). If an error occurred, the value is 0
     and the number of bytes n is <= 0 with the following meaning:

        n == 0: buf too small
        n  < 0: value larger than 64 bits (overflow)
                  and -n is the number of bytes read
    '''

    ux, n = read_uvarint(buf)  # ok to continue in presence of error

    x = ux >> 1

    if ux & 1 != 0:
        x = ~x

    return x, n


def read_int32_word(buf, size):
    if read_int8(buf[0]) & 0x80 > 0:
        pad = 0xFF
    else:
        pad = 0

    tmp = bytearray(WORD_SIZE)

    for i in range(WORD_SIZE - size):
        tmp[i] = pad

    offset = WORD_SIZE - size
    for i in range(offset, WORD_SIZE):
        tmp[i] = buf[i - offset]

    x = struct.unpack(b">i", str(tmp))[0]

    return x


def decimal_bin_size(precision, frac):
    digits_int = precision - frac
    words_int = digits_int / DIGITS_PER_WORD
    words_frac = frac / DIGITS_PER_WORD
    xint = digits_int - words_int * DIGITS_PER_WORD
    xfrac = frac - words_frac * DIGITS_PER_WORD
    return words_int * WORD_SIZE + DIG2BYTES[xint] + \
        words_frac * WORD_SIZE + DIG2BYTES[xfrac]


class BinLogEvent(object):
    def __init__(self, binlog):
        self.tp = binlog.tp
        self.commit_ts = binlog.commit_ts

    @classmethod
    def type_name(cls, tp):
        if tp == DML:
            return "DML"
        elif tp == DDL:
            return "DDL"
        else:
            return "Unknown"

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "%s: %s" % (self.commit_ts, self.type_name(self.tp))


class DDLEvent(BinLogEvent):
    def __init__(self, binlog):
        super(DDLEvent, self).__init__(binlog)
        self._statement = get_unicode(binlog.ddl_query)

    @property
    def statement(self):
        '''Return DDL statement

        @return: A unicode string of DDL statement
        '''
        return self._statement

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "%s: %s" % (super(DDLEvent, self).__unicode__(), self.statement)


class XidEvent(BinLogEvent):
    """A COMMIT event
    """

    def __init__(self, ts):
        self.commit_ts = ts

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "Transaction at: %s" % (self.commit_ts)


class RowsEvent(BinLogEvent):
    NIL_FLAG = 0
    BYTES_FLAG = 1
    COMPACTBYTES_FLAG = 2
    INT_FLAG = 3
    UINT_FLAG = 4
    FLOAT_FLAG = 5
    DECIMAL_FLAG = 6
    DURATION_FLAG = 7
    VARINT_FLAG = 8
    UVARINT_FLAG = 9
    MAX_FLAG = 250

    def __init__(self, binlog, event):
        super(RowsEvent, self).__init__(binlog)
        self._schema = get_unicode(event.schema_name)
        self._table = get_unicode(event.table_name)
        self._dml_tp = event.tp

    @property
    def schema(self):
        '''Return table's schema name of the event

        @return: A unicode string of schema
        '''
        return self._schema

    @property
    def table(self):
        '''Return table's name of the event

        @return: A unicode string of table name
        '''
        return self._table

    @classmethod
    def dml_type_name(cls, tp):
        if tp == Insert:
            return "INSERT"
        elif tp == Update:
            return "UPDATE"
        elif tp == Delete:
            return "DELETE"
        else:
            return "UNKNOWN"

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        parent = super(RowsEvent, self).__unicode__()
        return "%s: %s %s.%s" % (parent, self.dml_type_name(self._dml_tp),
                                 self.schema, self.table)

    @classmethod
    def parse_int(cls, row, pos, size):
        if size - pos < 8:
            raise InvalidRowData('insufficient bytes to decode value')

        u = read_be_uint64(row[pos:pos + 8])
        v = SIGNMASK ^ u
        return v, 8

    @classmethod
    def parse_uint(cls, row, pos, size):
        if size - pos < 8:
            raise InvalidRowData('insufficient bytes to decode value')

        v = read_be_uint64(row[pos:pos + 8])
        return v, 8

    @classmethod
    def parse_varint(cls, row, pos, size):
        v, n = read_varint(row[pos:pos + 10])  # needs at most 10 bytes
        if n > 0:
            return v, n

        if n < 0:
            raise InvalidRowData("value larger than 64 bits")

        raise InvalidRowData("insufficient bytes to decode value")

    @classmethod
    def parse_uvarint(cls, row, pos, size):
        v, n = read_uvarint(row[pos:pos + 10])  # needs at most 10 bytes
        if n > 0:
            return v, n

        if n < 0:
            raise InvalidRowData("value larger than 64 bits")

        raise InvalidRowData("insufficient bytes to decode value")

    @classmethod
    def parse_float(cls, row, pos, size):
        if size - pos < 8:
            raise InvalidRowData('insufficient bytes to decode value')

        tmp = bytearray(row[pos:pos + 8])
        if tmp[0] & 0x80 > 0:
            tmp[0] &= 0x7F
        else:
            u = struct.unpack(b">Q", str(tmp))[0]
            u = ~u
            tmp = struct.pack(b">q", u)

        v = struct.unpack(b">d", str(tmp))[0]
        return v, 8

    @classmethod
    def parse_bytes(cls, row, pos, size):
        ENC_GROUP_SIZE = 8
        ENC_MARKER = 0xFF
        ENC_PAD = 0x0

        old_pos = pos

        retval = ""
        while True:
            if size - pos < ENC_GROUP_SIZE + 1:
                raise InvalidRowData("insufficient bytes to decode value")

            group = row[pos:pos + ENC_GROUP_SIZE]
            marker = row[pos + ENC_GROUP_SIZE]

            pad_count = ENC_MARKER - marker

            if pad_count > ENC_GROUP_SIZE:
                raise InvalidRowData("invalid marker byte")

            real_roup_size = ENC_GROUP_SIZE - pad_count
            retval += group[:real_roup_size]
            pos += ENC_GROUP_SIZE + 1

            if pad_count != 0:
                pad_byte = ENC_PAD

                for v in group[real_roup_size:]:
                    if v != pad_byte:
                        raise InvalidRowData("invalid padding byte")

                break

        return retval, pos - old_pos

    @classmethod
    def parse_compact_bytes(cls, row, pos, size):
        n, s = cls.parse_varint(row, pos, size)
        if size - pos - s < n:
            raise InvalidRowData(
                "insufficient bytes to decode value, expected length: %s", n)

        return row[pos + s:pos + s + n], s + n

    @classmethod
    def parse_decimal(cls, row, pos, size):
        if size - pos < 3:
            raise InvalidRowData('insufficient bytes to decode value')

        precision = read_int8(row[pos])
        frac = read_int8(row[pos + 1])

        bin_size = decimal_bin_size(precision, frac)

        if size - pos < bin_size + 2:
            raise InvalidRowData("insufficient bytes to decode value")

        bin = row[pos + 2:pos + 2 + bin_size]
        bin_pos = 0

        if read_int8(bin[bin_pos]) & 0x80 > 0:
            negitive = False
            retval = ''
        else:
            negitive = True
            retval = '-'

        bin = bytearray(bin)
        bin[0] ^= 0x80
        bin = str(bin)

        # The number of *decimal* digits before the point.
        digits_int = precision - frac
        # The number of 32bit words before the point.
        words_int = digits_int / DIGITS_PER_WORD
        # The number of leading *decimal* digits not in a word
        leading_digits = digits_int - words_int * DIGITS_PER_WORD

        # The number of 32bit words after the point.
        words_frac = frac / DIGITS_PER_WORD
        # The number of trailing *decimal* digits not in a word
        trailing_digits = frac - words_frac * DIGITS_PER_WORD

        if leading_digits > 0:
            i = DIG2BYTES[leading_digits]
            x = read_int32_word(bin[bin_pos:], i)
            x = ~x if negitive else x
            retval += str(x)
            bin_pos += i

        for i in range(0, words_int * WORD_SIZE, WORD_SIZE):
            x = read_int32_word(bin[bin_pos + i:], WORD_SIZE)
            x = ~x if negitive else x
            retval += str(x)

        bin_pos += words_int * WORD_SIZE

        retval += '.'

        for i in range(0, words_frac * WORD_SIZE, WORD_SIZE):
            x = read_int32_word(bin[bin_pos + i:], WORD_SIZE)
            x = ~x if negitive else x
            retval += str(x)

        bin_pos += words_frac * WORD_SIZE

        if trailing_digits > 0:
            i = DIG2BYTES[trailing_digits]
            x = read_int32_word(bin[bin_pos:], i)
            x = ~x if negitive else x
            retval += str(x)

        return retval, bin_size + 2

    @classmethod
    def parse_duration(cls, row, pos, size):
        v, s = cls.parse_int(row, pos, size)
        d = timedelta(microseconds=v / 1000)

        return d, s

    @classmethod
    def parse_one_column(cls, value):
        pos = 0
        size = len(value)

        if size - pos < 1:
            raise InvalidRowData("Invalid encoded key")

        flag = read_int8(value[pos])
        pos += 1

        if cls.INT_FLAG == flag:
            v, _ = cls.parse_int(value, pos, size)
        elif cls.UINT_FLAG == flag:
            v, _ = cls.parse_uint(value, pos, size)
        elif cls.VARINT_FLAG == flag:
            v, _ = cls.parse_varint(value, pos, size)
        elif cls.UVARINT_FLAG == flag:
            v, _ = cls.parse_uvarint(value, pos, size)
        elif cls.FLOAT_FLAG == flag:
            v, _ = cls.parse_float(value, pos, size)
        elif cls.BYTES_FLAG == flag:
            v, _ = cls.parse_bytes(value, pos, size)
        elif cls.COMPACTBYTES_FLAG == flag:
            v, _ = cls.parse_compact_bytes(value, pos, size)
        elif cls.DECIMAL_FLAG == flag:
            v, _ = cls.parse_decimal(value, pos, size)
        elif cls.DURATION_FLAG == flag:
            v, _ = cls.parse_duration(value, pos, size)
        elif cls.NIL_FLAG == flag:
            v = None
        else:
            raise InvalidRowData("Invalid encoded key")

        return v

    @classmethod
    def parse_insert_and_delete_row(cls, row):
        values = {}
        types = {}

        for c in row:
            col = column.FromString(c)
            tp = read_uint8(col.tp)
            mysql_type = col.mysql_type
            name = get_unicode(col.name)

            value = cls.parse_one_column(col.value)

            if value is not None and \
                    mysql_type in (
                        MYSQL_TYPE_TINYTEXT,
                        MYSQL_TYPE_MEDIUMTEXT,
                        MYSQL_TYPE_LONGTEXT,
                        MYSQL_TYPE_TEXT,
                        MYSQL_TYPE_CHAR,
                        MYSQL_TYPE_VARCHAR
                    ):
                value = value.decode('utf-8')

            values[name] = value
            types[name] = (tp, mysql_type)

        return types, values

    @classmethod
    def parse_update_row(cls, row):
        old_values = {}
        new_values = {}
        types = {}

        for c in row:
            col = column.FromString(c)
            tp = read_uint8(col.tp)
            mysql_type = col.mysql_type
            name = unicode(col.name)

            value = cls.parse_one_column(col.value)
            changed_value = cls.parse_one_column(col.changed_value)

            old_values[name] = value
            new_values[name] = changed_value
            types[name] = (tp, mysql_type)

        return types, old_values, new_values


class DeleteRowsEvent(RowsEvent):
    """This event is trigger when a row in the database is removed

    For each row you have a hash with a single key:
    values which contain the data of the removed line.
    """

    def __init__(self, binlog, event):
        super(DeleteRowsEvent, self).__init__(binlog, event)
        self._types, self._values = self.parse_insert_and_delete_row(event.row)

    @property
    def types(self):
        return self._types

    @property
    def values(self):
        return self._values

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        parent = super(DeleteRowsEvent, self).__unicode__()
        values = self.values
        types = self.types

        s = ''
        for col in values:
            s += "%s %s, " % (col, format_column(types[col], values[col]))

        return "%s: %s" % (parent, s)


class WriteRowsEvent(RowsEvent):
    """This event is triggered when a row in database is added

    For each row you have a hash with a single key:
    values which contain the data of the new line.
    """

    def __init__(self, binlog, event):
        super(WriteRowsEvent, self).__init__(binlog, event)
        self._types, self._values = self.parse_insert_and_delete_row(event.row)

    @property
    def types(self):
        return self._types

    @property
    def values(self):
        return self._values

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        parent = super(WriteRowsEvent, self).__unicode__()
        values = self.values
        types = self.types

        s = ''
        for col in values:
            s += "%s %s, " % (col, format_column(types[col], values[col]))

        return "%s: %s" % (parent, s)


class UpdateRowsEvent(RowsEvent):
    """This event is triggered when a row in the database is changed

    For each row you got a hash with two keys:
        * before_values
        * after_values
    """

    def __init__(self, binlog, event):
        super(UpdateRowsEvent, self).__init__(binlog, event)
        self._types, self._before_values, self._after_values = \
            self.parse_update_row(event.row)

    @property
    def types(self):
        return self._types

    @property
    def before_values(self):
        return self._before_values

    @property
    def after_values(self):
        return self._after_values

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        parent = super(UpdateRowsEvent, self).__unicode__()
        before_values = self.before_values
        after_values = self.after_values
        types = self.types

        s = ''
        for col in before_values:
            s += "%s %s => %s, " % (
                col, format_column(types[col], before_values[col]),
                format_column(types[col], after_values[col]))

        return "%s: %s" % (parent, s)
