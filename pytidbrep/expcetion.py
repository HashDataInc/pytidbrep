# -*- coding: utf-8 -*-


class ReplicationError(Exception):
    pass


class EofError(ReplicationError):
    pass


class UnexpectedEofError(ReplicationError):
    pass


class MagicNotMatchError(ReplicationError):
    pass


class CrcNotMatcheError(ReplicationError):
    pass


class UnknownBinlogType(ReplicationError):
    pass


class UnknownDMLType(ReplicationError):
    pass


class InvalidRowData(ReplicationError):
    pass
