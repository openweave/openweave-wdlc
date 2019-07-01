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
#      ensures that the base name for traits, interfaces, resources,
#      and typespaces are unique within that typespace.
#
#      This is required for C and Objective-C. It is also good hygiene
#      in general.
#

"""Checks if any objects have duplicate names.

This validator ensures that the base name for traits, ifaces, resources, and
typespaces are unique within that typespace. This is required for C and
Objective-C. It's also good hygiene in general.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

from gwv import validator


class UniqueNamePerVendorValidator(validator.VisitorValidator):
  """Checks if any objects have duplicate names."""

  def visit_Vendor(self, vendor):
    name_set = set()

    for obj in itertools.chain(
        iter(vendor.trait_list), iter(vendor.typespace_list),
        iter(vendor.resource_list), iter(vendor.interface_list),
        iter(vendor.struct_list), iter(vendor.enum_list)):
      if obj.base_name in name_set:
        self.add_failure("Duplicate type name (%s) detected in vendor "
                         "%s" % (obj.base_name, vendor.base_name))
      name_set.add(obj.base_name)


process = UniqueNamePerVendorValidator.process
