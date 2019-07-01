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
#      validates and enforces that a min_version for an object never
#      exceeds that of its parent.
#

"""Ensures min_version never exceeds parent version."""

from gwv import schema
from gwv import validator


class MinVersionValidator(validator.VisitorValidator):
  """Ensures min_version never exceeds parent version."""

  def visit_Field(self, field):
    trait = self.get_obj_parent_trait(field)
    if trait is None:
      # This field is not inside a trait
      return
    if field.min_version > trait.version:
      self.add_failure('Fields cannot have a min_version > trait version.')

  def visit_EnumPair(self, pair):

    trait = self.get_obj_parent_trait(pair)
    if trait is None:
      # This enum is not inside a trait
      return
    if pair.min_version > trait.version:
      self.add_failure('Enum values cannot have a min_version > trait '
                       'version.')

  def visit_ResourceComponent(self, component):

    if component.min_version > component.parent.version:
      self.add_failure('Trait instances cannot have a min_version > resource '
                       'version.')

  def visit_InterfaceComponent(self, component):

    if component.min_version > component.parent.version:
      self.add_failure('Trait instances cannot have a min_version > iface '
                       'version.')

  def visit_Group(self, group):

    if group.min_version > group.parent.version:
      self.add_failure('Iface implementations cannot have a min_version > '
                       'resource version.')

  def get_obj_parent_trait(self, field):

    parent = field.parent
    while parent is not None and not isinstance(parent, schema.Trait):
      parent = parent.parent
    return parent


process = MinVersionValidator.process
