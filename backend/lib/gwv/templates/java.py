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
#      This file implements a code generation target-independent
#      specialized template for generating Java code from Weave Data
#      Language (WDL) schema.
#

"""Utilities for generating Java code from a schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re

from gwv import exception
from gwv import schema
from gwv.templates import base


class CodegenTemplate(base.CodegenTemplate):
  """Codegen template class for *.java files.

  Methods in here should be useful for all Java targets.
  """

  def __init__(self, template_path):
    base.CodegenTemplate.__init__(self, template_path)
    self.desc = 'Java'

    self.jinja_env.globals.update({
        'java_field_type': java_field_type,
        'java_base_field_type': java_base_field_type,
        'java_type_boxed': java_type_boxed,
        'proto_wrapped_field_type': proto_wrapped_field_type,
        'get_outer_class_name': get_outer_class_name,
        'get_proto_class_name': get_proto_class_name,
        'get_java_package': get_java_package
    })

    self.jinja_env.tests.update({
        'java_field_primitive': java_field_is_primitive,
        'java_base_field_primitive': java_base_field_is_primitive
    })


def java_base_field_type(field):
  """Returns the base Java type for a field object.

  Args:
    field: Any schema field object.

  Returns:
    The Java type as a string.
  """

  if not isinstance(field, schema.Field):
    raise exception.InvalidArgument('Invalid argument to java_type: %s, %s' %
                                    (type(field).__name__, field))

  if field.data_type == schema.Field.DataType.FLOAT:
    return 'Float' if field.is_nullable else 'float'
  elif field.data_type == schema.Field.DataType.DOUBLE:
    return 'Double' if field.is_nullable else 'double'
  elif (field.data_type == schema.Field.DataType.INT64 or
        field.data_type == schema.Field.DataType.UINT64):
    return 'Long' if field.is_nullable else 'long'
  elif field.data_type == schema.Field.DataType.INT32:
    return 'Integer' if field.is_nullable else 'int'
  elif field.data_type == schema.Field.DataType.UINT32:
    return 'Integer' if field.is_nullable else 'int'
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'Boolean' if field.is_nullable else 'boolean'
  elif field.data_type == schema.Field.DataType.STRING:
    return 'String'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'byte[]'
  elif field.data_type == schema.Field.DataType.STRUCT:
    return field.metadata.full_name
  elif field.data_type == schema.Field.DataType.ENUM:
    return field.metadata.full_name
  else:
    raise exception.InvalidArgument('Invalid field type to java_type: %s, %s' %
                                    (field, field.data_type))


def proto_wrapped_field_type(field):
  """Returns the protobuf wrapped type for a field object.

  Args:
    field: Any schema field object.

  Returns:
    The protobuf wrapped type as a string.
  """

  if not isinstance(field, schema.Field):
    raise exception.InvalidArgument('Invalid argument to java_type: %s, %s' %
                                    (type(field).__name__, field))
  if field.data_type == schema.Field.DataType.FLOAT:
    return 'google.protobuf.FloatValue'
  elif field.data_type == schema.Field.DataType.DOUBLE:
    return 'google.protobuf.DoubleValue'
  elif field.data_type == schema.Field.DataType.INT64:
    return 'google.protobuf.Int64Value'
  elif field.data_type == schema.Field.DataType.UINT64:
    return 'google.protobuf.UInt64Value'
  elif field.data_type == schema.Field.DataType.INT32:
    return 'google.protobuf.Int32Value'
  elif field.data_type == schema.Field.DataType.UINT32:
    return 'google.protobuf.UInt32Value'
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'google.protobuf.BoolValue'
  elif field.data_type == schema.Field.DataType.STRING:
    return 'google.protobuf.StringValue'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'google.protobuf.BytesValue'
  else:
    raise exception.InvalidArgument('Invalid field type to java_type: %s, %s' %
                                    (field, field.data_type))


def java_base_field_is_primitive(field):
  """Check if base field is primitive Java type.

  Args:
    field: Any schema field object.

  Returns:
    True if field is primitive, False otherwise
  """

  return java_base_field_type(field) in [
      'float', 'int', 'long', 'boolean', 'double', 'short', 'char', 'byte'
  ]


def java_field_is_primitive(field):
  """Check if field is primitive Java type.

  Args:
    field: Any schema field object.

  Returns:
    True if field is primitive, False otherwise
  """

  return java_base_field_is_primitive(field) and not field.is_array


def java_field_type(obj):
  """Returns the base Java type for a schema object.

  Args:
    obj: A Field or InterfaceComponent.

  Returns:
    The Java type as a string.
  """

  if isinstance(obj, schema.Field):
    base_type = java_base_field_type(obj)
    if obj.is_array:
      return 'List<%s>' % base_type
    return base_type
  elif isinstance(obj, schema.InterfaceComponent):
    return obj.trait.full_name
  else:
    raise exception.InvalidArgument("java_field_type doesn't support %r" % obj)


def java_type_boxed(typ):
  """Returns the java boxed type."""

  boxed_map = {
      'boolean': 'Boolean',
      'byte': 'Byte',
      'char': 'Character',
      'float': 'Float',
      'int': 'Integer',
      'long': 'Long',
      'short': 'Short',
      'double': 'Double'
  }
  if typ in boxed_map:
    return boxed_map[typ]
  return typ


def get_java_package(schema_object):
  """Returns the java package."""

  return re.sub(r'\.[A-Z].*', '', schema_object.full_name)


def get_outer_class_name(schema_object):
  """Returns the outer class name."""

  if not schema_object.java_outer_classname:
    if isinstance(schema_object, schema.CommandResponse):
      return schema_object.parent.parent.base_name + 'OuterClass'
    elif (isinstance(schema_object, schema.Command) or
          isinstance(schema_object, schema.Enum) or
          isinstance(schema_object, schema.Event) or
          isinstance(schema_object, schema.Struct)):
      return schema_object.parent.base_name + 'OuterClass'
    else:
      return schema_object.base_name + 'OuterClass'
  return schema_object.java_outer_classname


def get_proto_class_name(schema_object):
  """Returns the proto class name."""

  if schema_object.full_name.startswith('google.protobuf.'):
    return ('com.' + get_java_package(schema_object) + '.' +
            schema_object.full_name.replace(
                get_java_package(schema_object) + '.', ''))
  else:
    return (get_java_package(schema_object) + '.' +
            get_outer_class_name(schema_object) + '.' +
            schema_object.full_name.replace(
                get_java_package(schema_object) + '.', ''))
