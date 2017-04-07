# -*- coding: utf-8 -*-

import logging
import os
import re
import struct
import time

from pytidbrep.crc32c import crc32c
from pytidbrep.event import DDLEvent
from pytidbrep.event import DeleteRowsEvent
from pytidbrep.event import UpdateRowsEvent
from pytidbrep.event import WriteRowsEvent
from pytidbrep.expcetion import CrcNotMatcheError
from pytidbrep.expcetion import EofError
from pytidbrep.expcetion import MagicNotMatchError
from pytidbrep.expcetion import UnexpectedEofError
from pytidbrep.expcetion import UnknownBinlogType
from pytidbrep.expcetion import UnknownDMLType
from pytidbrep.pb_binlog.binlog_pb2 import Binlog
from pytidbrep.pb_binlog.binlog_pb2 import DDL
from pytidbrep.pb_binlog.binlog_pb2 import DML
from pytidbrep.pb_binlog.binlog_pb2 import Delete
from pytidbrep.pb_binlog.binlog_pb2 import Insert
from pytidbrep.pb_binlog.binlog_pb2 import Update

LOG = logging.getLogger(__name__)


class BinLogStreamReader(object):
    # the file name format is like binlog-0000000000000001
    binlog_name_patten = r"binlog-[0-9]{16}"
    binlog_name_matcher = re.compile(binlog_name_patten)
    binlog_magic = 471532804

    def __init__(self,
                 binlog_dir,
                 binlog_start=None,
                 blocking=False,
                 skip_to_timestamp=None,
                 ignore_error = False):
        self._binlog_dir = binlog_dir
        self._current_binlog_file = None
        self._current_binlog_file_name = None
        self._skip_to_timestamp = skip_to_timestamp
        self._blocking = blocking
        self._ignore_error = ignore_error
        self._current_events = []

        if binlog_start:
            self._current_binlog_file = self._get_next_binlog_file(
                binlog_start)

    def read_fully(self, size):
        b = ''
        s = size

        while s > 0:
            if self._current_binlog_file:
                d = self._current_binlog_file.read(s)
            else:
                d = None

            if not d:
                next_file = self._get_next_binlog_file()

                if next_file:
                    if s == size:
                        LOG.info('Reading binlog "%s"' %
                                 self._current_binlog_file_name)
                        if self._current_binlog_file:
                            self._current_binlog_file.close()
                        self._current_binlog_file = next_file
                    else:
                        # binlog event will not cross file boundary
                        raise UnexpectedEofError(
                            'Unexpected end of binlog file "%s"' %
                            self._current_binlog_file_name)
                else:
                    if self._blocking:
                        time.sleep(1)
                    elif s == size:
                        raise EofError('End of binlog file "%s"' %
                                       self._current_binlog_file_name)
                    else:
                        raise UnexpectedEofError(
                            'Unexpected end of binlog file "%s"' %
                            self._current_binlog_file_name)

                continue

            s -= len(d)
            b += d

        return b

    def read_le_int32(self):
        b = self.read_fully(4)
        return struct.unpack("<i", b)[0]

    def read_le_uint32(self):
        b = self.read_fully(4)
        return struct.unpack("<I", b)[0]

    def read_le_int64(self):
        b = self.read_fully(8)
        return struct.unpack("<q", b)[0]

    def _get_next_binlog_file(self, start_file=None):
        if not os.path.exists(self._binlog_dir):
            raise RuntimeError(
                'binlog directory "%s" does not exist' % self._binlog_dir)

        binlogs = [
            f for f in os.listdir(self._binlog_dir)
            if os.path.isfile(os.path.join(self._binlog_dir, f)) and
            self.binlog_name_matcher.match(f)
        ]

        binlogs.sort()

        # with specified start position in directory
        if start_file:
            binlogs.index(start_file)
            self._current_binlog_file_name = start_file
            return open(
                os.path.join(self._binlog_dir, self._current_binlog_file_name),
                'rb')

        if not binlogs:
            return None

        # start with the first file in the directory
        if not self._current_binlog_file_name:
            self._current_binlog_file_name = binlogs[0]
            return open(
                os.path.join(self._binlog_dir, self._current_binlog_file_name),
                'rb')

        # next file in the directory
        index = binlogs.index(self._current_binlog_file_name)

        if index + 1 < len(binlogs):
            self._current_binlog_file = binlogs[index + 1]
            return open(
                os.path.join(self._binlog_dir, self._current_binlog_file_name),
                'rb')
        else:
            return None

    def _read_payload(self):
        try:
            magic = self.read_le_int32()
        except EofError:
            return None

        if magic != self.binlog_magic:
            raise MagicNotMatchError(
                '%s is not a valid binlog file: Magic not match')

        size = self.read_le_int64()
        payload = self.read_fully(size)
        crc = self.read_le_uint32()

        if crc != crc32c(payload):
            raise CrcNotMatcheError('CRC32 does not match in file "%s"' %
                                    self._current_binlog_file_name)

        return payload

    def _decode_DML(self, binlog):
        data = binlog.dml_data

        for event in data.events:
            if event.tp == Insert:
                self._current_events.append(WriteRowsEvent(binlog, event))
            elif event.tp == Update:
                self._current_events.append(UpdateRowsEvent(binlog, event))
            elif event.tp == Delete:
                self._current_events.append(DeleteRowsEvent(binlog, event))
            else:
                raise UnknownDMLType("Unknown DML type: %s" % event.tp)

    def fetchone(self):
        while True:
            if self._current_events:
                return self._current_events.pop(0)

            payload = self._read_payload()

            if not payload:
                raise StopIteration

            try:
                binlog = Binlog.FromString(payload)
    
                if self._skip_to_timestamp and \
                   binlog.commit_ts < self._skip_to_timestamp:
                    continue
    
                if binlog.tp == DML:
                    self._decode_DML(binlog)
                    continue
                elif binlog.tp == DDL:
                    return DDLEvent(binlog)
                else:
                    raise UnknownBinlogType('unknown binlog type %s' % binlog.tp)
            except Exception as e:
                if self._ignore_error:
                    LOG.warning('Ignore invalid binlog entry at ts: %s' % binlog.commit_ts)
                else:
                    raise

    def __iter__(self):
        return iter(self.fetchone, None)


if __name__ == "__main__":
    logging.basicConfig()
    stream = BinLogStreamReader(
        '/hashdata/mysql2pgsql/pytidbrep/data/data/drainer', skip_to_timestamp=390997282615197697,ignore_error=True)
    for event in stream:
        print event
