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
#      This file effects a utility for pooling a set of protobuf files
#      together to make them easier to work with.
#
#      The utility is similar to 'google.protobuf.descriptor_pool' and
#      does denormalizing and adds some features otherwise missing
#      from that package.
#

"""Utility for pooling a set of protobuf files together.

* Does a bunch of denormailzing to make them easier to work with
* Similar to google.protobuf.descriptor_pool, but adds some missing features
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import inflection

from google.protobuf import descriptor_pb2


class ProtoDesc(object):
  """Base protobuf descriptor wrapper.

  Attributes:
    file: Description
    full_name: Description
    location: Source code location info.
    parent: Parent ProtoDesc
  """

  def __init__(self, desc, full_name, file_desc, path, parent):
    self._base_ = desc
    self.full_name = full_name
    self.file = file_desc
    self.parent = parent

    if self.file is None:
      self.file = FileDesc(descriptor_pb2.FileDescriptorProto(), '<unknown>')
    self.location = self.file.get_location(path)
    # fill in an empty location if one can't be found, e.g. map entries
    if not self.location:
      self.location = descriptor_pb2.SourceCodeInfo.Location()

  # Wrap base
  def __getattr__(self, attr):
    return getattr(self._base_, attr)

  def __dir__(self):
    return list(self.__dict__.keys()) + dir(self._base_)

  # Just spit out the base as string
  def __str__(self):
    out = ''
    out += str(self._base_)
    return out


class FileDesc(ProtoDesc):

  def __init__(self, desc, full_name):
    self._locations = {str(l.path): l for l in desc.source_code_info.location}
    super(FileDesc, self).__init__(desc, full_name, self, [], None)

  # Get source_code_info location based on path
  def get_location(self, path):
    return self._locations.get(str(path))


class FieldDesc(ProtoDesc):
  """Base field descriptor wrapper."""

  def __init__(self, desc, full_name, file_desc, path, parent):
    super(FieldDesc, self).__init__(desc, full_name, file_desc, path, parent)
    self.message_type = None
    self.enum_type = None
    self.message_dependencies = collections.OrderedDict()
    self.enum_dependencies = collections.OrderedDict()

  def is_oneof(self):
    return self.HasField('oneof_index')

  def oneof_label(self):
    if self.is_oneof():
      return self.parent.oneof_decl[self.oneof_index].name

  # True if this field is a map
  def is_map(self):
    return (self.message_type and self.message_type.options and
            self.message_type.options.map_entry)


class MessageDesc(ProtoDesc):
  """Base message descriptor wrapper."""

  def __init__(self, desc, full_name, file_desc, path, parent=None):
    super(MessageDesc, self).__init__(desc, full_name, file_desc, path, parent)
    self.messages = collections.OrderedDict()
    self.enums = collections.OrderedDict()
    self.fields = collections.OrderedDict()
    self.message_dependencies = collections.OrderedDict()
    self.enum_dependencies = collections.OrderedDict()
    self.is_map_entry = desc.options and desc.options.map_entry

  def map_field(self):
    if self.is_map_entry:
      return self.parent.fields[inflection.underscore(
          self.name[:-len('Entry')])]
    return None


class EnumDesc(ProtoDesc):
  """Base enum descriptor wrapper."""

  def __init__(self, desc, full_name, file_desc, path, parent=None):
    super(EnumDesc, self).__init__(desc, full_name, file_desc, path, parent)
    self.values = collections.OrderedDict()


class EnumValueDesc(ProtoDesc):
  pass


class ProtoPool(object):
  """Pool for working with a set of proto files.

  Vends ProtoDesc objects instead of plain protobuf descriptors.
  """

  def __init__(self):
    self._files = collections.OrderedDict()
    self._messages = collections.OrderedDict()
    self._enums = collections.OrderedDict()
    self._fields = collections.OrderedDict()

  def add_file_set(self, file_generator):
    for file_desc in sorted(file_generator, key=lambda f: f.name):
      self.add_file(file_desc)
    self.update_dependencies()

  def add_file(self, file_desc):
    """Add a protobuf file to the pool.

    Args:
      file_desc: A new protobuf file descriptor to add

    Returns:
      FileDesc: The wrapped file_desc
    """

    full_name = normalize_type(file_desc.name).replace('/', '.').rsplit('.',
                                                                        1)[0]
    file_desc = self._files[file_desc.name] = FileDesc(file_desc, full_name)

    msg_index = 0
    for msg in file_desc.message_type:
      self.add_message(msg, file_desc.package, file_desc, [
          descriptor_pb2.FileDescriptorProto.MESSAGE_TYPE_FIELD_NUMBER,
          msg_index
      ])
      msg_index += 1

    enum_index = 0
    for enum in file_desc.enum_type:
      self.add_enum(enum, file_desc.package, file_desc, [
          descriptor_pb2.FileDescriptorProto.ENUM_TYPE_FIELD_NUMBER, enum_index
      ])
      enum_index += 1

    return file_desc

  def add_message(self, msg, package, file_desc, path, parent=None):
    """Adds protobuf message descriptor to pool.

    Args:
      msg: A protobuf descriptor message
      package: Package name for message
      file_desc: A prorotbuf file descriptor
      path: A list of paths.
      parent: An optional parent ProtoDesc

    Returns:
      MessageDesc: The wrapped msg
    """

    full_name = concat_name(package, msg.name)

    msg_desc = MessageDesc(msg, full_name, file_desc, path, parent)
    self._messages[full_name] = msg_desc

    if parent:
      parent.messages[msg.name] = msg_desc

    nested_index = 0
    for nested_msg in msg.nested_type:
      nested_path = path + [
          descriptor_pb2.DescriptorProto.NESTED_TYPE_FIELD_NUMBER, nested_index
      ]
      self.add_message(nested_msg, full_name, file_desc, nested_path, msg_desc)
      nested_index += 1

    enum_index = 0
    for enum in msg.enum_type:
      enum_path = path + [
          descriptor_pb2.DescriptorProto.ENUM_TYPE_FIELD_NUMBER, enum_index
      ]
      self.add_enum(enum, full_name, file_desc, enum_path, msg_desc)
      enum_index += 1

    field_index = 0
    for field in msg.field:
      field_path = path + [
          descriptor_pb2.DescriptorProto.FIELD_FIELD_NUMBER, field_index
      ]
      self.add_field(field, full_name, file_desc, field_path, msg_desc)
      field_index += 1

    return msg_desc

  def add_enum_value(self, enum_value, package, file_desc, path, parent):
    full_name = concat_name(package, enum_value.name)

    value_desc = EnumValueDesc(enum_value, full_name, file_desc, path, parent)

    parent.values[enum_value.name] = value_desc

    return value_desc

  def add_enum(self, enum, package, file_desc, path, parent=None):
    """Add an enum to the pool.

    Args:
      enum: A protobuf enum description
      package: Package name for the enum
      file_desc: The file descriptor that contains the file
      path: A path list for the enum within the file
      parent: Optional parent message

    Returns:
      EnumDesc: The wrapped enum
    """
    full_name = concat_name(package, enum.name)

    enum_desc = self._enums[full_name] = EnumDesc(enum, full_name, file_desc,
                                                  path, parent)

    if parent:
      parent.enums[enum.name] = enum_desc

    value_index = 0
    for value in enum.value:
      value_path = path + [
          descriptor_pb2.EnumDescriptorProto.VALUE_FIELD_NUMBER, value_index
      ]
      self.add_enum_value(value, full_name, file_desc, value_path, enum_desc)
      value_index += 1

    return enum_desc

  def add_field(self, field, package, file_desc, path, parent):
    full_name = concat_name(package, field.name)

    desc = FieldDesc(field, full_name, file_desc, path, parent)

    self._fields[full_name] = desc
    parent.fields[field.name] = desc

    return desc

  def update_field_types(self):
    """Fill in the message_type and enum_type on each field.

    Must be run after everything is loaded into the pool
    """

    for field in self._fields.values():
      if field.type == descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE:
        field.message_type = self.get_message(field.type_name)
      elif field.type == descriptor_pb2.FieldDescriptorProto.TYPE_ENUM:
        field.enum_type = self.get_enum(field.type_name)

  def update_dependencies(self):
    """Fill in the message and enum dependencies for each message and field.

    Must be run after everything is loaded into the pool.
    """

    self.update_field_types()
    change = True
    # Keep trying until nothing changes
    while change:
      change = False
      for field in self._fields.values():
        orig_len = (
            len(field.message_dependencies) + len(field.enum_dependencies))
        if field.message_type:
          field.message_dependencies[
              field.message_type.full_name] = field.message_type
          field.message_dependencies.update(
              field.message_type.message_dependencies)
          field.enum_dependencies.update(field.message_type.enum_dependencies)
        elif field.enum_type:
          field.enum_dependencies[field.enum_type.full_name] = field.enum_type
        field.parent.message_dependencies.update(field.message_dependencies)
        field.parent.enum_dependencies.update(field.enum_dependencies)
        if orig_len != (
            len(field.message_dependencies) + len(field.enum_dependencies)):
          change = True

  def get_file(self, type_name):
    return self._files.get(normalize_type(type_name))

  def get_message(self, type_name):
    return self._messages.get(normalize_type(type_name))

  def get_enum(self, type_name):
    return self._enums.get(normalize_type(type_name))

  def get_field(self, field_name):
    return self._fields.get(normalize_type(field_name))

  def get_files(self):
    return list(self._files.values())

  def get_messages(self):
    return list(self._messages.values())

  def get_enums(self):
    return list(self._enums.values())

  def get_fields(self):
    return list(self._fields.values())


def normalize_type(type_name):
  if type_name[0] == '.':
    type_name = type_name[1:]
  return type_name


def concat_name(package, name):
  return package + '.' + name


def parent_name(type_name):
  return normalize_type(type_name).rsplit('.', 1)[0]
