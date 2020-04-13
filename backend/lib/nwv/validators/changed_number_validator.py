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
#      validates and enforces object tag change (i.e., consistency)
#      across two schema corpus revisions.
#

"""Checks if any objects were removed or changed type in the schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator


class ChangedNumberValidation(validator.VisitorComparisonValidator):
  """Checks if any objects were removed or changed type in the schema."""

  def visit_Field(self, previous_field):
    self.check_number(previous_field)

  def visit_EnumPair(self, previous_enumpair):
    self.check_number(previous_enumpair)

  def visit_Trait(self, previous_trait):
    self.check_number(previous_trait)

  def visit_Component(self, previous_component):
    self.check_number(previous_component)

  def check_number(self, previous_obj):
    current_obj = self.get_obj_from_current_schema(previous_obj)
    if not current_obj:
      # Removed object validator will handle this case
      return

    if current_obj.number != previous_obj.number:
      msg = ("The id/tag number for item %s has changed from the "
             "previous schema. Changing id/tag numbers is not allowed "
             "without backward compatibility." % (previous_obj.full_name))
      if previous_obj.get_stability() is schema.Stability.ALPHA:
        self.add_warning(msg)
      else:
        self.add_failure(msg)


process = ChangedNumberValidation.process
