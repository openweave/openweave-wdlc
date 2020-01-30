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
#      This file effects a Weave Data Language (WDL) validator that
#      validates and enforces 'extends' syntax and conventions.
#

"""Validate that extends rules are followed."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator


class ExtendsValidator(validator.VisitorValidator):
  """Validate that extends rules are followed."""

  def visit_generic(self, obj):
    if obj.extends:
      if not isinstance(obj, type(obj.extends)):
        self.add_failure(
            "%s extends %s, but these objects have different base types.",
            obj.full_name, obj.extends.full_name)

  def visit_Trait(self, trait):
    if trait.extends:
      self.validate_extends(trait.extends.state_list, trait.state_list)

  def visit_Command(self, command):
    if command.extends:
      self.validate_extends(command.extends.param_list, command.param_list)

  def visit_Event(self, event):
    if event.extends:
      self.validate_extends(event.extends.field_list, event.field_list)

  def visit_Struct(self, struct):
    if struct.extends:
      self.validate_extends(struct.extends.field_list, struct.field_list)

  def validate_extends(self, super_list, sub_list, is_enum=False):
    for super_field in super_list:
      sub_field = sub_list.by_name(super_field.base_name)
      if not sub_field:
        self.add_failure("%s extends %s, but %s is missing field %s." %
                         (sub_list.parent.full_name,
                          super_list.parent.full_name,
                          sub_list.parent.full_name, super_field.base_name))
      elif super_field.number != sub_field.number:
        self.add_failure("%s extends %s, but the numbers for field %s "
                         "do not match." %
                         (sub_list.parent.full_name,
                          super_list.parent.full_name, super_field.base_name))
      elif (super_field.data_type != sub_field.data_type or
            not isinstance(super_field.metadata, type(sub_field.metadata)) or
            ((sub_field.data_type == schema.Field.DataType.STRUCT or
              sub_field.data_type == schema.Field.DataType.ENUM) and
             super_field.metadata != sub_field.metadata)):
        self.add_failure("%s extends %s, but the types for field %s "
                         "do not match." %
                         (sub_list.parent.full_name,
                          super_list.parent.full_name, super_field.base_name))


process = ExtendsValidator.process
