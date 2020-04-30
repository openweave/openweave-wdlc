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
#      specialized template for generating Objective C code from Weave
#      Data Language (WDL) schema.
#

"""Utilities for generating ObjC code from a schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os
import inflection

from gwv import exception
from gwv import schema
from gwv.templates import base
import six

CLASS_PREFIX_NLK = 'NLK'
CLASS_PREFIX_GPB = 'GPB'


class CodegenTemplate(base.CodegenTemplate):
  """Objective-c codegen template class."""

  def __init__(self, template_path):
    """Initialze this CodegenTemplate.

    Args:
      template_path: The path to the template.
    """
    base.CodegenTemplate.__init__(self, template_path)
    self.desc = 'ObjC'

    self.jinja_env.globals.update({
        'flatten': flatten,
        'get_file_name': get_file_name,
        'get_directory_name': get_directory_name,
        'get_path': get_path,
        'get_root_object': get_root_object,
        'get_base_name': get_base_name,
        'get_class_name': get_class_name,
        'get_proto_class_name': get_proto_class_name,
        'get_enum_name': get_enum_name,
        'get_enum_pair_name': get_enum_pair_name,
        'get_enum_pair_swift_name': get_enum_pair_swift_name,
        'get_enum_proto_name': get_enum_proto_name,
        'get_enum_pair_proto_name': get_enum_pair_proto_name,
        'get_field_type': get_field_type,
        'get_field_class_name': get_field_class_name,
        'get_field_type_parameter': get_field_type_parameter,
        'get_field_base_type': get_field_base_type,
        'get_field_base_class_name': get_field_base_class_name,
        'get_field_proto_type': get_field_proto_type,
        'get_field_proto_class_name': get_field_proto_class_name,
        'get_field_proto_type_parameter': get_field_proto_type_parameter,
        'get_field_proto_base_type': get_field_proto_base_type,
        'get_field_proto_base_class_name': get_field_proto_base_class_name,
        'get_field_proto_base_type_name': get_field_proto_base_type_name,
        'get_field_name': get_field_name,
        'get_field_proto_name': get_field_proto_name,
        'get_field_ownership': get_field_ownership,
        'get_field_property_attributes': get_field_property_attributes,
        'get_field_clang_attributes': get_field_clang_attributes,
        'get_field_comment': get_field_comment,
        'get_field_value_method': get_field_value_method,
        'get_field_default_value': get_field_default_value,
        'get_field_test_value': get_field_test_value,
    })

    self.jinja_env.tests.update({
        'pointer': is_pointer,
        'primitive': is_primitive,
    })


def flatten(objects):
  """Returns a flatten list of objects."""

  flat_objects = []
  for obj in objects:
    if (isinstance(obj, collections.Iterable) and
        not isinstance(obj, (str, six.text_type))):
      flat_objects.extend(flatten(obj))
    elif obj is not None:
      flat_objects.append(obj)
  return flat_objects


def get_sanitized_name(name):
  """Returns a sanitized name."""

  # reserved words are copied from
  # https://github.com/google/protobuf/blob/master/src/google/protobuf/compiler/objectivec/objectivec_helpers.cc#L167
  # pylint: disable=g-inconsistent-quotes
  # pylint: disable=line-too-long
  # pyformat: disable
  reserved_words = [
      # Objective C "keywords" that aren't in C
      # From
      # http://stackoverflow.com/questions/1873630/reserved-keywords-in-objective-c
      "id", "_cmd", "super", "in", "out", "inout", "bycopy", "byref", "oneway",
      "self",

      # C/C++ keywords (Incl C++ 0x11)
      # From http://en.cppreference.com/w/cpp/keywords
      "and", "and_eq", "alignas", "alignof", "asm", "auto", "bitand", "bitor",
      "bool", "break", "case", "catch", "char", "char16_t", "char32_t", "class",
      "compl", "const", "constexpr", "const_cast", "continue", "decltype",
      "default", "delete", "double", "dynamic_cast", "else", "enum", "explicit",
      "export", "extern ", "false", "float", "for", "friend", "goto", "if",
      "inline", "int", "long", "mutable", "namespace", "new", "noexcept", "not",
      "not_eq", "nullptr", "operator", "or", "or_eq", "private", "protected",
      "public", "register", "reinterpret_cast", "return", "short", "signed",
      "sizeof", "static", "static_assert", "static_cast", "struct", "switch",
      "template", "this", "thread_local", "throw", "true", "try", "typedef",
      "typeid", "typename", "union", "unsigned", "using", "virtual", "void",
      "volatile", "wchar_t", "while", "xor", "xor_eq",

      # C99 keywords
      # From
      # http://publib.boulder.ibm.com/infocenter/lnxpcomp/v8v101/index.jsp?topic=%2Fcom.ibm.xlcpp8l.doc%2Flanguage%2Fref%2Fkeyw.htm
      "restrict",

      # Objective-C Runtime typedefs
      # From <obc/runtime.h>
      "Category", "Ivar", "Method", "Protocol",

      # NSObject Methods
      # new is covered by C++ keywords.
      "description", "debugDescription", "finalize", "hash", "dealloc", "init",
      "class", "superclass", "retain", "release", "autorelease", "retainCount",
      "zone", "isProxy", "copy", "mutableCopy", "classForCoder",

      # GPBMessage Methods
      # Only need to add instance methods that may conflict with
      # method declared in protos. The main cases are methods
      # that take no arguments, or setFoo:/hasFoo: type methods.
      "clear", "data", "delimitedData", "descriptor", "extensionRegistry",
      "extensionsCurrentlySet", "isInitialized", "serializedSize",
      "sortedExtensionsInUse", "unknownFields",

      # MacTypes.h names
      "Fixed", "Fract", "Size", "LogicalAddress", "PhysicalAddress", "ByteCount",
      "ByteOffset", "Duration", "AbsoluteTime", "OptionBits", "ItemCount",
      "PBVersion", "ScriptCode", "LangCode", "RegionCode", "OSType",
      "ProcessSerialNumber", "Point", "Rect", "FixedPoint", "FixedRect", "Style",
      "StyleParameter", "StyleField", "TimeScale", "TimeBase", "TimeRecord",
  ]
  # pylint: enable=g-inconsistent-quotes
  # pylint: enable=line-too-long
  # pyformat: enable
  if name in reserved_words:
    return '{}_p'.format(name)
  return name


def get_file_name(file_obj, prefix=CLASS_PREFIX_NLK, suffix=None):
  """Returns the file name.

  The prefix and suffix are added as is and no mutations are made.

  Args:
    file_obj: The WDL schema object create the file name for.
    prefix: The string to use as a prefix for the file name.
    suffix: The string to use as a suffix for the file name.
  """

  components = []
  if prefix is not None:
    components += prefix
  components += inflection.camelize(
      os.path.splitext(os.path.basename(file_obj.source_file))[0])
  if suffix is not None:
    components += suffix
  return ''.join(components)


def get_directory_name(file_obj):
  """Returns the directory name."""

  return os.path.dirname(file_obj.source_file)


def get_path(file_obj, extension, prefix=None, suffix=None):
  """Returns the file path."""

  base_name = ''.join([get_file_name(file_obj, prefix, suffix), '.', extension])
  return os.path.join(get_directory_name(file_obj), base_name)


def get_root_object(schema_obj):
  """Returns the root object."""

  if isinstance(schema_obj, schema.CommandResponse):
    return schema_obj.parent.parent
  elif (isinstance(schema_obj, schema.Command) or
        isinstance(schema_obj, schema.Enum) or
        isinstance(schema_obj, schema.Event) or
        isinstance(schema_obj, schema.Struct)):
    if not base.is_common(schema_obj):
      return schema_obj.parent
  return schema_obj


def get_base_name(schema_obj, separator=''):
  """Returns the base name."""

  if isinstance(schema_obj, schema.Field):
    return get_base_name(schema_obj.metadata, separator)
  root_object = get_root_object(schema_obj)
  if root_object is not schema_obj:
    return separator.join((root_object.base_name, schema_obj.base_name))
  return schema_obj.base_name


def get_class_name(schema_obj, prefix=CLASS_PREFIX_NLK):
  """Returns the class name."""

  base_name = get_base_name(schema_obj)
  if prefix is None:
    return base_name
  return prefix + base_name


def get_proto_class_name(schema_obj):
  """Returns the proto class name."""

  base_name = get_base_name(schema_obj, '_')
  if isinstance(schema_obj, schema.Field):
    return get_proto_class_name(schema_obj.metadata)
  elif isinstance(schema_obj, schema.Struct):
    if base.is_protobuf(schema_obj):
      return CLASS_PREFIX_GPB + base_name
    else:
      return schema_obj.objc_class_prefix + base_name
  return schema_obj.objc_class_prefix + base_name


def get_enum_name(enum, prefix=CLASS_PREFIX_NLK):
  """Returns the enum name."""

  return get_class_name(enum, prefix)


def get_enum_pair_name(enum_pair, prefix=CLASS_PREFIX_NLK):
  """Returns the enum_pair name."""

  base_name = get_class_name(enum_pair.parent, prefix)
  value_name = get_enum_pair_value_name(enum_pair)
  return ''.join((base_name, value_name))


def get_enum_pair_swift_name(enum_pair):
  """Returns the enum_pair swift name."""

  value_name = get_enum_pair_value_name(enum_pair)
  if value_name[0].isdigit() or len(value_name) == 1:
    return ''.join(('_', value_name))


def get_enum_pair_value_name(enum_pair):
  """Returns enum_pair value name."""

  value_name = inflection.camelize(enum_pair.base_name.lower())
  if value_name.startswith(enum_pair.parent.base_name):
    return value_name[len(enum_pair.parent.base_name):]
  return value_name


def get_enum_proto_name(enum):
  """Returns the enum proto name."""

  return get_proto_class_name(enum)


def get_enum_pair_proto_name(enum_pair):
  """Returns the enum_pair proto name."""

  base_name = get_proto_class_name(enum_pair.parent)
  value_name = get_enum_pair_value_name(enum_pair)
  return '_'.join((base_name, value_name))


def get_field_type(field, prefix=CLASS_PREFIX_NLK):
  """Returns the field type."""

  if field.is_map:
    class_name = get_field_class_name(field)
    map_key = base.map_key(field)
    map_key_type_parameter = get_field_type_parameter(map_key, prefix)
    map_value = base.map_value(field)
    map_value_type_parameter = get_field_type_parameter(map_value, prefix)
    return '{}<{}, {}> *'.format(class_name, map_key_type_parameter,
                                 map_value_type_parameter)
  elif field.is_array:
    class_name = get_field_class_name(field)
    type_parameter = get_field_type_parameter(field, prefix)
    return '{}<{}> *'.format(class_name, type_parameter)
  else:
    return get_field_base_type(field, prefix)


def get_field_class_name(field, prefix=CLASS_PREFIX_NLK):
  """Returns the field class name."""

  if field.is_map:
    return 'NSDictionary'
  elif field.is_array:
    return 'NSArray'
  else:
    return get_field_base_class_name(field, prefix)


def get_field_type_parameter(field, prefix=CLASS_PREFIX_NLK):
  """Returns the field type parameter."""

  if field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      return 'NSNumber *'
    elif field.metadata.full_name == 'google.protobuf.Timestamp':
      return 'NSDate *'
    elif field.metadata.full_name == 'weave.common.ResourceId':
      return 'NSString *'
    elif field.metadata.full_name == 'weave.common.ResourceName':
      return 'NSString *'
    else:
      if base.is_protobuf(field):
        class_name = get_proto_class_name(field)
      else:
        class_name = get_class_name(field, prefix)
      return '{} *'.format(class_name)
  elif is_primitive(field):
    return 'NSNumber *'
  elif field.data_type == schema.Field.DataType.STRING:
    return 'NSString *'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'NSData *'
  raise exception.InvalidArgument(field)


def get_field_base_type(field, prefix=CLASS_PREFIX_NLK):
  """Returns the field base type."""

  if is_primitive(field) and not field.is_nullable:
    return get_field_primitive_type(field)
  else:
    class_name = get_field_base_class_name(field, prefix)
    return '{} *'.format(class_name)


def get_field_base_class_name(field, prefix=CLASS_PREFIX_NLK):
  """Returns the field base class name."""

  if field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      if field.is_nullable:
        return 'NSNumber'
    elif field.metadata.full_name == 'google.protobuf.Timestamp':
      return 'NSDate'
    elif field.metadata.full_name == 'weave.common.ResourceId':
      return 'NSString'
    elif field.metadata.full_name == 'weave.common.ResourceName':
      return 'NSString'
    else:
      if base.is_protobuf(field):
        return get_proto_class_name(field)
      else:
        return get_class_name(field, prefix)
  elif is_primitive(field):
    if field.is_nullable:
      return 'NSNumber'
  elif field.data_type == schema.Field.DataType.STRING:
    return 'NSString'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'NSData'
  raise exception.InvalidArgument(field)


def get_field_primitive_type(field, prefix=CLASS_PREFIX_NLK):
  """Returns the field primitive type."""

  if field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      return 'NSTimeInterval'
  elif field.data_type == schema.Field.DataType.ENUM:
    return get_enum_name(field, prefix)
  elif field.data_type == schema.Field.DataType.FLOAT:
    return 'float'
  elif field.data_type == schema.Field.DataType.DOUBLE:
    return 'double'
  elif field.data_type == schema.Field.DataType.INT64:
    return 'int64_t'
  elif field.data_type == schema.Field.DataType.UINT64:
    return 'uint64_t'
  elif field.data_type == schema.Field.DataType.INT32:
    return 'int32_t'
  elif field.data_type == schema.Field.DataType.UINT32:
    return 'uint32_t'
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'BOOL'
  raise exception.InvalidArgument(field)


def get_field_proto_type(field):
  """Returns the field proto type."""

  if field.is_map:
    class_name = get_field_proto_class_name(field)
    map_key = base.map_key(field)
    map_key_type_parameter = get_field_proto_type_parameter(map_key)
    map_value = base.map_value(field)
    map_value_type_parameter = get_field_proto_type_parameter(map_value)
    if (map_key.data_type == schema.Field.DataType.STRING and
        (map_value.data_type == schema.Field.DataType.STRUCT or
         map_value.data_type == schema.Field.DataType.STRING or
         map_value.data_type == schema.Field.DataType.BYTES)):
      return '{}<{}, {}> *'.format(class_name, map_key_type_parameter,
                                   map_value_type_parameter)
    elif (map_value.data_type == schema.Field.DataType.STRUCT or
          map_value.data_type == schema.Field.DataType.STRING or
          map_value.data_type == schema.Field.DataType.BYTES):
      type_parameter = get_field_proto_type_parameter(field)
      return '{}<{}> *'.format(class_name, type_parameter)
    else:
      return '{} *'.format(class_name)
  elif field.is_array:
    class_name = get_field_proto_class_name(field)
    if (field.data_type == schema.Field.DataType.STRUCT or
        field.data_type == schema.Field.DataType.STRING or
        field.data_type == schema.Field.DataType.BYTES):
      type_parameter = get_field_proto_type_parameter(field)
      return '{}<{}> *'.format(class_name, type_parameter)
    else:
      return '{} *'.format(class_name)
  else:
    return get_field_proto_base_type(field)


def get_field_proto_class_name(field):
  """Returns the field proto class name."""

  if field.is_map:
    map_key = base.map_key(field)
    map_value = base.map_value(field)
    if (map_key.data_type == schema.Field.DataType.STRING and
        (map_value.data_type == schema.Field.DataType.STRUCT or
         map_value.data_type == schema.Field.DataType.STRING or
         map_value.data_type == schema.Field.DataType.BYTES)):
      return 'NSMutableDictionary'
    else:
      return get_field_proto_dictionary_class_name(field)
  elif field.is_array:
    if (field.data_type == schema.Field.DataType.STRUCT or
        field.data_type == schema.Field.DataType.STRING or
        field.data_type == schema.Field.DataType.BYTES):
      return 'NSMutableArray'
    else:
      return get_field_proto_array_class_name(field)
  else:
    return get_proto_class_name(field)


def get_field_proto_type_parameter(field):
  """Returns the field proto type parameter."""

  if field.data_type == schema.Field.DataType.STRUCT:
    class_name = get_proto_class_name(field)
    return '{} *'.format(class_name)
  elif field.data_type == schema.Field.DataType.STRING:
    return 'NSString *'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'NSData *'
  raise exception.InvalidArgument(field)


def get_field_proto_base_type(field):
  """Returns the field proto base type."""

  if (field.data_type == schema.Field.DataType.STRUCT or
      field.data_type == schema.Field.DataType.STRING or
      field.data_type == schema.Field.DataType.BYTES):
    class_name = get_field_proto_base_class_name(field)
    return '{} *'.format(class_name)
  else:
    return get_field_proto_primitive_type(field)


def get_field_proto_base_class_name(field):
  """Returns the field proto base class name."""

  if field.data_type == schema.Field.DataType.STRUCT:
    return get_proto_class_name(field)
  elif field.data_type == schema.Field.DataType.STRING:
    return 'NSString'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'NSData'
  raise exception.InvalidArgument(field)


def get_field_proto_primitive_type(field):
  """Returns the field proto primitive type."""

  if field.data_type == schema.Field.DataType.ENUM:
    return get_enum_proto_name(field)
  elif field.data_type == schema.Field.DataType.FLOAT:
    return 'float'
  elif field.data_type == schema.Field.DataType.DOUBLE:
    return 'double'
  elif field.data_type == schema.Field.DataType.INT64:
    return 'int64_t'
  elif field.data_type == schema.Field.DataType.UINT64:
    return 'uint64_t'
  elif field.data_type == schema.Field.DataType.INT32:
    return 'int32_t'
  elif field.data_type == schema.Field.DataType.UINT32:
    return 'uint32_t'
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'BOOL'
  raise exception.InvalidArgument(field)


def get_field_proto_base_type_name(field):
  """Returns the field proto base type name."""

  if field.data_type == schema.Field.DataType.ENUM:
    return 'Enum'
  elif field.data_type == schema.Field.DataType.FLOAT:
    return 'Float'
  elif field.data_type == schema.Field.DataType.DOUBLE:
    return 'Double'
  elif field.data_type == schema.Field.DataType.INT64:
    return 'Int64'
  elif field.data_type == schema.Field.DataType.UINT64:
    return 'UInt64'
  elif field.data_type == schema.Field.DataType.INT32:
    return 'Int32'
  elif field.data_type == schema.Field.DataType.UINT32:
    return 'UInt32'
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'Bool'
  elif field.data_type == schema.Field.DataType.STRING:
    return 'String'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'Data'
  elif field.data_type == schema.Field.DataType.STRUCT:
    return 'Message'
  raise exception.InvalidArgument(field)


def get_field_proto_array_class_name(field):
  """Returns the field proto array class name."""

  array_types = [
      schema.Field.DataType.ENUM,
      schema.Field.DataType.FLOAT,
      schema.Field.DataType.DOUBLE,
      schema.Field.DataType.INT64,
      schema.Field.DataType.UINT64,
      schema.Field.DataType.INT32,
      schema.Field.DataType.UINT32,
      schema.Field.DataType.BOOL,
  ]
  if field.data_type in array_types:
    class_name = [
        CLASS_PREFIX_GPB,
        get_field_proto_base_type_name(field),
        'Array',
    ]
    return ''.join(class_name)
  raise exception.InvalidArgument(field)


def get_field_proto_dictionary_class_name(field):
  """Returns the field proto dictionary class name."""

  map_key = base.map_key(field)
  map_key_types = [
      schema.Field.DataType.INT64,
      schema.Field.DataType.UINT64,
      schema.Field.DataType.INT32,
      schema.Field.DataType.UINT32,
      schema.Field.DataType.BOOL,
      schema.Field.DataType.STRING,
  ]
  if map_key.data_type in map_key_types:
    map_value = base.map_value(field)
    map_value_object_types = [
        schema.Field.DataType.STRUCT,
        schema.Field.DataType.STRING,
        schema.Field.DataType.BYTES,
    ]
    if map_value.data_type in map_value_object_types:
      map_value_base_type_name = 'Object'
    else:
      map_value_base_type_name = get_field_proto_base_type_name(map_value)
    class_name = [
        CLASS_PREFIX_GPB,
        get_field_proto_base_type_name(map_key),
        map_value_base_type_name,
        'Dictionary',
    ]
    return ''.join(class_name)
  raise exception.InvalidArgument(field)


def get_field_base_name(field):
  """Returns the field base name."""

  uppercase_segments = [
      'url',
      'http',
      'https',
  ]
  segments = [
      x.upper() if x in uppercase_segments else x
      for x in field.base_name.split('_')
  ]
  base_name = '_'.join(segments)
  return inflection.camelize(base_name, False)


def get_field_name(field, uppercase_first_letter=False):
  """Returns the field name."""

  base_name = get_field_base_name(field)
  base_name = get_sanitized_name(base_name)
  if uppercase_first_letter:
    return base_name[0].upper() + base_name[1:]
  return base_name


def get_field_proto_name(field, uppercase_first_letter=False):
  """Returns the field proto name."""

  base_name = get_field_base_name(field)
  if field.is_array:
    base_name = '{}Array'.format(base_name)
  elif base_name.endswith('Array'):
    base_name = '{}_p'.format(base_name)
  base_name = get_sanitized_name(base_name)
  if uppercase_first_letter:
    return base_name[0].upper() + base_name[1:]
  return base_name


def get_field_ownership(field):
  """Returns the field ownership."""

  if field.is_map:
    return 'copy'
  elif field.is_array:
    return 'copy'
  elif field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      if field.is_nullable:
        return 'strong'
      else:
        return 'assign'
    elif field.metadata.full_name == 'google.protobuf.Timestamp':
      return 'strong'
    elif field.metadata.full_name == 'weave.common.ResourceId':
      return 'copy'
    elif field.metadata.full_name == 'weave.common.ResourceName':
      return 'copy'
    else:
      return 'strong'
  elif is_primitive(field):
    if field.is_nullable:
      return 'strong'
    else:
      return 'assign'
  elif field.data_type == schema.Field.DataType.STRING:
    return 'copy'
  elif field.data_type == schema.Field.DataType.BYTES:
    return 'copy'
  raise exception.InvalidArgument(field)


def get_field_property_attributes(field, readonly=True):
  """Returns the field property attributes."""

  attributes = ['nonatomic', get_field_ownership(field)]
  if field.is_nullable:
    attributes.append('nullable')
  if readonly:
    attributes.append('readonly')
  else:
    attributes.append('readwrite')
  return attributes


def get_field_clang_attributes(field):
  """Returns the field clang attributes."""

  attributes = []
  if (is_pointer(field) and field.base_name.startswith(
      ('alloc_', 'copy_', 'mutable_copy_', 'new_'))):
    attributes.append('NS_RETURNS_NOT_RETAINED')
  return attributes


def get_field_comment(field, prefix=CLASS_PREFIX_NLK):
  """Returns the field comment."""

  if is_primitive(field):
    if field.is_map or field.is_array:
      primitive_type = get_field_primitive_type(field, prefix)
      return '{} values'.format(primitive_type)
    elif field.is_nullable:
      primitive_type = get_field_primitive_type(field, prefix)
      return '{} value'.format(primitive_type)


def get_field_value_method(field):
  """Returns the field value method."""

  if field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      return 'doubleValue'
  elif field.data_type == schema.Field.DataType.ENUM:
    return 'intValue'
  elif field.data_type == schema.Field.DataType.FLOAT:
    return 'floatValue'
  elif field.data_type == schema.Field.DataType.DOUBLE:
    return 'doubleValue'
  elif field.data_type == schema.Field.DataType.INT64:
    return 'longLongValue'
  elif field.data_type == schema.Field.DataType.UINT64:
    return 'unsignedLongLongValue'
  elif field.data_type == schema.Field.DataType.INT32:
    return 'intValue'
  elif field.data_type == schema.Field.DataType.UINT32:
    return 'unsignedIntValue'
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'boolValue'
  raise exception.InvalidArgument(field)


def get_field_default_value(field):
  """Returns the field default value."""

  if field.is_map:
    raise exception.InvalidArgument(field)
  elif field.is_array:
    raise exception.InvalidArgument(field)
  else:
    return get_field_default_base_value(field)


def get_field_default_base_value(field):
  """Returns the field default base value."""

  if field.is_nullable:
    return 'nil'
  if field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      return '0'
    elif field.metadata.full_name == 'google.protobuf.Timestamp':
      return 'Date(timeIntervalSince1970: 0)'
    elif field.metadata.full_name == 'weave.common.ResourceId':
      return '""'
    elif field.metadata.full_name == 'weave.common.ResourceName':
      return '""'
  elif field.data_type == schema.Field.DataType.ENUM:
    if field.is_map or field.is_array:
      return '0'
    else:
      enum_pair = field.metadata.pair_list[1]
      name = get_enum_pair_swift_name(enum_pair)
      if name is None:
        name = get_enum_pair_value_name(enum_pair)
        name = inflection.camelize(name, False)
      return '.{}'.format(name)
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'false'
  elif is_primitive(field):
    return '0'
  elif field.data_type == schema.Field.DataType.STRING:
    return '""'
  elif field.data_type == schema.Field.DataType.BYTES:
    return '"".data(using: String.Encoding.utf8)!'
  raise exception.InvalidArgument(field)


def get_field_test_value(field):
  """Returns the field test value."""

  base_value = get_field_test_base_value(field)
  if field.is_map:
    map_key = base.map_key(field)
    if is_primitive(map_key):
      map_key_value = 1
    elif map_key.data_type == schema.Field.DataType.STRING:
      map_key_value = '"1"'
    return '[{}: {}]'.format(map_key_value, base_value)
  elif field.is_array:
    return '[{}]'.format(base_value)
  else:
    return base_value


def get_field_test_base_value(field):
  """Returns the field test base value."""

  if field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      return '1'
    elif field.metadata.full_name == 'google.protobuf.Timestamp':
      return 'Date(timeIntervalSince1970: 1)'
    elif field.metadata.full_name == 'weave.common.ResourceId':
      return '"test-resource-id"'
    elif field.metadata.full_name == 'weave.common.ResourceName':
      return '"test-resource-name"'
    else:
      class_name = get_class_name(field)
      return '{}()'.format(class_name)
  elif field.data_type == schema.Field.DataType.ENUM:
    if field.is_map or field.is_array:
      return 1
    else:
      enum_pair = field.metadata.pair_list[1]
      name = get_enum_pair_swift_name(enum_pair)
      if name is None:
        name = get_enum_pair_value_name(enum_pair)
        name = inflection.camelize(name, False)
      return '.{}'.format(name)
  elif field.data_type == schema.Field.DataType.BOOL:
    return 'true'
  elif is_primitive(field):
    return '1'
  elif field.data_type == schema.Field.DataType.STRING:
    return '"test-string"'
  elif field.data_type == schema.Field.DataType.BYTES:
    return '"test-data".data(using: String.Encoding.utf8)!'
  raise exception.InvalidArgument(field)


def is_pointer(field):
  """Checks if pointer."""

  return (field.is_map or field.is_array or field.is_nullable or
          not is_primitive(field))


def is_primitive(field):
  """Checks if primitive."""

  if field.data_type == schema.Field.DataType.STRUCT:
    if field.metadata.full_name == 'google.protobuf.Duration':
      return True
  primitive_types = [
      schema.Field.DataType.ENUM,
      schema.Field.DataType.FLOAT,
      schema.Field.DataType.DOUBLE,
      schema.Field.DataType.INT64,
      schema.Field.DataType.UINT64,
      schema.Field.DataType.INT32,
      schema.Field.DataType.UINT32,
      schema.Field.DataType.BOOL,
  ]
  return field.data_type in primitive_types
