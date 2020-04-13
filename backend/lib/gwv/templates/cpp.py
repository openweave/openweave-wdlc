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
#      This file implements a code generation target-independent
#      specialized template for generating C++ code from Weave Data
#      Language (WDL) schema.
#

"""Specialized CodegenTemplate for generating C++ code."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inflection

from gwv import schema
from gwv.templates import c


class CodegenTemplate(c.CodegenTemplate):
  """Codegen template class for *.cpp files."""

  def __init__(self, template_filename):
    c.CodegenTemplate.__init__(self, template_filename)
    self.desc = 'C++'

    self.jinja_env.globals.update(
        cpp_type=cpp_type,
        cpp_type_name=cpp_type_name,
        full_cpp_name=full_cpp_name,
    )


def cpp_type(field):
  """Returns the type."""

  data_type = field.data_type
  if field.fixed_width:
    return '%sint%d_t' % ('u' if not field.is_signed else '', field.fixed_width)
  if field.struct_type:
    if field.struct_type.full_name == 'weave.common.ResourceId':
      if field.resource_type:
        return 'uint64_t'
      else:
        return 'nl::SerializedByteString'
    elif field.struct_type.full_name == 'weave.common.ResourceName':
      return 'const char *'
    elif field.struct_type.full_name in [
        'google.protobuf.Duration', 'google.protobuf.Timestamp'
    ]:
      return 'int64_t'
    elif field.struct_type.full_name == 'weave.common.StringRef':
      return 'const char *'
    elif field.struct_type.full_name == 'weave.common.TraitTypeId':
      return 'uint32_t'
    else:
      return full_cpp_name(field.struct_type)
  elif field.enum_type:
    return 'uint32_t' if field.enum_type.is_bitmask else 'int32_t'

  return {
      schema.Field.DataType.UINT32: 'uint32_t',
      schema.Field.DataType.UINT64: 'uint64_t',
      schema.Field.DataType.INT32: 'int32_t',
      schema.Field.DataType.INT64: 'int64_t',
      schema.Field.DataType.BOOL: 'bool',
      schema.Field.DataType.FLOAT: 'float',
      schema.Field.DataType.DOUBLE: 'double',
      schema.Field.DataType.STRING: 'const char *',
      schema.Field.DataType.BYTES: 'nl::SerializedByteString',
  }[data_type]


def cpp_type_name(type_as_str):
  """Returns a human readable form of the cpp type."""

  return {
      'uint8_t': 'UInt8',
      'uint16_t': 'UInt16',
      'uint32_t': 'UInt32',
      'uint64_t': 'UInt64',
      'int8_t': 'Int8',
      'int16_t': 'Int16',
      'int32_t': 'Int32',
      'int64_t': 'Int64',
      'bool': 'Boolean',
      'float': 'FloatingPoint32',
      'double': 'FloatingPoint64',
      'const char *': 'UTF8String',
      'nl::SerializedByteString': 'ByteString',
  }.setdefault(type_as_str, 'Structure')


def full_cpp_name(obj):
  """Returns the full name."""

  if not obj:
    return ''
  return 'Schema::' + '::'.join(
      map(inflection.camelize, obj.full_name.split('.')))
