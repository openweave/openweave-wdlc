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
#      specialized template for generating C code from Weave Data
#      Language (WDL) schema.
#

"""Specialized CodegenTemplate for generating C/C++ code."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import struct
import inflection

from gwv import schema
from gwv.templates import base


class CodegenTemplate(base.CodegenTemplate):
  """Codegen template class for *.c, *.h files.

  Might also be useful for *.cpp/*.cc in a pinch, though you'd probaby want to
  add a cc_type function (similar to c_type defined here) to come up with better
  class names.
  """

  def __init__(self, template_path):
    base.CodegenTemplate.__init__(self, template_path)
    self.desc = 'C/C++'

    self.jinja_env.globals.update(
        c_field_type=c_field_type,
        c_header_file=c_header_file,
        c_macro_name=c_macro_name,
        get_path_handles=get_path_handles,
        resource_id_bytes=resource_id_bytes,
        resource_id_number=resource_id_number,
        tlv_type=tlv_type,
        list_to_bitfield=list_to_bitfield,
        full_c_name=full_c_name,
    )

    self.jinja_env.tests.update(standard=is_standard)


def c_field_type(field):
  """Returns the field type."""

  out = field.data_type.value
  if field.data_type in (schema.Field.DataType.INT32,
                         schema.Field.DataType.UINT32,
                         schema.Field.DataType.INT64,
                         schema.Field.DataType.UINT64):
    out += '_t'

  if field.data_type == schema.Field.DataType.ENUM:
    return 'int32_t'
  if field.data_type == schema.Field.DataType.BOOL:
    return 'bool'
  if field.data_type == schema.Field.DataType.BOOL:
    return 'bool'


def c_macro_name(obj):
  """Returns the macro name."""

  package = obj.namespace.replace('.', '_').upper()
  name = inflection.underscore(obj.base_name).upper()
  return '%s__%s' % (package, name)


def c_header_file(obj, suffix=''):
  """Returns the header file."""

  if (obj.full_name.startswith('weave.common.') or
      obj.full_name.startswith('wdl.')):
    # Workaround for exceptional top-level types
    namespace = obj.namespace
  else:
    child = obj
    while child:
      parent = child.parent
      if isinstance(parent, schema.Typespace):
        namespace = parent.namespace
        break
      elif isinstance(parent, schema.Vendor):
        namespace = child.namespace
        break
      child = parent
    else:
      raise RuntimeError("couldn't find package of %s" % obj.full_name)

  namespace_path = os.path.join(*namespace.split('.'))
  name = obj.base_name
  if isinstance(obj, schema.Enum):
    name += 'Enum'
  elif isinstance(obj, schema.Struct):
    name += 'StructSchema'
  name += suffix + '.h'
  return os.path.join(namespace_path, name)


# We need to override base.is_standard because we have extra standard types
def is_standard(schema_obj):
  """Returns true if the schema_obj is a standard type."""

  if isinstance(schema_obj, schema.Field):
    return is_standard(schema_obj.metadata)
  elif isinstance(schema_obj, schema.Struct):
    standard_types = [
        # Only types that are handled by WDM translator should be
        # added here.
        'weave.common.ResourceId',
        'weave.common.ResourceName',
        'weave.common.StringRef',
        'weave.common.TraitTypeId',
        'google.protobuf.Timestamp',
        'google.protobuf.Duration',
    ]
    return schema_obj.full_name in standard_types
  return False


def get_path_handles(trait):
  """Gets the path handles."""

  queue = [(field,) for field in trait.state_list]
  out = []
  while queue:
    path = queue.pop(0)
    out.append(path)

    field = path[-1]

    if field.is_map:
      # Maps (dictionaries) are special; include only the value path
      field.map_value.number = 0
      queue.append(path + (field.map_value,))
    elif field.struct_type:
      if is_standard(field):
        continue  # Well known types are treated as atomic fields
      if field.is_array:
        continue  # Arrays cannot be recursively addressed
      for child in reversed(field.struct_type.field_list):
        queue.insert(0, path + (child,))
  return out


def tlv_type(field):
  """Returns the tlv type."""

  if field.is_map:
    return 'map <{0}, {1}>'.format(
        tlv_type(field.map_key), tlv_type(field.map_value))

  if field.enum_type and field.is_array and field.enum_type.is_bitmask:
    return 'uint'

  if field.is_array:
    return 'array'

  if field.struct_type:
    if field.struct_type.full_name == 'weave.common.StringRef':
      return 'union'
    elif field.struct_type.full_name == 'weave.common.ResourceName':
      return 'string'
    elif field.struct_type.full_name == 'weave.common.TraitTypeId':
      return 'uint32'
    elif field.struct_type.full_name == 'weave.common.ResourceId':
      return 'uint64' if field.resource_type else 'bytes'
    elif field.struct_type.full_name in ('google.protobuf.Timestamp',
                                         'google.protobuf.Duration'):
      if field.fixed_width is not None:
        return '{0}int{1} {2}'.format('u' if not field.is_signed else '',
                                      field.fixed_width, {
                                          1: 'seconds',
                                          0.001: 'milliseconds'
                                      }.get(field.precision, ''))
      return 'uint'
    else:
      return 'structure'

  if field.fixed_width:
    return ('int' if field.is_signed else 'uint') + str(field.fixed_width)

  if field.enum_type:
    return 'int'

  return field.data_type.value


def resource_id_number(resource_id_str):
  """Returns the resource id number."""

  _, hex_number = resource_id_str.split('_')
  return long(hex_number, 16)


def resource_id_bytes(resource_id_str):
  """Returns the resource id bytes."""

  type_name, _ = resource_id_str.split('_')
  number = resource_id_number(resource_id_str)
  packed = struct.pack('>HQ',
                       getattr(schema.Field.ResourceType, type_name).value,
                       number)
  return map(ord, packed)


def list_to_bitfield(table):
  """Returns a bitfield array of each element that is bool(element) == True."""

  bitfield = [0x0] * (len(table) // 8 + (len(table) % 8 > 0))
  for i in range(len(table)):
    bitfield[i // 8] |= bool(table[i]) << (i % 8)
  return bitfield


def full_c_name(obj):
  """Returns the full name."""

  if not obj:
    return ''
  return inflection.underscore('schema_{0}_{1}'.format(
      obj.namespace.replace('.', '_').replace('_trait', ''), obj.base_name))
