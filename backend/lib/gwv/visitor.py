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
#      This file defines and implements a visitor pattern for Weave
#      Data Language (WDL) code generators and schema validators.
#

"""Abstract implementation of the visitor pattern for GWV Schema objects."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema


class SchemaVisitor(object):
  """SchemaVisitor implements the visitor pattern for schema models.

  Subclasses should override visit_* methods corresponding to the model classes
  that need to be processed. The default implementations recursively traverse
  *_list attributes; overriding methods must call the super method if this
  traversal is desired.
  """

  # This class follows the method naming convention of ast.NodeVisitor, so:
  # pylint: disable=g-bad-name

  def __init__(self, **kwargs):
    pass

  @classmethod
  def process(cls, schema_obj, **kwargs):
    cls(**kwargs).visit(schema_obj)

  def visit(self, obj, subtype_prefix=None):
    """Super method for visiting each obj."""
    if obj is None:
      return
    # First, try to visit "subtype" methods, e.g. visit_struct_Field
    if subtype_prefix:
      cls_name = obj.__class__.__name__
      getattr(self, '_visit_%s_%s' % (subtype_prefix, cls_name))(obj)
    # Next, visit methods for the obj class and any SchemaObject parent classes
    for cls in obj.__class__.__mro__:
      if (issubclass(cls, schema.SchemaObject) and
          cls is not schema.SchemaObject and
          cls is not schema.TraitCollectionBase and
          cls is not schema.StructEnumCollectionBase):
        cls_name = cls.__name__
        getattr(self, '_visit_%s' % cls_name)(obj)
    # Last, all objects get passed to visit_generic
    self.visit_generic(obj)

  def visit_list(self, lst, **kwargs):
    for obj in lst:
      self.visit(obj, **kwargs)

  def visit_generic(self, obj):
    pass

  def visit_Schema(self, schema_obj):
    pass

  def _visit_Schema(self, schema_obj):
    self.visit_Schema(schema_obj)
    self.visit_list(schema_obj.vendor_list)

  def visit_Vendor(self, vendor):
    pass

  def _visit_Vendor(self, vendor):
    self.visit_Vendor(vendor)
    self.visit_list(vendor.typespace_list)
    self.visit_list(vendor.trait_list)
    self.visit_list(vendor.interface_list)
    self.visit_list(vendor.resource_list)
    self.visit_list(vendor.struct_list)
    self.visit_list(vendor.enum_list)

  def visit_Typespace(self, typespace):
    pass

  def _visit_Typespace(self, typespace):
    self.visit_Typespace(typespace)
    self.visit_list(typespace.enum_list)
    self.visit_list(typespace.struct_list)

  def visit_Enum(self, enum):
    pass

  def _visit_Enum(self, enum):
    self.visit_Enum(enum)
    self.visit_list(enum.pair_list)

  def visit_EnumPair(self, pair):
    pass

  def _visit_EnumPair(self, pair):
    self.visit_EnumPair(pair)

  def visit_Struct(self, struct):
    pass

  def _visit_Struct(self, struct):
    self.visit_Struct(struct)
    self.visit_list(struct.field_list, subtype_prefix='struct')

  def visit_Trait(self, trait):
    pass

  def _visit_Trait(self, trait):
    self.visit_Trait(trait)
    self.visit_list(trait.enum_list)
    self.visit_list(trait.struct_list)
    self.visit_list(trait.command_list)
    self.visit_list(trait.state_list, subtype_prefix='state')
    self.visit_list(trait.event_list)

  def visit_Command(self, command):
    pass

  def _visit_Command(self, command):
    self.visit_Command(command)
    self.visit_list(command.parameter_list, subtype_prefix='parameter')
    self.visit(command.response)

  def visit_CommandResponse(self, command_response):
    pass

  def _visit_CommandResponse(self, command_response):
    self.visit_CommandResponse(command_response)
    self.visit_list(command_response.field_list, subtype_prefix='response')

  def visit_Field(self, field):
    pass

  def _visit_Field(self, field):
    self.visit_Field(field)

  def visit_Event(self, event):
    pass

  def _visit_Event(self, event):
    self.visit_Event(event)
    self.visit_list(event.field_list, subtype_prefix='event')

  def visit_event_Field(self, field):
    pass

  def _visit_event_Field(self, field):
    self.visit_event_Field(field)

  def visit_struct_Field(self, field):
    pass

  def _visit_struct_Field(self, field):
    self.visit_struct_Field(field)

  def visit_parameter_Field(self, field):
    pass

  def _visit_parameter_Field(self, field):
    self.visit_parameter_Field(field)

  def visit_response_Field(self, field):
    pass

  def _visit_response_Field(self, field):
    self.visit_response_Field(field)

  def visit_state_Field(self, field):
    pass

  def _visit_state_Field(self, field):
    self.visit_state_Field(field)

  def visit_Interface(self, interface):
    pass

  def _visit_Interface(self, interface):
    self.visit_Interface(interface)
    self.visit_list(interface.component_list)
    self.visit_list(interface.group_list)

  def visit_Resource(self, interface):
    pass

  def _visit_Resource(self, resource):
    self.visit_Resource(resource)
    self.visit_list(resource.component_list)
    self.visit_list(resource.group_list)

  def _visit_Component(self, component):
    self.visit_Component(component)

  def visit_Component(self, component):
    pass

  def _visit_InterfaceComponent(self, component):
    self.visit_InterfaceComponent(component)

  def visit_InterfaceComponent(self, component):
    pass

  def _visit_ResourceComponent(self, component):
    self.visit_ResourceComponent(component)

  def visit_ResourceComponent(self, component):
    pass

  def visit_Device(self, device):
    pass

  def _visit_Device(self, device):
    self.visit_Device(device)
    self.visit_list(device.group_list)

  def visit_Group(self, group):
    pass

  def _visit_Group(self, group):
    self.visit_Group(group)
    self.visit_list(group.component_list)

  def visit_GroupComponentRef(self, component_ref):
    pass

  def _visit_GroupComponentRef(self, component_ref):
    self.visit_GroupComponentRef(component_ref)
