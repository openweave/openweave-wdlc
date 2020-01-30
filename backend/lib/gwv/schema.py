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
#      This file implements the main schema parser and handler for
#      generating code from Weave Data Language (WDL) schema.
#

"""Schema objects for the Google Weave Schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from enum import Enum as PyEnum  # Renamed to avoid confusion with schema.Enum

from gwv import exception


def get_schema(obj):
  """Return the root Schema instance for a given object.

  Args:
    obj: SchemaObject or a list of SchemaObjects to traverse.

  Returns:
    The root Schema object.

  Raises:
    Exception: Unexpected condition while searching.
  """

  while obj is not None:
    if isinstance(obj, Schema):
      return obj

    if hasattr(obj, 'parent'):
      obj = obj.parent
    else:
      raise Exception('Lost the trail while looking for schema object')

  raise Exception('Schema object not found')


class Stability(PyEnum):
  """Stability levels for schema objects."""

  ALPHA = 0
  BETA = 1
  PROD = 2


def get_stability(obj):
  """Gets the stability for a given schema object.

  Most objects do not have a stability flag. Objects inherit their
  stability from their parent. So this method walks up the given
  objects parents looking for a stability flag. If one is not found
  None is returned.

  Args:
    obj: SchemaObject or a list of SchemaObjects to traverse.

  Returns:
    The stability level for the given
  """

  while obj:
    if hasattr(obj, 'stability'):
      return obj.stability
    obj = obj.parent
  return None


def _get_version_map(obj):
  while obj:
    if hasattr(obj, 'version_map'):
      return obj.version_map
    obj = obj.parent
  return None


def _get_version(obj):
  while obj:
    if hasattr(obj, 'version'):
      return obj.version
    obj = obj.parent
  return None


class SchemaObject(object):
  """The base class used for other objects in the schema.

  All schema objects have a name, number, and description.  When added to a
  list, the name and number must be unique to the list.
  """

  def __init__(self, full_name, number, description):
    self.number = number
    self.description = description
    self.objc_class_prefix = None
    self.java_outer_classname = None

    # The parent SchemaObject, even if it means jumping over a list.
    self.parent = None

    # The parent schema_object_list.
    self.parent_list = None

    # The file that this object was sourced from.
    self.source_file = '<unknown>'  # Deprecated use file instead
    self.file = None

    # The schema object that this object is derived from.
    self.derived_from = None

    # The schema object extends another object
    self.extends = None

    self.full_name = full_name

    name_components = full_name.rsplit('.', 1)
    if len(name_components) > 1:
      self.namespace = name_components[0]
      self.base_name = name_components[1]
    else:
      self.namespace = None
      self.base_name = name_components[0]

  def __str__(self):
    return self.full_name

  def __repr__(self):
    return '%s(%r)' % (self.__class__.__name__, self.full_name)

  def get_schema(self):
    return get_schema(self)

  def get_stability(self):
    return get_stability(self)

  def get_version(self):
    return _get_version(self)

  def get_version_map(self):
    return _get_version_map(self)


class SchemaObjectList(list):
  """Base class used for lists of schema objects.

  The schema_object_list function will generate a new SchemaObjectList
  subclass
  tailored to a specific SchemaObject subclass.
  """

  def __init__(self, parent, base_name):
    list.__init__(self)
    self.parent = parent
    self.base_name = base_name

  def __validate__(self, element):
    """Override this to add additional validation to list.append()."""

    pass

  def get_schema(self):
    return get_schema(self)

  def by_name(self, name):
    for obj in self:
      if obj.base_name == name:
        return obj

    return None

  def by_number(self, number):
    for obj in self:
      if obj.number == number:
        return obj

    return None


def schema_object_list(schema_object_class):
  """Returns a new list subclass tailored to the given schema_object_class.

  Used to construct lists of schema objects such as Traits, Interfaces,
  Commands, and other subclasses of SchemaObject.

  Args:
    schema_object_class: A subclass of SchemaObject.

  Returns:
    A new list<schema_object_class> class.
  """

  class SchemaObjectListSubclass(SchemaObjectList):
    """A list<schema_object_class> class."""

    def append(self, obj):
      """Override the standard list append method.

      Args:
        obj: The object to append.

      Returns:
        Whatever list.append returns.

      Raises:
        exception.InvalidValue: The object is of the wrong type.
        exception.DuplicateObject: An object with the same name or number that
          already exists in the list.
      """

      if not isinstance(obj, schema_object_class):
        raise exception.InvalidValue('Expected %s instance, got %s' %
                                     (str(schema_object_class), str(obj)))

      if self.by_name(obj.base_name):
        raise exception.DuplicateObject(
            'Duplicate %s object by_name on %s: %s' %
            (str(schema_object_class), self.parent.full_name, obj.base_name))

      if self.by_number(obj.number):
        raise exception.DuplicateObject(
            'Duplicate %s object by_number on %s: %s' %
            (str(schema_object_class), self.parent.full_name, obj.base_name))

      self.__validate__(obj)

      if not isinstance(self.parent, File):
        obj.parent_list = self
        obj.parent = self.parent

      return list.append(self, obj)

  return SchemaObjectListSubclass


class File(SchemaObject):
  """A File in the schema."""

  def __init__(self, name, number, description):
    """Construct and initialize a Constant instance.

    Args:
      name: The name of this file.
      number: The number of this file.
      description: A short description for the file.
    """

    SchemaObject.__init__(self, name, number, description)
    self.trait_list = TraitList(self, 'trait_list')
    self.typespace_list = TypespaceList(self, 'typespace_list')
    self.interface_list = InterfaceList(self, 'interface_list')
    self.resource_list = ResourceList(self, 'resource_list')
    self.struct_list = StructList(self, 'struct_list')
    self.enum_list = EnumList(self, 'enum_list')


class FileList(schema_object_list(File)):
  """A list of File objects."""

  pass


class Constant(SchemaObject):
  """A Constant in the schema.

  Used to represent named constants.
  """

  class Type(PyEnum):
    """List of constant types supported by the schema."""

    RESOURCE_ID = 'resource_id'

  def __init__(self, name, number, description, constant_type, value):
    """Construct and initialize a Constant instance.

    Args:
      name: The name of this constant.
      number: The number of this constant.
      description: A short description for the constant.
      constant_type: The type of this constant.
      value: The value of this constant.
    """

    SchemaObject.__init__(self, name, number, description)
    self.constant_type = constant_type
    self.value = value


class ConstantList(schema_object_list(Constant)):
  """A list of Constant objects."""

  pass


class ConstantGroup(SchemaObject):
  """A named group of Constants."""

  def __init__(self, name, number, description):
    """Construct and initialize a ConstantGroup.

    Args:
      name: The name of this constant group.
      number: The number of this constant group.
      description: A short description for the constant group.
    """

    SchemaObject.__init__(self, name, number, description)

    self.constant_list = ConstantList(self, 'constant_list')


class ConstantGroupList(schema_object_list(ConstantGroup)):
  """A list of ConstantGroup objects."""

  pass


class Field(SchemaObject):
  """A Field in the schema.

  Used to represent fields in command parameters and results, fields in the
  trait state, and fields in arbitrary objects.
  """

  class DataType(PyEnum):
    """List of data types supported by the schema."""

    # Constraint-based types that represent native types.
    FLOAT = 'float'
    DOUBLE = 'double'
    INT64 = 'int64'
    UINT64 = 'uint64'
    INT32 = 'int32'
    UINT32 = 'uint32'
    BOOL = 'bool'
    STRING = 'string'
    BYTES = 'bytes'

    # Schema-object types that refer to concepts from the Google Weave schema.
    ENUM = 'enum'
    STRUCT = 'struct'

  class ResourceType(PyEnum):
    """List of resource types supported by the schema."""

    DEVICE = 1
    USER = 2
    ACCOUNT = 3
    AREA = 4
    FIXTURE = 5
    GROUP = 6
    ANNOTATION = 7
    STRUCTURE = 8
    GUEST = 9

  def __init__(self, name, number, description, data_type=None, metadata=None):
    """Construct and initialize a field.

    Args:
      name: The name of this field.
      number: The number of this field.
      description: A brief description for this field.
      data_type: The data type of this field.
      metadata: The metadata of this field.
    """

    SchemaObject.__init__(self, name, number, description)
    self.data_type = data_type
    self.metadata = metadata
    self.is_optional = False
    self.deprecated = False
    self.is_array = False
    self.is_nullable = False
    self.writable = False
    self.is_oneof = False
    self.is_map = False
    self.resource_type = None
    self.is_ephemeral = False
    self.max_value = None
    self.min_value = None
    self.max_length = None
    self.fixed_width = None
    self.is_signed = None
    self.precision = None
    self.struct_type = None
    self.enum_type = None
    self.min_version = 1
    self.max_version = None


class EnumPair(SchemaObject):
  """A name, value pair from an enumeration.

  These consist entirely of the name, a number, and a description attributes
  inherited from SchemaObject.
  """

  def __init__(self, name, number, description):
    """Construct and initialize an EnumPair instance.

    Args:
      name: The name of this enum pair.
      number: The number of this pair.
      description: A short description for the pair.
    """

    SchemaObject.__init__(self, name, number, description)

    self.min_version = 1
    self.max_version = None


class EnumPairList(schema_object_list(EnumPair)):
  """A list of EnumPairs.

  Standard enums have no restrictions other than the unique name/number
  constraint provided by SchemaObject.
  """

  pass


class Enum(SchemaObject):
  """An enumeration of named integer values."""

  def __init__(self, name, number, description):
    """Construct and initialize an Enum instance.

    Args:
      name: The name of this enumeration.
      number: The number of this enumeration.
      description: A short description for the enumeration.
    """

    SchemaObject.__init__(self, name, number, description)

    self.pair_list = EnumPairList(self, 'pair_list')
    self.is_bitmask = False
    self.min_version = 1
    self.max_version = None


class EnumList(schema_object_list(Enum)):
  """A list of Enum objects."""

  pass


class StructFieldList(schema_object_list(Field)):
  """A data structure consisting of one or more fields."""

  pass


class Struct(SchemaObject):
  """A data structure defined and used by a trait."""

  def __init__(self, name, number, description):
    """Construct and initialize a Struct object.

    Args:
      name: The name of this struct.
      number: The number of this struct.
      description: A brief description of this struct.
    """

    SchemaObject.__init__(self, name, number, description)
    self.field_list = StructFieldList(self, 'field_list')
    self.min_version = 1
    self.max_version = None


class Event(Struct):
  """A data structure defined and used by a trait."""

  class Importance(PyEnum):
    PRODUCTION_CRITICAL = 1
    PRODUCTION_STANDARD = 2
    INFO = 3
    DEBUG = 4

  def __init__(self, name, number, description):
    """Construct and initialize a Event object.

    Args:
      name: The name of this event.
      number: The number of this event.
      description: A brief description of this event.
    """
    Struct.__init__(self, name, number, description)
    self.importance = Event.Importance.DEBUG


class StructList(schema_object_list(Struct)):
  """A list of Struct objects."""

  pass


class EventList(schema_object_list(Event)):
  """A list of Event objects."""

  pass


class ParameterList(schema_object_list(Field)):
  """A list of Field objects used as the parameter format of a command."""

  pass


class ResultList(schema_object_list(Field)):
  """A list of Field objects used as the results format of a command."""

  pass


class StateList(schema_object_list(Field)):
  """A list of Field objects used as the state of a trait."""

  pass


class Command(SchemaObject):
  """Definition of a command supported by the given trait."""

  def __init__(self, name, number, description):
    """Construct and initialize a Command object.

    Args:
      name: The name of this command.
      number: The number of this command.
      description: A short description for the command.
    """

    SchemaObject.__init__(self, name, number, description)
    self.parameter_list = ParameterList(self, 'parameter_list')
    self.response = None
    self.min_version = 1
    self.max_version = None


class CommandResponse(Struct):
  """Definition of a command response for a command."""

  def __init__(
      self,
      name,
      number,
      description,
  ):
    """Construct and initialize a Command Response object.

    Args:
      name: The name of this command response.
      number: The number of this command response.
      description: A short description for the command response.
    """

    Struct.__init__(self, name, number, description)


class CommandList(schema_object_list(Command)):
  """A list of Command objects."""

  pass


class StructEnumCollectionBase(SchemaObject):

  def __init__(self, name, number, description):
    """Construct and initialize a StructEnumCollectionBase instance.

    Args:
      name: The name of this typespace.
      number: The number of this typespace.
      description: A short description for the typespace.
    """

    SchemaObject.__init__(self, name, number, description)

    self.stability = Stability.ALPHA
    self.version = 0
    self.constant_group_list = ConstantGroupList(self, 'constant_group_list')
    self.enum_list = EnumList(self, 'enum_list')
    self.struct_list = StructList(self, 'struct_list')
    self.version_map = VersionMap()


class Typespace(StructEnumCollectionBase):
  """Definition of a typespace in a schema."""

  pass


class TypespaceList(schema_object_list(Typespace)):
  """A list of Typespace objects."""

  def append(self, typespace):
    if self:
      typespace.number = max(typespace.number for typespace in self) + 1
    else:
      typespace.number = 0
    super(TypespaceList, self).append(typespace)

  def by_number(self, _):
    return None  # Typespaces do not have meaningful numbers

  def __validate__(self, typespace):
    if self.parent.trait_list.by_name(typespace.base_name):
      raise exception.DuplicateObject(
          'Duplicate Typespace/Trait object by_name on %s: %s' %
          (self.parent.full_name, typespace.base_name))


class Trait(StructEnumCollectionBase):
  """Definition of a trait in a schema."""

  def __init__(self, name, number, description):
    """Construct and initialize a Trait instance.

    Args:
      name: The name of this trait.
      number: The number of this trait.
      description: A short description for the trait.
    """

    StructEnumCollectionBase.__init__(self, name, number, description)

    self.command_list = CommandList(self, 'command_list')
    self.state_list = StateList(self, 'state_list')
    self.event_list = EventList(self, 'event_list')

  def get_map_entry_structs(self):
    """Return all Structs defined by MAP fields in this Trait.

    Returns:
      A list of MAP entry Structs.
    """

    structs = []
    for command in self.command_list:
      for param in command.parameter_list:
        if param.is_map:
          structs.append(param.metadata)
    return structs


class TraitList(schema_object_list(Trait)):
  """A list of Trait objects."""

  def append(self, trait):
    super(TraitList, self).append(trait)
    self.sort(key=lambda t: t.number)

  def __validate__(self, trait):
    if self.parent.typespace_list.by_name(trait.base_name):
      raise exception.DuplicateObject(
          'Duplicate Typespace/Trait object by_name on %s: %s' %
          (self.parent.full_name, trait.base_name))


class Component(SchemaObject):
  """A component in an interface or resource."""

  def __init__(self, name, number, description):
    SchemaObject.__init__(self, name, number, description)
    # Will be set during linking
    self.trait = None
    self.min_version = 1
    self.max_version = None


class InterfaceComponent(Component):
  """A component in an interface."""

  pass


class ResourceComponent(Component):
  """A component in a trait."""

  class PublishedBy(PyEnum):
    SELF = 0
    EXTERNAL = 1

  def __init__(self, name, number, description):
    Component.__init__(self, name, number, description)
    # Will be set during linking
    self.instance_id = 0
    self.proxied = False
    self.subsribed = False
    self.published_by = ResourceComponent.PublishedBy.SELF
    self.property_refinements = {}


class FieldRefinement(object):
  """A refinement on a field."""

  def __init__(self, field):
    self.field = field
    self.implemented = True
    self.initial_value = None


class ComponentList(schema_object_list(Component)):
  """A list of Field objects.

  Used to represent the named traits of an interface.
  """

  pass


class TraitCollectionBase(SchemaObject):
  """Base class for Interfaces and Resources."""

  def __init__(self, name, number, description):
    """Construct and initialize a TraitGroupBase instance.

    Args:
      name: The name of this trait.
      number: The number of this trait.
      description: A short description for the trait.
    """

    SchemaObject.__init__(self, name, number, description)

    # TODO(rginda): These are really just a weave-specific alias to the
    # interface.  Maybe move this to codegen as a vendor+interface to
    # device_kind mapping.
    self.device_kind_name = None
    self.device_kind_code = None

    self.component_list = ComponentList(self, 'component_list')
    self.group_list = GroupList(self, 'group_list')
    self.variations = []
    self.stability = Stability.ALPHA
    self.version = 1
    self.version_map = VersionMap()


class Interface(TraitCollectionBase):
  """A group of traits that work together in a known manner."""

  pass


class InterfaceList(schema_object_list(Interface)):
  """A list of interfaces defined by a vendor."""

  def append(self, interface):
    super(InterfaceList, self).append(interface)
    self.sort(key=lambda i: i.number)


class GroupComponentRef(SchemaObject):
  """A reference to a another component defined in a device."""

  def __init__(self, name, number, description):
    """Construct and initialize a GroupComponentRef instance.

    Args:
      name: The name of this component group.
      number: The number of component group.
      description: A short description for the trait.
    """

    SchemaObject.__init__(self, name, number, description)

    self.source_component = None


class GroupComponentRefList(schema_object_list(GroupComponentRef)):
  pass


class Group(SchemaObject):
  """A named, and optionally typed, group of components.

  This is used to represent named component groups in a Device object.
  """

  def __init__(self, name, number, description):
    """Construct and initialize a Group instance.

    Args:
      name: The name of this group.
      number: The number of group.
      description: A short description for the trait.
    """

    SchemaObject.__init__(self, name, number, description)

    self.component_list = GroupComponentRefList(self, 'component_list')
    self.interface = None
    self.min_version = 1


class GroupList(schema_object_list(Group)):
  """A list of component groups on a device."""

  pass


class Resource(TraitCollectionBase):
  """A definition of a resource, usually a device."""

  pass


class ResourceList(schema_object_list(Resource)):
  """A list of resources."""

  pass


class Vendor(SchemaObject):
  """Definition of a vendor in a schema.

  A vendor is a namespace for traits, interfaces, and the objects they contain.
  """

  def __init__(self, name, number, description):
    """Construct and initialize a Vendor instance.

    Args:
      name: The name of this vendor.
      number: The number of this vendor.
      description: A short description for the vendor.
    """

    SchemaObject.__init__(self, name, number, description)
    self.file_list = FileList(self, 'file_list')
    self.trait_list = TraitList(self, 'trait_list')
    self.typespace_list = TypespaceList(self, 'typespace_list')
    self.interface_list = InterfaceList(self, 'interface_list')
    self.resource_list = ResourceList(self, 'resource_list')
    self.struct_list = StructList(self, 'struct_list')
    self.enum_list = EnumList(self, 'enum_list')

  def resolve_namespace(self, name):
    return self.typespace_list.by_name(name) or self.trait_list.by_name(name)


class VendorList(schema_object_list(Vendor)):
  """A list of Vendor objects."""

  pass


class Schema(SchemaObject):
  """The root object in the Google Weave schema."""

  def __init__(self):
    SchemaObject.__init__(self, 'Schema', 0, 'Google Weave Schema root object')
    self.vendor_list = VendorList(self, 'vendor_list')

  def trait_by_name(self, vendor_name, trait_name):
    vendor = self.vendor_list.by_name(vendor_name)
    if not vendor:
      return None

    return vendor.trait_list.by_name(trait_name)

  def full_name(self):
    return ''


class VersionMap(object):
  """A container for the WDL options version_map field.

  This map is currently applicable to resources and interfaces.
  """

  def __init__(self, version_map_extension=None):
    """Parse the version map from the proto file into a more useful format.

    Args:
      version_map_extension: The version_map object from the protobuf file.
    """

    self._parsed_map = {}
    if version_map_extension is None:
      return

    for version in version_map_extension:
      if hasattr(version, 'resource_version'):
        iface_trait_map = {
            t.name: t.version for t in version.trait_version_list
        }
        iface_trait_map.update(
            {t.name: t.version for t in version.iface_version_list})
        self._parsed_map[version.resource_version] = iface_trait_map

      if hasattr(version, 'parent_version'):
        trait_map = {t.name: t.version for t in version.dependent_version_list}
        self._parsed_map[version.parent_version] = trait_map

  def __bool__(self):
    return bool(self._parsed_map)

  __nonzero__ = __bool__

  def __str__(self):
    return str(self._parsed_map)

  def get_child_version(self, parent_version, child_name):
    """Gets the version of a child at a given parent version.

    Args:
      parent_version: Version number of the parent message.
      child_name: Fully qualified name of the trait or iface in question.

    Returns:
      Version (int) of child specified by the parent version.
    """
    for version in reversed(sorted(self._parsed_map)):
      if version > parent_version:
        continue

      v = self._parsed_map[version].get(child_name)
      if v is not None:
        return v

    return 1  # Default version is 1 if not specified otherwise.
