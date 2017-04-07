# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: binlog.proto

import sys
_b = sys.version_info[0] < 3 and (lambda x: x) or (
    lambda x: x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
    name='binlog.proto',
    package='pb_binlog',
    syntax='proto2',
    serialized_pb=
    _b('\n\x0c\x62inlog.proto\x12\tpb_binlog\"_\n\x05\x45vent\x12\x13\n\x0bschema_name\x18\x01 \x01(\t\x12\x12\n\ntable_name\x18\x02 \x01(\t\x12 \n\x02tp\x18\x03 \x01(\x0e\x32\x14.pb_binlog.EventType\x12\x0b\n\x03row\x18\x04 \x01(\x0c\"+\n\x07\x44MLData\x12 \n\x06\x65vents\x18\x01 \x03(\x0b\x32\x10.pb_binlog.Event\"w\n\x06\x42inlog\x12!\n\x02tp\x18\x01 \x01(\x0e\x32\x15.pb_binlog.BinlogType\x12\x11\n\tcommit_ts\x18\x02 \x01(\x03\x12$\n\x08\x64ml_data\x18\x03 \x01(\x0b\x32\x12.pb_binlog.DMLData\x12\x11\n\tddl_query\x18\x04 \x01(\x0c*/\n\tEventType\x12\n\n\x06Insert\x10\x00\x12\n\n\x06Update\x10\x01\x12\n\n\x06\x44\x65lete\x10\x02*\x1e\n\nBinlogType\x12\x07\n\x03\x44ML\x10\x00\x12\x07\n\x03\x44\x44L\x10\x01'
       ))
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_EVENTTYPE = _descriptor.EnumDescriptor(
    name='EventType',
    full_name='pb_binlog.EventType',
    filename=None,
    file=DESCRIPTOR,
    values=[
        _descriptor.EnumValueDescriptor(
            name='Insert', index=0, number=0, options=None, type=None),
        _descriptor.EnumValueDescriptor(
            name='Update', index=1, number=1, options=None, type=None),
        _descriptor.EnumValueDescriptor(
            name='Delete', index=2, number=2, options=None, type=None),
    ],
    containing_type=None,
    options=None,
    serialized_start=290,
    serialized_end=337, )
_sym_db.RegisterEnumDescriptor(_EVENTTYPE)

EventType = enum_type_wrapper.EnumTypeWrapper(_EVENTTYPE)
_BINLOGTYPE = _descriptor.EnumDescriptor(
    name='BinlogType',
    full_name='pb_binlog.BinlogType',
    filename=None,
    file=DESCRIPTOR,
    values=[
        _descriptor.EnumValueDescriptor(
            name='DML', index=0, number=0, options=None, type=None),
        _descriptor.EnumValueDescriptor(
            name='DDL', index=1, number=1, options=None, type=None),
    ],
    containing_type=None,
    options=None,
    serialized_start=339,
    serialized_end=369, )
_sym_db.RegisterEnumDescriptor(_BINLOGTYPE)

BinlogType = enum_type_wrapper.EnumTypeWrapper(_BINLOGTYPE)
Insert = 0
Update = 1
Delete = 2
DML = 0
DDL = 1

_EVENT = _descriptor.Descriptor(
    name='Event',
    full_name='pb_binlog.Event',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='schema_name',
            full_name='pb_binlog.Event.schema_name',
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
        _descriptor.FieldDescriptor(
            name='table_name',
            full_name='pb_binlog.Event.table_name',
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode('utf-8'),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
        _descriptor.FieldDescriptor(
            name='tp',
            full_name='pb_binlog.Event.tp',
            index=2,
            number=3,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
        _descriptor.FieldDescriptor(
            name='row',
            full_name='pb_binlog.Event.row',
            index=3,
            number=4,
            type=12,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b(""),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[],
    serialized_start=27,
    serialized_end=122, )

_DMLDATA = _descriptor.Descriptor(
    name='DMLData',
    full_name='pb_binlog.DMLData',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='events',
            full_name='pb_binlog.DMLData.events',
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[],
    serialized_start=124,
    serialized_end=167, )

_BINLOG = _descriptor.Descriptor(
    name='Binlog',
    full_name='pb_binlog.Binlog',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='tp',
            full_name='pb_binlog.Binlog.tp',
            index=0,
            number=1,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
        _descriptor.FieldDescriptor(
            name='commit_ts',
            full_name='pb_binlog.Binlog.commit_ts',
            index=1,
            number=2,
            type=3,
            cpp_type=2,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
        _descriptor.FieldDescriptor(
            name='dml_data',
            full_name='pb_binlog.Binlog.dml_data',
            index=2,
            number=3,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
        _descriptor.FieldDescriptor(
            name='ddl_query',
            full_name='pb_binlog.Binlog.ddl_query',
            index=3,
            number=4,
            type=12,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b(""),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            options=None),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[],
    serialized_start=169,
    serialized_end=288, )

_EVENT.fields_by_name['tp'].enum_type = _EVENTTYPE
_DMLDATA.fields_by_name['events'].message_type = _EVENT
_BINLOG.fields_by_name['tp'].enum_type = _BINLOGTYPE
_BINLOG.fields_by_name['dml_data'].message_type = _DMLDATA
DESCRIPTOR.message_types_by_name['Event'] = _EVENT
DESCRIPTOR.message_types_by_name['DMLData'] = _DMLDATA
DESCRIPTOR.message_types_by_name['Binlog'] = _BINLOG
DESCRIPTOR.enum_types_by_name['EventType'] = _EVENTTYPE
DESCRIPTOR.enum_types_by_name['BinlogType'] = _BINLOGTYPE

Event = _reflection.GeneratedProtocolMessageType(
    'Event',
    (_message.Message, ),
    dict(
        DESCRIPTOR=_EVENT,
        __module__='binlog_pb2'
        # @@protoc_insertion_point(class_scope:pb_binlog.Event)
    ))
_sym_db.RegisterMessage(Event)

DMLData = _reflection.GeneratedProtocolMessageType(
    'DMLData',
    (_message.Message, ),
    dict(
        DESCRIPTOR=_DMLDATA,
        __module__='binlog_pb2'
        # @@protoc_insertion_point(class_scope:pb_binlog.DMLData)
    ))
_sym_db.RegisterMessage(DMLData)

Binlog = _reflection.GeneratedProtocolMessageType(
    'Binlog',
    (_message.Message, ),
    dict(
        DESCRIPTOR=_BINLOG,
        __module__='binlog_pb2'
        # @@protoc_insertion_point(class_scope:pb_binlog.Binlog)
    ))
_sym_db.RegisterMessage(Binlog)

# @@protoc_insertion_point(module_scope)
