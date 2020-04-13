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
#      validates and enforces forward object stability progression.
#

"""Checks if stability of an object moved backwards."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class StabiltyValidator(validator.VisitorComparisonValidator):
  """Checks if stability of an object moved backwards."""

  def visit_Trait(self, previous):
    self.check_stability(previous)

  def visit_Typespace(self, previous):
    self.check_stability(previous)

  def visit_Resource(self, previous):
    self.check_stability(previous)

  def visit_Interface(self, previous):
    self.check_stability(previous)

  def check_stability(self, previous_obj):
    current_obj = self.get_obj_from_current_schema(previous_obj)
    if not current_obj:
      # Removed object validator will handle this case
      return

    if current_obj.version < previous_obj.version:
      self.add_failure("Version of {} went from {} to {}. "
                       "Versions must always increase.".format(
                           previous_obj.full_name, previous_obj.version,
                           current_obj.version))
    elif current_obj.version > previous_obj.version:
      # Current version has been bumped, no restriction on stability
      pass
    elif current_obj.stability.value < previous_obj.stability.value:
      self.add_failure("Stability of {} changed from {} to {}. "
                       "Stability may only increase unless "
                       "the version number is also increased.".format(
                           previous_obj.full_name, previous_obj.stability,
                           current_obj.stability))


process = StabiltyValidator.process
