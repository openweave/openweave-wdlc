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
#      This file effects a Weave Data Language (WDL) test for the
#      validator that validates and enforces interface mapping syntax
#      and sematics.
#

"""Test for iface mapping validator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import iface_mapping_validator


class IfaceMappingValidatorTest(validator.ValidatorTestCase):
  """Test for iface mapping validator."""

  def test_valid_implicit_mapping(self):
    self.assert_valid(iface_mapping_validator.IfaceMappingValidator)

  def test_invalid_implicit_mapping(self):
    extra_iface_component = schema.InterfaceComponent('extra_component', 99, '')
    extra_iface_component.trait = self.get_test_trait()
    self.get_test_iface().component_list.append(extra_iface_component)

    self.assert_invalid(iface_mapping_validator.IfaceMappingValidator,
                        r'.*No valid mapping.*')

  def test_valid_explicit_mapping(self):
    iface_component = schema.InterfaceComponent('iface_component', 99, '')
    iface_component.trait = self.get_test_trait()
    self.get_test_iface().component_list.append(iface_component)

    resource_component = schema.Component('resource_component', 66, '')
    resource_component.trait = self.get_test_trait()
    self.get_test_resource().component_list.append(resource_component)

    group_ref = schema.GroupComponentRef('iface_component', 1, '')
    group_ref.source_component = resource_component
    self.get_test_group().component_list.append(group_ref)

    self.assert_valid(iface_mapping_validator.IfaceMappingValidator)

  def test_invalid_explicit_mapping(self):
    iface_component = schema.InterfaceComponent('iface_component', 99, '')
    iface_component.trait = self.get_test_trait()
    self.get_test_iface().component_list.append(iface_component)

    resource_component = schema.Component('resource_component', 66, '')
    resource_component.trait = self.get_test_trait()
    self.get_test_resource().component_list.append(resource_component)

    group_ref = schema.GroupComponentRef('iface_component_x', 1, '')
    group_ref.source_component = resource_component
    self.get_test_group().component_list.append(group_ref)

    self.assert_invalid(iface_mapping_validator.IfaceMappingValidator,
                        r'.*No valid mapping.*')

  def test_mismatch_type_mapping(self):
    self.get_test_resource_component().trait = schema.Trait('new_trait', 99, '')

    self.assert_invalid(iface_mapping_validator.IfaceMappingValidator,
                        r'.*type .* does not match.*')

if __name__ == '__main__':
  unittest.main()
