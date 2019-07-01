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
#      validates and enforces object addition or type change across
#      two schema corpus revisions.
#

"""Checks if any objects were removed or changed type in the schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator


class AddedObjectValidator(validator.VisitorComparisonValidator):
  """Checks if any objects were removed or changed type in the schema.

  Validator that checks if objects are being added with correct version
  annotations. The comparison validator is optimized for detecting removed
  objects, so the logic here is a bit convoluted.
  """

  def check_object(self, current_obj, previous_versionable,
                   current_versionable):

    previous_obj = self.get_obj_from_previous_schema(current_obj)

    if previous_obj is not None:
      # Nothing was added, nothing to check
      return

    if current_versionable.stability is schema.Stability.PROD:
      if not current_versionable.version > previous_versionable.version:
        self.add_failure(
            '{current_obj} added to PROD {versionable_name}. Objects cannot be '
            'added to PROD {type} without incrementing the {type} version.'
            .format(
                current_obj=current_obj.full_name,
                versionable_name=current_versionable.full_name,
                type=current_versionable.__class__.__name__))
    if current_versionable.version > 1:
      if current_obj.min_version != current_versionable.version:
        self.add_failure(
            '{current_obj} added to {versionable_name}. New objects added to '
            '{type} interface with version > 1 must specify min_version == '
            '{type} version.'.format(
                current_obj=current_obj.full_name,
                versionable_name=current_versionable.full_name,
                type=current_versionable.__class__.__name__))

  def visit_Typespace(self, previous_typespace):

    current_typespace = self.get_obj_from_current_schema(previous_typespace)

    if not current_typespace:
      return

    self._check_struct_enum(previous_typespace, current_typespace)

  def visit_Trait(self, previous_trait):

    current_trait = self.get_obj_from_current_schema(previous_trait)

    if not current_trait:
      return

    for current_field in current_trait.state_list:
      self.check_object(current_field, previous_trait, current_trait)

    for current_event in current_trait.event_list:
      self.check_object(current_event, previous_trait, current_trait)
      for current_field in current_event.field_list:
        self.check_object(current_field, previous_trait, current_trait)

    for current_command in current_trait.command_list:
      self.check_object(current_command, previous_trait, current_trait)
      for current_param in current_command.parameter_list:
        self.check_object(current_param, previous_trait, current_trait)
      if current_command.response:
        for current_field in current_command.response.field_list:
          self.check_object(current_field, previous_trait, current_trait)

    self._check_struct_enum(previous_trait, current_trait)

  def _check_struct_enum(self, previous_trait, current_trait):
    for current_struct in current_trait.struct_list:
      self.check_object(current_struct, previous_trait, current_trait)
      for current_field in current_struct.field_list:
        self.check_object(current_field, previous_trait, current_trait)

    for current_enum in current_trait.enum_list:
      self.check_object(current_enum, previous_trait, current_trait)
      for enum_pair in current_enum.pair_list:
        self.check_object(enum_pair, previous_trait, current_trait)

  def visit_Resource(self, previous_resource):
    current_resource = self.get_obj_from_current_schema(previous_resource)

    for component in current_resource.component_list:
      self.check_object(component, previous_resource, current_resource)

    for group in current_resource.group_list:
      self.check_object(group, previous_resource, current_resource)

  def visit_Interface(self, previous_interface):
    current_interface = self.get_obj_from_current_schema(previous_interface)

    for component in current_interface.component_list:
      self.check_object(component, previous_interface, current_interface)

    for group in current_interface.group_list:
      self.check_object(group, previous_interface, current_interface)


process = AddedObjectValidator.process
