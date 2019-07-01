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
#      enforces trait instance identifier uniqueness.
#

"""Validator to ensure unique trait instance ids."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class TraitInstanceIdValidator(validator.VisitorValidator):
  """Validator to ensure unique trait instance ids."""

  def visit_Resource(self, interface):
    trait_types = {}
    for component in interface.component_list:
      instances = trait_types.setdefault(component.trait.full_name, set())
      if component.instance_id in instances:
        self.add_failure("Trait component %s with type %s, has "
                         "a non unique instance id(%d)." %
                         (component.full_name, component.trait.full_name,
                          component.instance_id))
      instances.add(component.instance_id)

    for trait_type, instances in trait_types.iteritems():
      if 0 not in instances:
        self.add_failure("Trait type %s does not have a "
                         "component with instance id 0." %
                         (trait_type.full_name))


process = TraitInstanceIdValidator.process
