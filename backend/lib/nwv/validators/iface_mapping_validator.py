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
#      validates and enforces interface mapping syntax and sematics.
#

"""Validate that iface mapping is valid."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class IfaceMappingValidator(validator.VisitorValidator):
  """Validate that iface mapping is valid."""

  def visit_Group(self, group):
    for iface_component in group.interface.component_list:

      if group.component_list.by_name(iface_component.base_name):
        # First check if there's an explicit mapping for this component
        source_component = group.component_list.by_name(
            iface_component.base_name).source_component
      else:
        # If not, check for an implicit mapping
        source_component = group.parent.component_list.by_name(
            iface_component.base_name)

      if source_component is None:
        self.add_failure("No valid mapping from trait {} to {}".format(
            iface_component.full_name, group.parent.full_name))
        return

      if source_component.trait != iface_component.trait:
        self.add_failure("Trait type of {} does not match {}.".format(
            source_component.full_name, iface_component.full_name))
        return

  def visit_GroupComponentRef(self, ref):
    if not ref.source_component:
      self.add_failure("Invalid mapping for {}".format(ref.full_name))
      return


process = IfaceMappingValidator.process
