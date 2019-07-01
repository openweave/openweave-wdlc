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
#      This file effects a Weave Data Language (WDL) validator that
#      validates and enforces that object references have consistent
#      stability and hierarchy (e.g, traits do not reference
#      resources).
#

"""Checks if references have consistent stability."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator


def _find_containing_name(obj):
  while obj:
    if (isinstance(obj, schema.StructEnumCollectionBase) or
        isinstance(obj, schema.TraitCollectionBase)):
      return type(obj).__name__, obj.full_name
    obj = obj.parent
  return None, None


def _check_references_current_version(parent, child):
  """Checks references of the current version."""

  if parent is None or child is None or parent.get_version_map() is None:
    return False

  included_version = parent.get_version_map().get_child_version(
      parent.get_version(),
      _find_containing_name(child)[1])

  return included_version == child.get_version()


class StabilityReferenceValidator(validator.VisitorValidator):
  """Checks if references have consistent stability."""

  def visit_Field(self, field):
    if _check_references_current_version(field, field.struct_type or
                                         field.enum_type):
      self.compare_stability(field, field.struct_type or field.enum_type)

  def compare_stability(self, value, referenced_value):
    if (value is None) or (referenced_value is None):
      return

    if (value.get_stability() is None) or (referenced_value.get_stability() is
                                           None):
      return

    if value.get_stability().value > referenced_value.get_stability().value:

      value_type, value_name = _find_containing_name(value)
      referenced_value_type, referenced_value_name = (
          _find_containing_name(referenced_value))

      self.add_failure("{} {} has stability {}, and references {}, which has "
                       "stability {}. {}s can only reference {}s at an "
                       "equal or higher stability level.".format(
                           value_type, value_name,
                           value.get_stability().name, referenced_value_name,
                           referenced_value.get_stability().name, value_type,
                           referenced_value_type))
      return True

  def visit_Trait(self, trait):
    if trait.extends and _check_references_current_version(
        trait, trait.extends):
      self.compare_stability(trait, trait.extends)

  def visit_Event(self, event):
    if event.extends and _check_references_current_version(
        event, event.extends):
      self.compare_stability(event, event.extends)

  def visit_Command(self, command):
    if command.extends and _check_references_current_version(
        command, command.extends):
      self.compare_stability(command, command.extends)

  def visit_CommandResponse(self, command_response):
    if command_response.extends and _check_references_current_version(
        command_response, command_response.extends):
      self.compare_stability(command_response, command_response.extends)

  def visit_Struct(self, struct):
    if struct.extends and _check_references_current_version(
        struct, struct.extends):
      self.compare_stability(struct, struct.extends)

  def visit_Component(self, component):
    if _check_references_current_version(component.parent, component.trait):
      self.compare_stability(component.parent, component.trait)

  def visit_Group(self, group):
    if _check_references_current_version(group.parent, group.interface):
      self.compare_stability(group.parent, group.interface)


process = StabilityReferenceValidator.process
