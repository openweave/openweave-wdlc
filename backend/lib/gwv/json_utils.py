#
#    Copyright (c) 2019-2020 Google LLC. All Rights Reserved.
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
#      This file implements utilities for JSON representation handling
#      and output generation from Weave Data Language (WDL) schema.
#

"""Utilities to export a schema to JSON."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math

from gwv import schema
import six


class JsonFormat(object):
  """Enumeration of supported JSON formats."""

  # JSON format used internally to drive the Google Weave Service validation
  # logic.
  SERVER_VALIDATION = 1

  # JSON sent from a device to the Google Weave Service as part of the device
  # resource.
  DEVICE_RESOURCE = 2


def description_as_json(description):
  """Return a json representation of the given description string.

  Args:
    description: The description.

  Returns:
    A JSON appropriate representation.
  """

  return description.split('\n') if description else []


def enum_as_json(enum, json_format):
  """Return a json representation of the given enum.

  Args:
    enum: The enum.
    json_format: A value from the JsonFormat class.

  Returns:
    A JSON appropriate representation.
  """

  rv = collections.OrderedDict()

  if json_format == JsonFormat.SERVER_VALIDATION and enum.description:
    rv['@description'] = description_as_json(enum.description)

  rv['type'] = 'string'
  rv['enum'] = []
  for enum_pair in enum.pair_list:
    if not enum_pair.number:
      continue

    rv['enum'].append(enum_pair.camel_name)

  if json_format == JsonFormat.SERVER_VALIDATION:
    rv['@enumDescriptions'] = collections.OrderedDict()
    for enum_pair in enum.pair_list:
      if not enum_pair.number:
        continue

      rv['@enumDescriptions'][enum_pair.camel_name] = description_as_json(
          enum_pair.description)

  return rv


def struct_as_json(struct, json_format):
  """Return a json representation of the given struct.

  Args:
    struct: The struct.
    json_format: A value from the JsonFormat class.

  Returns:
    A JSON appropriate representation.
  """

  rv = collections.OrderedDict()

  if json_format == JsonFormat.SERVER_VALIDATION and struct.description:
    rv['@description'] = description_as_json(struct.description)

  rv['type'] = 'object'
  rv['additionalProperties'] = False
  rv['properties'] = fields_as_json(struct.field_list, json_format)

  required_list = []
  for (name, d) in six.iteritems(rv['properties']):
    if 'isRequired' in d:
      if d['isRequired']:
        required_list.append(name)
      del d['isRequired']

  if required_list:
    rv['required'] = sorted(required_list)

  return rv


def fields_as_json(field_list, json_format):
  """Return an OrderedDict() that describes a list of fields in a JSON format.

  Args:
    field_list: The list of fields to represent.
    json_format: A value from the JsonFormat class.

  Returns:
    A JSON appropriate representation.

  Raises:
    Exception: Something unexpected was found in the field list.
  """

  rv = collections.OrderedDict()

  for field in field_list:
    field_json = collections.OrderedDict()

    if json_format == JsonFormat.SERVER_VALIDATION and field.description:
      field_json['@description'] = description_as_json(field.description)

    if (field.data_type == schema.Field.DataType.FLOAT or
        field.data_type == schema.Field.DataType.DOUBLE):
      field_json['type'] = 'number'
      if field.metadata.max_value is not None:
        field_json['maximum'] = field.metadata.max_value
      if field.metadata.min_value is not None:
        field_json['minimum'] = field.metadata.min_value

    elif (field.data_type == schema.Field.DataType.INT64 or
          field.data_type == schema.Field.DataType.UINT64 or
          field.data_type == schema.Field.DataType.UINT32 or
          field.data_type == schema.Field.DataType.INT32):
      field_json['type'] = 'integer'
      if field.metadata.max_value is not None:
        field_json['maximum'] = field.metadata.max_value
      if field.metadata.min_value is not None:
        field_json['minimum'] = field.metadata.min_value

    elif field.data_type == schema.Field.DataType.BOOL:
      field_json['type'] = 'boolean'

    elif (field.data_type == schema.Field.DataType.STRING or
          field.data_type == schema.Field.DataType.BYTES):
      field_json['type'] = 'string'
      if field.metadata.max_bytes is not None:
        field_json['maxLength'] = field.metadata.max_bytes

    elif field.data_type == schema.Field.DataType.BYTES:
      field_json['type'] = 'string'
      if field.metadata.max_bytes is not None:
        # Since bytes must be encoded as base64, calculate max base64 size
        field_json['maxLength'] = 4 * math.ceil(
            float(field.metadata.max_bytes) / 3)

    elif field.data_type == schema.Field.DataType.ENUM:
      if json_format == JsonFormat.SERVER_VALIDATION:
        field_json['@ref'] = '#/@definitions/%s' % field.metadata.name
      else:
        field_json = enum_as_json(field.metadata, json_format)

    elif field.data_type == schema.Field.DataType.STRUCT:
      if field.is_array:
        field_json['type'] = 'array'
        if json_format == JsonFormat.SERVER_VALIDATION:
          field_json['items'] = {
              '@ref': '#/@definitions/%s' % field.metadata.name
          }
        else:
          field_json['items'] = struct_as_json(field.metadata, json_format)
      else:
        if json_format == JsonFormat.SERVER_VALIDATION:
          field_json['@ref'] = '#/@definitions/%s' % field.metadata.name
        else:
          field_json = struct_as_json(field.metadata, json_format)

    else:
      raise Exception('Unexpected field type: %s' % field.data_type)

    if field.is_optional:
      field_json['isOptional'] = field.is_optional

    rv[field.camel_name] = field_json

  return rv


def command_as_json(command, json_format):
  """Return an OrderedDict() that describes a command in a JSON format.

  Args:
    command: The command to represent.
    json_format: A value from the JsonFormat class.

  Returns:
    A JSON appropriate representation.
  """

  rv = collections.OrderedDict()

  trait = command.parent_list.parent

  if json_format == JsonFormat.SERVER_VALIDATION:
    if command.description:
      rv['@description'] = description_as_json(command.description)

    rv['@errors'] = []
    for error in trait.error_list:
      if error.name == 'UNKNOWN':
        continue

      rv['@errors'].append(error.camel_name)

  if command.parameter_list:
    rv['parameters'] = fields_as_json(command.parameter_list, json_format)

  if command.response:
    rv['results'] = fields_as_json(command.response.field_list, json_format)

  return rv


def trait_as_json(trait, json_format):
  """Return an OrderedDict() that describes a trait in a weave JSON format.

  Args:
    trait: The trait to represent.
    json_format: A value from the JsonFormat class.

  Returns:
    A JSON appropriate representation.
  """

  rv = collections.OrderedDict()

  if json_format == JsonFormat.SERVER_VALIDATION:
    if trait.visibility != schema.Trait.Visibility.UNKNOWN:
      rv['@visibility'] = trait.visibility.name

  # This is where we'd include the top-level @description for the trait
  # if the server expected one.  But it doesn't, so we don't.

  if trait.command_list:
    rv['commands'] = collections.OrderedDict()

    for command in trait.command_list:
      rv['commands'][command.camel_name] = command_as_json(command, json_format)

  if trait.state_list:
    rv['state'] = fields_as_json(trait.state_list, json_format)

  if json_format == JsonFormat.SERVER_VALIDATION:
    defs = collections.OrderedDict()

    for enum in trait.enum_list:
      defs[enum.name] = enum_as_json(enum, json_format)

    for struct in trait.struct_list:
      defs[struct.name] = struct_as_json(struct, json_format)

    for entry_struct in trait.get_map_entry_structs():
      defs[entry_struct.name] = struct_as_json(entry_struct, json_format)

    if defs:
      rv['@definitions'] = defs

  if trait.command_list and json_format == JsonFormat.SERVER_VALIDATION:
    rv['@errorDescriptions'] = collections.OrderedDict()
    for error in trait.error_list:
      if error.name == 'UNKNOWN':
        continue
      rv['@errorDescriptions'][error.camel_name] = description_as_json(
          error.description)

  return rv


def interface_as_json(iface, dummy_json_format):
  """Return an OrderedDict() that describes a interface in a weave JSON format.

  Args:
    iface: The interface to represent.
    dummy_json_format: A value from the JsonFormat class. (dummy_ prefix
      squelches the pylint warning about this currently unused parameter.)

  Returns:
    A JSON appropriate representation.
  """

  rv = collections.OrderedDict()

  rv['interfaceId'] = iface.number
  rv['deviceKindName'] = iface.device_kind_name
  rv['deviceKindCode'] = iface.device_kind_code

  rv['traits'] = []
  for component in iface.component_list:
    rv_trait = collections.OrderedDict()
    rv_trait['trait'] = component.trait.class_name
    rv_trait['name'] = component.camel_name
    rv_trait['isOptional'] = component.is_optional
    rv['traits'].append(rv_trait)

  return rv
