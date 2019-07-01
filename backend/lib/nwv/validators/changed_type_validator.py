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
#      validates and enforces object type change (i.e., consistency)
#      across two schema corpus revisions.
#

"""Checks if the type on any object was changed."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator


class ChangedTypeValidator(validator.VisitorComparisonValidator):
  """Checks if the type on any object was changed."""

  def visit_Field(self, previous_field):
    current_field = self.get_obj_from_current_schema(previous_field)
    if not current_field:
      # Removed object validator will handle this case
      return

    if (current_field.data_type != previous_field.data_type or (
        (current_field.data_type == schema.Field.DataType.STRUCT or
         current_field.data_type == schema.Field.DataType.ENUM) and
        current_field.metadata.full_name != previous_field.metadata.full_name)):
      msg = ("The type for field %s has changed from the "
             "previous schema. Changing field type is not allowed "
             "without breaking backward compatibility." %
             (previous_field.full_name))
      if current_field.get_stability() is schema.Stability.ALPHA:
        self.add_warning(msg)
      else:
        self.add_failure(msg)

  def visit_Component(self, previous_component):
    current_component = self.get_obj_from_current_schema(previous_component)

    if not current_component:
      # Removed object validator will handle this case
      return

    if current_component.trait.full_name != previous_component.trait.full_name:
      msg = ("The type for component %s has changed from the "
             "previous schema. Changing component type is not allowed "
             "without breaking backward compatibility." %
             (previous_component.full_name))
      if current_component.get_stability() is schema.Stability.ALPHA:
        self.add_warning(msg)
      else:
        self.add_failure(msg)


process = ChangedTypeValidator.process
