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
#      specialized template for generating JavaScript code from Weave
#      Data Language (WDL) schema.
#

"""Utilities for generating Javascript code from a schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import exception
from gwv import schema
from gwv.templates import base


class CodegenTemplate(base.CodegenTemplate):
  """Codegen template class for *.js files.

  Methods in here should be useful for all Javascript targets.
  """

  def __init__(self, template_path):
    base.CodegenTemplate.__init__(self, template_path)

    self.desc = "Js"

    self.jinja_env.globals.update({
        "primitive_map": primitive_map,
        "wrapped_primitive_map": wrapped_primitive_map,
    })

    self.jinja_env.tests.update({"field_is_primitive": field_is_primitive})


def primitive_map(data_type):
  """Returns the type string for a primitive field.

  Args:
      data_type: Any schema field datatype.

  Returns:
      String
  """

  return data_type.name


def wrapped_primitive_map(data_type):
  """Returns the type string for a wrapped/boxed/nullable primitive.

  Args:
      data_type: Any schema field datatype.

  Returns:
      String
  """

  if data_type.name == "FLOAT":
    return "FloatValue"
  elif data_type.name == "DOUBLE":
    return "DoubleValue"
  elif data_type.name == "INT64":
    return "Int64Value"
  elif data_type.name == "UINT64":
    return "UInt64Value"
  elif data_type.name == "INT32":
    return "Int32Value"
  elif data_type.name == "UINT32":
    return "UInt32Value"
  elif data_type.name == "BOOL":
    return "BoolValue"
  elif data_type.name == "STRING":
    return "StringValue"
  elif data_type.name == "BYTES":
    return "BytesValue"
  else:
    # TODO(michaelaaron): real error handling
    return "Error"


def field_is_primitive(field):
  """Returns the True if the field is primitive, else returns False.

  Args:
    field: Any schema field object.

  Returns:
    Boolean
  """

  if not isinstance(field, schema.Field):
    raise exception.InvalidArgument(
        "Invalid argument to field_is_primitive: %s, %s" %
        (type(field).__name__, field))

  if isinstance(field, schema.Struct):
    return False

  data_type_map = schema.Field.DataType
  if (field.data_type == data_type_map.FLOAT or
      field.data_type == data_type_map.INT64 or
      field.data_type == data_type_map.UINT64 or
      field.data_type == data_type_map.INT32 or
      field.data_type == data_type_map.UINT32 or
      field.data_type == data_type_map.DOUBLE or
      field.data_type == data_type_map.BOOL or
      field.data_type == data_type_map.STRING or
      field.data_type == data_type_map.BYTES or
      field.data_type == data_type_map.ENUM):
    return True
  else:
    return False
