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
#      validator that validates and enforces that object references
#      have consistent stability and hierarchy (e.g, traits do not
#      reference resources).
#

"""Checks if references have consistent stability."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import stability_reference_validator


class StabilityReferenceValidatorTest(validator.ValidatorTestCase):
  """Checks if references have consistent stability."""

  def test_resource_referencing_old_trait_invalid(self):
    self.get_test_resource().stability = schema.Stability.BETA
    # The implemented iface also has a stability mismatch, causing two errors
    # Removing all groups for this test.
    del self.get_test_resource().group_list[:]
    self.get_test_trait().stability = schema.Stability.ALPHA
    self.get_test_trait().version = 1

    self.assert_invalid(
        stability_reference_validator.StabilityReferenceValidator,
        r'.*Resources can only reference Traits.*')

  def test_resource_referencing_old_trait_valid(self):
    self.get_test_resource().stability = schema.Stability.BETA
    self.get_test_iface().stability = schema.Stability.BETA
    self.get_test_trait().stability = schema.Stability.ALPHA
    version_map = schema.VersionMap()
    version_map._parsed_map = {2: {'TestTrait': 1}}  # pylint: disable=protected-access

    self.get_test_resource().version_map = version_map

    self.assert_valid(stability_reference_validator.StabilityReferenceValidator)

  def test_resource_referencing_current_trait(self):
    self.get_test_resource().stability = schema.Stability.BETA
    self.get_test_iface().stability = schema.Stability.BETA
    self.get_test_trait().stability = schema.Stability.ALPHA
    version_map = schema.VersionMap()
    version_map._parsed_map = {2: {'TestTrait': 2}}  # pylint: disable=protected-access

    self.get_test_resource().version_map = version_map

    self.assert_invalid(
        stability_reference_validator.StabilityReferenceValidator,
        r'.*Resources can only reference Traits.*')

  def test_resource_referencing_interface(self):
    pass

  def test_interface_referencing_trait(self):
    pass

  def test_interface_referencing_interface(self):
    pass

  def test_trait_referencing_current_trait(self):
    trait = schema.Trait('Test2Trait', 2, '')
    trait.version = 2
    self.get_test_vendor().trait_list.append(trait)

    struct = schema.Struct('Test2Struct', 2, '')
    trait.struct_list.append(struct)

    field = schema.Field('field', 1000, '')
    field.struct_type = struct

    self.get_test_trait().state_list.append(field)
    self.get_test_trait().version_map = schema.VersionMap()
    self.get_test_trait().version_map._parsed_map = {2: {'Test2Trait': 2}}  # pylint: disable=protected-access

    trait.stability = schema.Stability.ALPHA
    self.get_test_trait().stability = schema.Stability.BETA

    self.assert_invalid(
        stability_reference_validator.StabilityReferenceValidator,
        r'.*Traits can only reference Traits.*')

  def test_trait_referencing_old_trait(self):
    trait = schema.Trait('Test2Trait', 2, '')
    trait.version = 2
    self.get_test_vendor().trait_list.append(trait)

    struct = schema.Struct('Test2Struct', 2, '')
    trait.struct_list.append(struct)

    field = schema.Field('field', 1000, '')
    field.struct_type = struct

    self.get_test_trait().state_list.append(field)

    trait.stability = schema.Stability.ALPHA
    self.get_test_trait().stability = schema.Stability.BETA

    self.assert_valid(stability_reference_validator.StabilityReferenceValidator)

if __name__ == '__main__':
  unittest.main()
