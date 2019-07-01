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
#      This file effects a Weave Data Language (WDL) test for the
#      validator that validates and enforces that a min_version for an
#      object never exceeds that of its parent.
#

"""Test for MinVersionValidator validator."""

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import min_version_validator


class MinVersionValidatorTests(validator.ValidatorTestCase):
  """Test for MinVersionValidator validator."""

  def test_invalid_min_version_on_state_field(self):

    trait = self.get_test_trait()
    trait.version = 2

    field = schema.Field('invalid_version', 1000, '',
                         schema.Field.DataType.STRUCT, None)
    field.min_version = 3

    trait.state_list.append(field)

    self.assert_invalid(min_version_validator.MinVersionValidator,
                        'Fields cannot have a min_version > trait '
                        'version.')

  def test_invalid_min_version_on_enum_value(self):

    trait = self.get_test_trait()
    trait.version = 2

    enum = self.get_test_enum()
    enum.pair_list[0].min_version = 3

    self.assert_invalid(min_version_validator.MinVersionValidator,
                        'Enum values cannot have a min_version > trait '
                        'version.')

  def test_invalid_min_version_on_resource_trait(self):

    resource = self.get_test_resource()
    resource_component = self.get_test_resource_component()

    resource.version = 2
    resource_component.min_version = 3

    self.assert_invalid(min_version_validator.MinVersionValidator,
                        'Trait instances cannot have a min_version > '
                        'resource version.')

  def test_invalid_min_version_on_iface_implements(self):

    resource = self.get_test_resource()
    iface_implements = self.get_test_group()

    resource.version = 2
    iface_implements.min_version = 3

    self.assert_invalid(min_version_validator.MinVersionValidator,
                        'Iface implementations cannot have a min_version '
                        '> resource version.')

if __name__ == '__main__':
  unittest.main()
