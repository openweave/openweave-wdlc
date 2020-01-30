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
#      validates and enforces that resources and interfaces only
#      implement each interface type once and only once.
#

"""Resources and ifaces may only implement each iface type once."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class OneInterfaceType(validator.VisitorValidator):
  """Resources and ifaces may only implement each iface type once."""

  def visit_Interface(self, iface):
    iface_types = []
    for group in iface.group_list:
      implemented_iface = group.interface
      if implemented_iface in iface_types:
        self.add_failure('Iface %s implements iface %s more than once' %
                         (iface.full_name, implemented_iface.full_name))
      iface_types.append(implemented_iface)

  def visit_Device(self, device):
    iface_types = []
    for group in device.group_list:
      implemented_iface = group.interface
      if implemented_iface in iface_types:
        self.add_failure('Iface %s implements iface %s more than once' %
                         (device.full_name, implemented_iface.full_name))
      iface_types.append(implemented_iface)


process = OneInterfaceType.process
