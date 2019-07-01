#
#    Copyright (c) 2019 Google LLC. All Rights Reserved.
#    Copyright (c) 2016-2018 Nest Labs Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

#
#    Description:
#      This file effects a parser for transforming protobuf-based
#      Weave Data Lanaguage (WDL) schema into an internal schema
#      format for further processing and manipulation.
#

"""Parser for turning nwv protobuf schema into Google Weave internal schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import itertools
import re
import inflection

from google.protobuf import any_pb2
from google.protobuf import duration_pb2
from google.protobuf import field_mask_pb2
from google.protobuf import timestamp_pb2
from wdl import data_access_pb2
from wdl import vendors_pb2
from wdl import wdl_options_pb2
from weave.common import command_response_status_pb2
from weave.common import identifiers_pb2
from weave.common import resource_type_pb2
from weave.common import string_ref_pb2
from weave.common import time_pb2
from weave.common import units_pb2
from google.protobuf import descriptor_pb2
from google.protobuf import text_encoding
from gwv import exception
from gwv import schema
from nwv import proto_pool
import logging

WRAPPER_TYPES = {
    '.google.protobuf.BoolValue':
        descriptor_pb2.FieldDescriptorProto.TYPE_BOOL,
    '.google.protobuf.BytesValue':
        descriptor_pb2.FieldDescriptorProto.TYPE_BYTES,
    '.google.protobuf.DoubleValue':
        descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE,
    '.google.protobuf.FloatValue':
        descriptor_pb2.FieldDescriptorProto.TYPE_FLOAT,
    '.google.protobuf.Int32Value':
        descriptor_pb2.FieldDescriptorProto.TYPE_INT32,
    '.google.protobuf.Int64Value':
        descriptor_pb2.FieldDescriptorProto.TYPE_INT64,
    '.google.protobuf.StringValue':
        descriptor_pb2.FieldDescriptorProto.TYPE_STRING,
    '.google.protobuf.UInt32Value':
        descriptor_pb2.FieldDescriptorProto.TYPE_UINT32,
    '.google.protobuf.UInt64Value':
        descriptor_pb2.FieldDescriptorProto.TYPE_UINT64,
}

_unique_number = itertools.count()


def _get_dependencies_in_namespace(msg_desc, namespace):
  """Return all message dependencies in the given namespace."""
  dependencies = []
  for key in msg_desc.message_dependencies:
    if key.startswith(namespace):
      dependencies.append(key)
  return dependencies


def _order_messages_by_dependency(messages, namespace):
  """Return messages with dependent messages returned after their dependencies.

  Args:
    messages: dict(str -> (descriptor, dependencies)), maps message full
        names to a tuple of their descriptor and local dependencies.
    namespace: str, prefix of messages to consider "local".

  Yields:
    Message descriptors with dependent messages after dependencies.
  """
  remaining_messages = collections.OrderedDict(
      (x.full_name, (x, _get_dependencies_in_namespace(x, namespace)))
      for x in messages)
  while remaining_messages:
    for nested_msg_desc, deps in remaining_messages.values():
      for dep in deps:
        if dep in remaining_messages:
          break
      else:
        del remaining_messages[nested_msg_desc.full_name]
        yield nested_msg_desc


class Parser(object):
  """Parses a protobuf descriptors and turns them into Google Weave Schema."""

  def __init__(self, schema_obj):
    self._schema_pool = collections.OrderedDict()

    self.schema_obj = schema_obj

  def link_file(self, file_obj):
    """Links and initializes a given schema file.

    Args:
      file_obj: Uninitialized file_obj object

    Raises:
      InvalidType:
    """

    if not isinstance(file_obj, schema.File):
      raise exception.InvalidType('Expecting a file')

    if not self.is_protobuf(file_obj.full_name):
      vendor = self.get_vendor(file_obj.full_name)
      if vendor != None:
          vendor.file_list.append(file_obj)

    for message_desc in file_obj.desc.message_type:
      full_name = '.'.join((file_obj.desc.package, message_desc.name))
      schema_obj = self.get_obj(full_name)
      if isinstance(schema_obj, schema.Trait):
        file_obj.trait_list.append(schema_obj)
      elif isinstance(schema_obj, schema.Typespace):
        file_obj.typespace_list.append(schema_obj)
      elif isinstance(schema_obj, schema.Interface):
        file_obj.interface_list.append(schema_obj)
      elif isinstance(schema_obj, schema.Resource):
        file_obj.resource_list.append(schema_obj)
      elif isinstance(schema_obj, schema.Struct):
        file_obj.struct_list.append(schema_obj)
      else:
        raise exception.InvalidType('Unexpected type in file: {}'.format(
            type(schema_obj)))

    for enum_desc in file_obj.desc.enum_type:
      full_name = '.'.join((file_obj.desc.package, enum_desc.name))
      schema_obj = self.get_obj(full_name)
      if isinstance(schema_obj, schema.Enum):
        file_obj.enum_list.append(schema_obj)
      else:
        raise exception.InvalidType('Unexpected type in file: {}'.format(
            type(schema_obj)))

  def link_field_constraints(self, field):
    """Parse field constraints and set data type.

    This method will fill in the data_type, metadata and constraints for a given
    field.

    Args:
      field: Uninitialized schema field constraints
    """

  def link_field(self, field):
    """Links a schema field object.

    Args:
        field: Unintialized schema field object
    """

    options = None
    if field.desc.options.HasExtension(wdl_options_pb2.prop):
      options = field.desc.options.Extensions[wdl_options_pb2.prop]
    elif field.desc.options.HasExtension(wdl_options_pb2.param):
      options = field.desc.options.Extensions[wdl_options_pb2.param]

    parent_writable = True
    if field.desc.parent.options.HasExtension(wdl_options_pb2.properties):
      props = field.desc.parent.options.Extensions[wdl_options_pb2.properties]
      if props.HasField('writable'):
        parent_writable = (
            wdl_options_pb2.WriteAccess.Name(props.writable) == 'READ_WRITE')

    field.objc_class_prefix = field.desc.file.options.objc_class_prefix
    field.java_outer_classname = field.desc.file.options.java_outer_classname
    field.source_file = field.desc.file.name
    field.is_oneof = field.desc.is_oneof()
    if options:
      field.is_nullable = options.nullable

    field.writable = parent_writable
    if field.desc.options.HasExtension(wdl_options_pb2.prop):
      props = field.desc.options.Extensions[wdl_options_pb2.prop]
      if options.HasField('writable'):
        field.writable = (
            wdl_options_pb2.WriteAccess.Name(props.writable) == 'READ_WRITE')
      field.is_optional = options.optional
      field.is_ephemeral = options.ephemeral

    if options is not None:
      if options.compatibility.HasField('min_version'):
        field.min_version = options.compatibility.min_version
      if options.compatibility.HasField('max_version'):
        field.max_version = options.compatibility.max_version

    field_desc = field.desc
    if field_desc.is_map():
      # Unwrap maps to value field
      field_desc = field.desc.message_type.fields['value']
      field.map_key = self.get_obj(
          field.desc.message_type.fields['key'].full_name)
      self.parse_options(field.map_key,
                         field.desc.options.Extensions[wdl_options_pb2.keyprop])
      field.map_value = self.get_obj(
          field.desc.message_type.fields['value'].full_name)
      self.parse_options(field.map_value, options)
      field.is_map = True
    else:
      field.is_array = field.desc.label == field_desc.LABEL_REPEATED

    field_type = field_desc.type
    if field_desc.type_name in WRAPPER_TYPES:
      field_type = WRAPPER_TYPES[field_desc.type_name]
      if not field.is_nullable and not self.is_common(field.full_name):
        # The fact that this was wrapped is lost,  so can't be checked in
        # separate validator
        raise exception.InvalidUsage(
            'Field %s is a wrapper type '
            'but is not nullable.' % field_desc.full_name)
    elif field.is_nullable and field_type != field_desc.TYPE_MESSAGE:
      raise exception.InvalidUsage('Field %s is nullable, but '
                                   'is not a wrapper or strudct '
                                   'type.' % field_desc.full_name)
    field.data_type = {
        field_desc.TYPE_FLOAT: schema.Field.DataType.FLOAT,
        field_desc.TYPE_DOUBLE: schema.Field.DataType.DOUBLE,
        field_desc.TYPE_UINT64: schema.Field.DataType.UINT64,
        field_desc.TYPE_UINT32: schema.Field.DataType.UINT32,
        field_desc.TYPE_INT64: schema.Field.DataType.INT64,
        field_desc.TYPE_INT32: schema.Field.DataType.INT32,
        field_desc.TYPE_FIXED64: schema.Field.DataType.INT64,
        field_desc.TYPE_FIXED32: schema.Field.DataType.INT32,
        field_desc.TYPE_SINT64: schema.Field.DataType.INT64,
        field_desc.TYPE_SINT32: schema.Field.DataType.INT32,
        field_desc.TYPE_STRING: schema.Field.DataType.STRING,
        field_desc.TYPE_ENUM: schema.Field.DataType.ENUM,
        field_desc.TYPE_BOOL: schema.Field.DataType.BOOL,
        field_desc.TYPE_BYTES: schema.Field.DataType.BYTES,
        field_desc.TYPE_MESSAGE: schema.Field.DataType.STRUCT,
    }[field_type]

    if field.data_type is schema.Field.DataType.STRUCT:
      field.struct_type = self.get_obj(field_desc.type_name)
      if not isinstance(field.struct_type, schema.Struct):
        raise exception.InvalidType(
            'Message {}, referenced by field {}, is not a struct. '
            'Fields may only reference structs.'.format(
                field.struct_type.full_name, field.full_name))
      # set metadata for legacy support
      field.metadata = field.struct_type
    elif field.data_type is schema.Field.DataType.ENUM:
      field.enum_type = self.get_obj(field_desc.type_name)
      # set metadata for legacy support
      field.metadata = field.enum_type

    self.parse_options(field, options)

  def parse_options(self, field, options):
    """Parses field constraint options."""

    encoding_val = field.desc.options.Extensions[wdl_options_pb2.tlv].encoding
    tlv_encoding_fixed = wdl_options_pb2.Encoding.Name(encoding_val) == 'FIXED'

    if not options:
      return

    if options.HasField('number_constraints'):
      if field.data_type not in (schema.Field.DataType.FLOAT,
                                 schema.Field.DataType.DOUBLE):
        raise exception.InvalidType(
            'Field %s in %s specifies number constraints, but number '
            'constraints are only valid for floats and doubles.' %
            (field.base_name, field.parent.full_name))
      constraint = options.number_constraints
      if constraint.HasField('min'):
        field.min_value = constraint.min
      if constraint.HasField('max'):
        field.max_value = constraint.max
      if constraint.HasField('precision'):
        field.precision = constraint.precision
      if constraint.HasField('fixed_encoding_width'):
        field.fixed_width = constraint.fixed_encoding_width
      field.is_signed = (field.min_value < 0)

      if not tlv_encoding_fixed:
        raise exception.InvalidType(
            'Field %s in %s has number constraints, but tlv fixed '
            'encoding is not set.' % (field.base_name, field.parent.full_name))
    elif tlv_encoding_fixed:
      raise exception.InvalidType(
          'Field %s in %s has tlv encoding set to fixed but no '
          'number constraints.' % (field.base_name, field.parent.full_name))

    if options.HasField('int_constraints'):
      if field.data_type not in (schema.Field.DataType.INT32,
                                 schema.Field.DataType.INT64):
        raise exception.InvalidType(
            'Field %s in %s specifies int constraints, but int '
            'constraints are only valid for int32 and int64.' %
            (field.base_name, field.parent.full_name))
      constraint = options.int_constraints
      if constraint.HasField('min'):
        field.min_value = constraint.min
      if constraint.HasField('max'):
        field.max_value = constraint.max
      if constraint.HasField('width'):
        field.fixed_width = constraint.width
      field.is_signed = True

    if options.HasField('uint_constraints'):
      if field.data_type not in (schema.Field.DataType.UINT32,
                                 schema.Field.DataType.UINT64):
        raise exception.InvalidType(
            'Field %s in %s specifies uint constraints, but uint '
            'constraints are only valid for uint32 and uint64.' %
            (field.base_name, field.parent.full_name))
      constraint = options.uint_constraints
      if constraint.HasField('min'):
        field.min_value = constraint.min
      if constraint.HasField('max'):
        field.max_value = constraint.max
      if constraint.HasField('width'):
        field.fixed_width = constraint.width
      field.is_signed = False

    if options.HasField('string_constraints'):
      if (field.data_type is not schema.Field.DataType.STRING and
          not field.desc.type_name.endswith('weave.common.StringRef')):
        raise exception.InvalidType(
            'Field %s in %s specifies string constraints, but string '
            'constraints are only valid for strings.' %
            (field.base_name, field.parent.full_name))
      constraint = options.string_constraints
      if constraint.HasField('min_length'):
        field.min_length = constraint.min_length
      if constraint.HasField('max_length'):
        field.max_length = constraint.max_length

    if options.HasField('bytes_constraints'):
      if field.data_type is not schema.Field.DataType.BYTES:
        raise exception.InvalidType(
            'Field %s in %s specifies bytes constraints, but bytes '
            'constraints are only valid for bytes.' % (field.base_name,
                                                       field.parent.full_name))
      constraint = options.bytes_constraints
      if constraint.HasField('min_length'):
        field.min_length = constraint.min_length
      if constraint.HasField('max_length'):
        field.max_length = constraint.max_length

    if options.HasField('timestamp_constraints'):
      if not field.desc.type_name.endswith('google.protobuf.Timestamp'):
        raise exception.InvalidType(
            'Field %s in %s specifies timestamp constraints, but '
            'timestamp constraints are only valid for timestamps.' %
            (field.base_name, field.parent.full_name))
      constraint = options.timestamp_constraints
      if constraint.HasField('signed'):
        field.is_signed = constraint.signed
      if constraint.HasField('precision'):
        field.precision = constraint.precision
      if constraint.HasField('width'):
        field.fixed_width = constraint.width

    if options.HasField('duration_constraints'):
      if not field.desc.type_name.endswith('google.protobuf.Duration'):
        raise exception.InvalidType(
            'Field %s in %s specifies duration constraints, but '
            'duration constraints are only valid for durations.' %
            (field.base_name, field.parent.full_name))
      constraint = options.duration_constraints
      if constraint.HasField('signed'):
        field.is_signed = constraint.signed
      if constraint.HasField('precision'):
        field.precision = constraint.precision
      if constraint.HasField('width'):
        field.fixed_width = constraint.width

    if options.HasField('resource_type'):
      if not field.desc.type_name.endswith('weave.common.ResourceId'):
        raise exception.InvalidType(
            'Field %s in %s specifies resource_type constraints, but '
            'resoruce type is only valid for resourceIds.' %
            (field.base_name, field.parent.full_name))

      field.resource_type = getattr(
          field.ResourceType,
          resource_type_pb2.ResourceType.Name(
              options.resource_type)[len('RESOURCE_TYPE_'):])

  def link_group(self, group):
    """Links a schema group object.

    Args:
      group: schema group object
    """

    group.interface = self.get_obj(group.desc.type_name)

    options = group.desc.options.Extensions[wdl_options_pb2.implconfig]

    parent_interface = self.get_obj(group.desc.parent.parent.full_name)

    for mapping in options.trait_mapping:
      from_component = parent_interface.component_list.by_name(
          getattr(mapping, 'from'))
      to_component = group.interface.component_list.by_name(mapping.to)
      if not from_component or not to_component:
        raise exception.InvalidUsage('Implements mapping for %s is invalid.' %
                                     parent_interface.full_name)
      ref = schema.GroupComponentRef(to_component.base_name,
                                     to_component.number, '')
      ref.source_component = from_component
      group.component_list.append(ref)

    if options.HasField('min_version'):
      group.min_version = options.min_version

  def link_typespace(self, typespace):
    """Links and initializes a given schema typespace.

    Args:
      typespace: Uninitialized typespace object

    Raises:
      InvalidType:
      MissingArgument:
    """

    if not isinstance(typespace, schema.Typespace):
      raise exception.InvalidType('Expecting an typespace')

    if typespace.desc.fields:
      raise exception.InvalidType(
          'Typespace {} contains properties, typespaces should not contain '
          'properties.'.format(typespace.full_name))

    options = typespace.desc.options.Extensions[wdl_options_pb2.typespace]

    vendor = self.get_vendor(typespace.desc.full_name)
    vendor.typespace_list.append(typespace)

    # Used to set the file descriptor in dev_*
    typespace.nwv_pb_desc = text_encoding.CEscape(
        typespace.desc.SerializeToString(), False)

    typespace.stability = schema.Stability(options.stability)
    typespace.version = options.version
    typespace.version_map = schema.VersionMap(options.version_map)

    for nested_msg_desc in _order_messages_by_dependency(
        typespace.desc.messages.values(), typespace.full_name):
      if nested_msg_desc.is_map_entry:
        continue  # ignore map entries
      nested_msg = self.get_obj(nested_msg_desc.full_name)
      if nested_msg:
        if isinstance(nested_msg, schema.Command):
          typespace.command_list.append(nested_msg)
        elif isinstance(nested_msg, schema.Event):
          typespace.event_list.append(nested_msg)
        elif isinstance(nested_msg, schema.Struct):
          typespace.struct_list.append(nested_msg)
        else:
          raise exception.InvalidType('Unexpected type in typespace')

    for nested_enum_desc in typespace.desc.enums.values():
      nested_enum = self.get_obj(nested_enum_desc.full_name)
      constant_type = nested_enum_desc.options.Extensions[
          wdl_options_pb2.enumopts].constant_type
      if constant_type:
        typespace.constant_group_list.append(nested_enum)
      else:
        typespace.enum_list.append(nested_enum)

  def get_extends(self, extends_name):
    extends = None
    if extends_name:
      extends = self.get_obj(extends_name)
      if not extends:
        raise exception.InvalidUsage('Cannot find extended object %s' %
                                     (extends_name))
    return extends

  def validate_extendable(self, options, fields, parent_fields_dict=None):
    """Checks that the fields extend the parent fields.

    Args:
      options: The descriptor options.
      fields: The fields to check.
      parent_fields_dict: the parent fields to check against.
    """

    if options.extendable:
      if (options.reserved_tag_min <= 0 or options.reserved_tag_max <= 1 or
          options.reserved_tag_max <= options.reserved_tag_min):
        raise exception.InvalidUsage('Extendable options are invalid')
      for field in fields:
        if (parent_fields_dict is not None and
            field.base_name in parent_fields_dict):
          continue  # Ignore fields that are in parent
        if (field.number > options.reserved_tag_max or
            field.number < options.reserved_tag_min):
          raise exception.InvalidUsage(
              'Field %s in %s number %d is outside reserved range. %d-%d' %
              (field.base_name, field.parent.full_name, field.number,
               options.reserved_tag_min, options.reserved_tag_max))

  def link_trait(self, trait):
    """Links a given trait and inserts it into the schema.

    Args:
      trait: An uninitialized schema trait object

    Raises:
      InvalidType:
      MissingArgument:
    """

    if not isinstance(trait, schema.Trait):
      raise exception.InvalidType('Expecting an trait')

    options = trait.desc.options.Extensions[wdl_options_pb2.trait]

    vendor = self.get_vendor(trait.desc.full_name)
    vendor.trait_list.append(trait)

    # Used to set the file descriptor in dev_*
    trait.nwv_pb_desc = text_encoding.CEscape(trait.desc.SerializeToString(),
                                              False)

    trait.stability = schema.Stability(options.stability)
    trait.version = options.version
    trait.version_map = schema.VersionMap(options.version_map)

    for field_desc in trait.desc.fields.values():
      trait.state_list.append(self.get_obj(field_desc.full_name))

    for nested_msg_desc in _order_messages_by_dependency(
        trait.desc.messages.values(), trait.full_name):
      if nested_msg_desc.is_map_entry:
        continue  # ignore map entries
      nested_msg = self.get_obj(nested_msg_desc.full_name)
      if isinstance(nested_msg, schema.Command):
        trait.command_list.append(nested_msg)
      elif isinstance(nested_msg, schema.Event):
        trait.event_list.append(nested_msg)
      elif isinstance(nested_msg, schema.CommandResponse):
        pass  # ignore, it will be handled inside link_command
      elif isinstance(nested_msg, schema.Struct):
        trait.struct_list.append(nested_msg)
      else:
        raise exception.InvalidType('Unexpected nested type in trait')

    for nested_enum_desc in trait.desc.enums.values():
      nested_enum = self.get_obj(nested_enum_desc.full_name)
      constant_type = nested_enum_desc.options.Extensions[
          wdl_options_pb2.enumopts].constant_type
      if constant_type:
        trait.constant_group_list.append(nested_enum)
      else:
        trait.enum_list.append(nested_enum)

    trait.extends = self.get_extends(
        trait.desc.options.Extensions[wdl_options_pb2.properties].extends.trait)

    self.validate_extendable(
        trait.desc.options.Extensions[wdl_options_pb2.properties],
        trait.state_list, trait.extends.desc.fields if trait.extends else {})

  def link_event(self, event):
    """Links the schema Event."""

    if not isinstance(event, schema.Event):
      raise exception.InvalidType('Expecting an event')

    options = event.desc.options.Extensions[wdl_options_pb2.event]

    for field_desc in event.desc.fields.values():
      event.field_list.append(self.get_obj(field_desc.full_name))

    if options.compatibility.HasField('min_version'):
      event.min_version = options.compatibility.min_version
    if options.compatibility.HasField('max_version'):
      event.max_version = options.compatibility.max_version

    event.extends = self.get_extends(options.extends)
    event.importance = event.Importance(options.event_importance)

  def link_command(self, command):
    """Links the schema Command."""

    if not isinstance(command, schema.Command):
      raise exception.InvalidType('Expecting a command')

    options = command.desc.options.Extensions[wdl_options_pb2.command]
    if options.completion_event:
      response_desc = command.desc.parent.messages[options.completion_event]
      if not response_desc:
        raise exception.InvalidType('Cannot find completion event %s in trait' %
                                    options.completion_event)
      response = self.get_obj(response_desc.full_name)
      if not isinstance(response, schema.CommandResponse):
        raise exception.InvalidType(
            'Completion event %s must be a ResponseEvent' %
            response_desc.full_name)
      command.response = response
      command.response.parent = command

    if options.compatibility.HasField('min_version'):
      command.min_version = options.compatibility.min_version
    if options.compatibility.HasField('max_version'):
      command.max_version = options.compatibility.max_version

    for field_desc in command.desc.fields.values():
      command.parameter_list.append(self.get_obj(field_desc.full_name))

    command.extends = self.get_extends(
        command.desc.options.Extensions[wdl_options_pb2.command].extends)

  def link_command_response(self, response):
    """Links the schema CommandResponse."""

    if not isinstance(response, schema.CommandResponse):
      raise exception.InvalidType('Expecting a CommandResponse')

    options = response.desc.options.Extensions[wdl_options_pb2.event]

    if options.compatibility.HasField('min_version'):
      response.min_version = options.compatibility.min_version
    if options.compatibility.HasField('max_version'):
      response.max_version = options.compatibility.max_version

    for field_desc in response.desc.fields.values():
      response.field_list.append(self.get_obj(field_desc.full_name))

  def link_constant_group(self, enum):
    """Links the schema ConstantGroup."""

    # NOTE: Throws ValueError if constant_type is invalid

    if not isinstance(enum, schema.ConstantGroup):
      raise exception.InvalidType('Expecting a constant group')

    constant_type = schema.Constant.Type(
        enum.desc.options.Extensions[wdl_options_pb2.enumopts].constant_type)

    constants = enum.constant_list

    for value in enum.desc.values.values():
      description = self.parse_comments(value)

      # For now, require exactly 1 value
      constant_value, = (
          value.options.Extensions[wdl_options_pb2.enumvalue]
          .constant_resource_id)

      constants.append(
          schema.Constant(value.full_name, value.number, description,
                          constant_type, constant_value))

  def link_enum(self, enum):
    """Parses the protobuf enum descriptor turns into a Google Weave Enum.

    Args:
      enum: A protobuf enum description to add to schema

    Raises:
      InvalidType: Encountered an invalid type while linking
      DuplicateObject: Duplicate enum value pair encountered
      InvalidUsage: Option used in an invalid way
    """

    options = enum.desc.options.Extensions[wdl_options_pb2.enumopts]
    enum_pairs = enum.pair_list

    if self.is_common(enum.full_name):
      self.link_common_enum(enum)
    elif (not enum.desc.parent or not isinstance(
        self.get_obj(enum.desc.parent.full_name),
        schema.StructEnumCollectionBase)):
      raise exception.InvalidType(
          ('Unexpected enum %s defined outside a typespace or trait' % enum))

    if options is not None:
      if options.compatibility.HasField('min_version'):
        enum.min_version = options.compatibility.min_version
      if options.compatibility.HasField('max_version'):
        enum.max_version = options.compatibility.max_version

    for value in enum.desc.values.values():
      description = self.parse_comments(value)
      pair_opts = value.options.Extensions[wdl_options_pb2.enumvalue]

      value.full_name.replace(
          inflection.underscore(enum.base_name).decode('utf-8').upper() + '_',
          '')

      enum_pair = schema.EnumPair(value.full_name, value.number, description)
      enum_pair.source_file = enum.source_file

      if pair_opts is not None:
        if pair_opts.compatibility.HasField('min_version'):
          enum_pair.min_version = pair_opts.compatibility.min_version
        if pair_opts.compatibility.HasField('max_version'):
          enum_pair.max_version = pair_opts.compatibility.max_version

      try:
        enum_pairs.append(enum_pair)
      except exception.DuplicateObject:
        pass

    enum.is_bitmask = options.bitmask

    if options.extends:
      raise exception.InvalidUsage('Extending enums is not yet supported.')

  def link_struct(self, struct):
    """Parse a protobuf message and turn it into a gwv schema struct.

    Args:
      struct: Protobuf message descriptor representing a struct

    Raises:
      InvalidType: Encountered an invalid type while linking
    """

    options = struct.desc.options.Extensions[wdl_options_pb2.structopts]

    if struct.desc.is_map_entry:
      # ignore map entries
      return

    if self.is_common(struct.full_name):
      self.link_common_struct(struct)
    elif (not struct.desc.parent or not isinstance(
        self.get_obj(struct.desc.parent.full_name),
        schema.StructEnumCollectionBase)):
      raise exception.InvalidType((
          'Unexpected struct %s defined outside a typespace or trait' % struct))

    for field_desc in struct.desc.fields.values():
      struct.field_list.append(self.get_obj(field_desc.full_name))

    struct.extends = self.get_extends(
        struct.desc.options.Extensions[wdl_options_pb2.structopts].extends)

    if options is not None:
      if options.compatibility.HasField('min_version'):
        struct.min_version = options.compatibility.min_version
      if options.compatibility.HasField('max_version'):
        struct.max_version = options.compatibility.max_version

  def link_interface_component(self, component):
    """Link and initialize an nwv interface component.

    Args:
      component: Uninitialized interface component objcet
    """

    component.trait = self.get_obj(component.desc.type_name)
    options = component.desc.options
    if options.HasExtension(wdl_options_pb2.traitiface):
      config_options = options.Extensions[wdl_options_pb2.traitiface]
      if config_options.HasField('min_version'):
        component.min_version = config_options.min_version

  def link_resource_component(self, component):
    """Link and initialize an nwv resource component.

    Args:
      component: Uninitialized component objcet
    """

    options = component.desc.options
    if options.HasExtension(wdl_options_pb2.traitinst):
      instance_id = options.Extensions[wdl_options_pb2.traitinst].instance
      component.instance_id = instance_id
    if not options.HasExtension(wdl_options_pb2.traitconfig):
      raise exception.InvalidUsage(
          'Trait config missing on {}. Every trait instance '
          'component must define trait config options.'.format(
              component.full_name))
    config_options = options.Extensions[wdl_options_pb2.traitconfig]
    component.published_by = schema.ResourceComponent.PublishedBy(
        config_options.published_by)
    if component.published_by == schema.ResourceComponent.PublishedBy.SELF:
      if not config_options.HasField('proxied'):
        raise exception.InvalidUsage(
            'Trait component {} is published by SELF but does not '
            'explicitly define proxied.'.format(component.full_name))
    elif (component.published_by ==
          schema.ResourceComponent.PublishedBy.EXTERNAL):
      if not config_options.HasField('subscribed'):
        raise exception.InvalidUsage(
            'Trait component {} is published by EXTERNAL but does '
            'not explicitly define subscribed.'.format(component.full_name))
    component.subscribed = config_options.subscribed
    component.proxied = config_options.proxied
    component.trait = self.get_obj(component.desc.type_name)

    if config_options.HasField('min_version'):
      component.min_version = config_options.min_version

    refinement_options = config_options.prop_refinement
    for refinement_option in refinement_options:
      prop_name = refinement_option.property
      prop = component.trait.state_list.by_name(prop_name)
      if not prop:
        raise exception.InvalidType('Property {} does not exist on trait {}'
                                    .format(prop_name, component.full_name))
      refinement = component.property_refinements[
          prop_name] = schema.FieldRefinement(prop)
      refinement.implemented = not refinement_option.unimplemented
      field_desc = refinement.field.desc
      field_type = WRAPPER_TYPES.get(field_desc.type_name, field_desc.type)
      if refinement_option.initial_bool_value:
        if field_type != field_desc.TYPE_BOOL:
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type, 'BOOL'))
        refinement.initial_value = refinement_option.initial_bool_value
      if refinement_option.initial_int_value:
        if field_type not in (field_desc.TYPE_INT32, field_desc.TYPE_INT64):
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type,
                  'INT32 or INT64'))
        refinement.initial_value = refinement_option.initial_int_value
      if refinement_option.initial_uint_value:
        if field_type not in (field_desc.TYPE_UINT32, field_desc.TYPE_UINT64):
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type,
                  'UINT32 or UINT64'))
        refinement.initial_value = refinement_option.initial_uint_value
      if refinement_option.initial_number_value:
        if field_type not in (field_desc.TYPE_FLOAT, field_desc.TYPE_DOUBLE):
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type,
                  'FLOAT or DOUBLE'))
        refinement.initial_value = refinement_option.initial_number_value
      if refinement_option.initial_string_value:
        if field_type != field_desc.TYPE_STRING:
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type, 'STRING'))
        refinement.initial_value = refinement_option.initial_string_value
      if refinement_option.initial_bytes_base16_value:
        if field_type != field_desc.TYPE_BYTES:
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type, 'BYTES'))
        value = refinement_option.initial_bytes_base16_value
        refinement.initial_bytes_base16_value = value
      if refinement_option.initial_resource_id_value:
        if field_desc.type_name != '.weave.common.ResourceId':
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.component,
                  'weave.common.ResourceId'))
        refinement.initial_value = refinement_option.initial_resource_id_value
      if refinement_option.initial_duration_value:
        if field_desc.type_name != '.google.protobuf.Duration':
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type_name,
                  'google.protobuf.Duration'))
        refinement.initial_value = [{
            'seconds': o.seconds,
            'nanos': o.nanos
        } for o in refinement_option.initial_duration_value]
      if refinement_option.initial_timestamp_value:
        if field_desc.type_name != '.google.protobuf.Timestamp':
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type_name,
                  'google.protobuf.Timestamp'))
        refinement.initial_value = [{
            'seconds': o.seconds,
            'nanos': o.nanos
        } for o in refinement_option.initial_timestamp_value]
      if refinement_option.initial_enum_value_name:
        if field_type != field_desc.TYPE_ENUM:
          raise exception.InvalidType(
              'Inital value for for {} on {} is type {}, expected {}'.format(
                  prop_name, component.full_name, field_desc.type_name, 'ENUM'))
        refinement.initial_value = refinement_option.initial_enum_value_name
      if refinement_option.initial_struct_value:
        raise exception.InvalidUsage(
            'Component {} defines an initial value; initial values for'
            ' structs is not implemented.'.format(component.full_name))

      # Every initial value option is an array
      # Flatten the array if the target property is not an array
      if (refinement.initial_value and
          field_desc.label != field_desc.LABEL_REPEATED):
        if len(refinement.initial_value) > 1:
          raise exception.InvalidType(
              'Array of initial values given for {}, which is not'
              ' an array'.format(component.full_name))
        refinement.initial_value = refinement.initial_value[0]

  def link_interface(self, interface):
    """Link and initialize an nwv object.

    Args:
      interface: Uninitialized interface objcet
    """

    vendor = self.get_vendor(interface.desc.full_name)
    vendor.interface_list.append(interface)

    interface.device_kind_name = interface.desc.name
    interface.device_kind_code = None

    options = interface.desc.options.Extensions[wdl_options_pb2.iface]
    interface.stability = schema.Stability(options.stability)
    if options.HasField('version'):
      interface.version = options.version

    interface.version_map = schema.VersionMap(options.version_map)

    for field_desc in interface.desc.fields.values():
      interface.component_list.append(self.get_obj(field_desc.full_name))

    for nested_msg_desc in interface.desc.messages.values():
      for implements_desc in nested_msg_desc.fields.values():
        interface.group_list.append(self.get_obj(implements_desc.full_name))

  def link_resource(self, resource):
    """Link and initialize an nwv object.

    Args:
      resource: Uninitialized resource objcet
    """

    vendor = self.get_vendor(resource.desc.full_name)
    vendor.resource_list.append(resource)

    resource.device_kind_name = resource.desc.name
    resource.device_kind_code = None

    options = resource.desc.options.Extensions[wdl_options_pb2.resource]
    resource.stability = schema.Stability(options.stability)
    if options.HasField('version'):
      resource.version = options.version

    resource.version_map = schema.VersionMap(options.version_map)

    for field_desc in resource.desc.fields.values():
      resource.component_list.append(self.get_obj(field_desc.full_name))

    for nested_msg_desc in resource.desc.messages.values():
      for implements_desc in nested_msg_desc.fields.values():
        resource.group_list.append(self.get_obj(implements_desc.full_name))

  def add_proto_to_pool(self, desc):
    """Adds proto descriptor to pool."""

    options = desc.options
    comments = self.parse_comments(desc)
    source_file = desc.file.name

    if isinstance(desc, proto_pool.MessageDesc):
      typ = wdl_options_pb2.MessageType.Name(
          desc.options.Extensions[wdl_options_pb2.message_type])
      if typ == 'IFACE_IMPLEMENTATIONS':
        return
      typ_cls = {
          'TRAIT': schema.Trait,
          'TYPESPACE': schema.Typespace,
          'RESOURCE': schema.Resource,
          'IFACE': schema.Interface,
          'RESPONSE_EVENT': schema.CommandResponse,
          'EVENT': schema.Event,
          'COMMAND': schema.Command,
          'STRUCT': schema.Struct,
          'UNION': schema.Struct,
          'TYPEDEF': schema.Struct
      }[typ]
      obj_id = {
          'TRAIT': options.Extensions[wdl_options_pb2.trait].id,
          'EVENT': options.Extensions[wdl_options_pb2.event].id,
          'COMMAND': options.Extensions[wdl_options_pb2.command].id
      }.get(typ, _unique_number.next())
    elif isinstance(desc, proto_pool.FieldDesc):
      parent_typ = wdl_options_pb2.MessageType.Name(
          desc.parent.options.Extensions[wdl_options_pb2.message_type])
      if parent_typ == 'IFACE_IMPLEMENTATIONS':
        typ_cls = schema.Group
      elif parent_typ == 'RESOURCE':
        typ_cls = schema.ResourceComponent
      elif parent_typ == 'IFACE':
        typ_cls = schema.InterfaceComponent
      else:
        typ_cls = schema.Field
      obj_id = desc.number
    elif isinstance(desc, proto_pool.EnumDesc):
      if options.Extensions[wdl_options_pb2.enumopts].constant_type:
        typ_cls = schema.ConstantGroup
      else:
        typ_cls = schema.Enum
      obj_id = _unique_number.next()
    elif isinstance(desc, proto_pool.FileDesc):
      typ_cls = schema.File
      obj_id = _unique_number.next()

    obj = typ_cls(desc.full_name, obj_id, comments)
    obj.desc = desc
    obj.objc_class_prefix = desc.file.options.objc_class_prefix
    obj.java_outer_classname = desc.file.options.java_outer_classname

    # This checks if the proto file has a valid objc_class_prefix defined.
    # Currently, this is just a WARNING but theoretically, without this,
    # the iOS code will have issues.
    if (isinstance(desc, proto_pool.FileDesc) and 
            not(self.is_common(desc.package + '.')) and (obj.objc_class_prefix == "")):
        logging.warn(desc.full_name + " is missing a valid obj_class_prefix!")

    obj.source_file = source_file
    self.add_obj(desc.full_name, obj)

  def proto_pool_to_schema_pool(self, proto_pool_obj):
    """Returns the schema pool for a proto pool."""

    for file_desc in proto_pool_obj.get_files():
      self.add_proto_to_pool(file_desc)

    for enum_desc in proto_pool_obj.get_enums():
      self.add_proto_to_pool(enum_desc)

    for msg_desc in proto_pool_obj.get_messages():
      self.add_proto_to_pool(msg_desc)

    for field_desc in proto_pool_obj.get_fields():
      self.add_proto_to_pool(field_desc)

    for name, number in vendors_pb2.Vendor.items():
      name = name.lower()
      self.add_obj(name, schema.Vendor(name, number, ''))

    # TODO(robbarnes) extract these packages from extension
    self.add_obj('wdl', self.get_obj('common'))
    self.add_obj('weave', self.get_obj('common'))
    self.add_obj('tahiti_df', self.get_obj('nest'))
    self.add_obj('light_demo', self.get_obj('nest'))

  def link_schema(self):
    """Links the schema."""

    for obj in self._schema_pool.values():
      link_methods = {
          schema.Command: self.link_command,
          schema.CommandResponse: self.link_command_response,
          schema.ConstantGroup: self.link_constant_group,
          schema.Enum: self.link_enum,
          schema.Event: self.link_event,
          schema.Event: self.link_event,
          schema.Field: self.link_field,
          schema.File: self.link_file,
          schema.Group: self.link_group,
          schema.Interface: self.link_interface,
          schema.InterfaceComponent: self.link_interface_component,
          schema.Resource: self.link_resource,
          schema.ResourceComponent: self.link_resource_component,
          schema.Struct: self.link_struct,
          schema.Trait: self.link_trait,
          schema.Typespace: self.link_typespace,
          schema.Vendor: self.link_vendor,
      }
      link_methods[type(obj)](obj)

      if not isinstance(obj, schema.Vendor):
        obj.file = self.get_obj(obj.desc.file.full_name)

  def add_file_set(self, file_set_generator):
    """Define trait and interface objects from a protobuf FileDescriptorSet."""

    proto_pool_obj = proto_pool.ProtoPool()
    proto_pool_obj.add_file_set(file_set_generator)

    files = [
        # wdl
        data_access_pb2,
        vendors_pb2,
        # weave common
        command_response_status_pb2,
        identifiers_pb2,
        resource_type_pb2,
        string_ref_pb2,
        time_pb2,
        units_pb2,
        # google protobuf
        any_pb2,
        duration_pb2,
        field_mask_pb2,
        timestamp_pb2,
    ]

    for file_obj in files:
      file_desc = descriptor_pb2.FileDescriptorProto()
      file_obj.DESCRIPTOR.CopyToProto(file_desc)
      proto_pool_obj.add_file(file_desc)

    self.proto_pool_to_schema_pool(proto_pool_obj)
    self.link_schema()

  def get_vendor(self, name):
    """Reruns the vendor with the given name."""
    if name.startswith('.'):
      name = name[1:]
    vendor_name = name.split('.')[0]
    return self._schema_pool.get(vendor_name)

  def link_vendor(self, vendor):
    """Links the schema vendor."""

    # Deduplicate because we have vendor aliases.
    if not self.schema_obj.vendor_list.by_name(vendor.base_name):
      self.schema_obj.vendor_list.append(vendor)

  def get_obj(self, full_name):
    """Reruns the schema object given the full name."""
    if full_name.startswith('.'):
      full_name = full_name[1:]
    return self._schema_pool.get(full_name)

  def add_obj(self, full_name, obj):
    """Adds the given object to pool."""

    if full_name.startswith('.'):
      full_name = full_name[1:]
    self._schema_pool[full_name] = obj

  def is_common(self, name):
    """Tests if the name starts with a common prefix."""
    common_type_prefixes = (
        'google.protobuf.',
        'wdl.',
        'datapol.',
        'weave.common.',
        'google.rpc.',
        'google.type.',
        'nest.messages.',
        'nestlabs.gateway.',
        'nestlabs.history.',
        'nestlabs.eventingapi.',
        'google.api.',
        'google.longrunning',
        'nest.services.',
    )
    return name.startswith(common_type_prefixes)

  def is_wdl(self, name):
    """Tests if the name starts with a wdl prefix."""
    prefixes = (
        'wdl.',
        'weave.common.',
    )
    return name.startswith(prefixes)

  def is_protobuf(self, name):
    """Tests if the name starts with a protobuf prefix."""
    prefixes = ('google.protobuf.',)
    return name.startswith(prefixes)

  def link_common_enum(self, enum):
    """Links the common enum."""
    if enum.full_name not in (
        'wdl.EventImportance',
        'weave.common.DayOfWeek',
        'weave.common.ResourceType',
    ):
      # ignore common enums not in this list
      return
    vendor = self.get_vendor(enum.full_name)
    vendor.enum_list.append(enum)

  def link_common_struct(self, struct):
    """Links the common struct."""
    if struct.full_name not in (
        'google.protobuf.Timestamp',
        'google.protobuf.Duration',
        'google.protobuf.FieldMask',
        'weave.common.ResourceId',
        'weave.common.ResourceName',
        'weave.common.TraitTypeId',
        'weave.common.TraitTypeInstance',
        'weave.common.InterfaceName',
        'weave.common.StringRef',
        'weave.common.TimeOfDay',
        'weave.common.Timer',
        'weave.common.EventId',
        'weave.common.ProfileSpecificStatusCode',
    ):
      # ignore common structs not in this list
      return
    vendor = self.get_vendor(struct.full_name)
    vendor.struct_list.append(struct)

  def parse_comments(self, desc):
    """Parse proto descriptor comments."""

    rv = []
    for line in desc.location.leading_comments.split('\n'):
      # Strip leading spaces and javadoc markers.
      line = re.sub(r'^[/\*]*', '', line)

      rv.append(line)

    if not rv:
      return None

    # If the last line is blank, remove it.
    if not rv[-1]:
      rv.pop()

    if not rv:
      return None

    # If the first line is blank, remove it.
    if not rv[0]:
      rv.pop(0)

    if not rv:
      return None

    return rv
