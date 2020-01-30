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
#      validator that validates and enforces enumeration syntax and
#      conventions.
#

"""Validator for enum value names."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import enum_value_name_validator


class EnumValueNameValidatorTests(validator.ValidatorTestCase):
  """Validator for enum value names."""

  def test_bad_zero_name(self):
    pair_list = self.get_test_enum().pair_list
    del pair_list[0]
    pair_list.append(schema.EnumPair('TEST_ENUM_BAD_ZERO', 0, ''))
    self.assert_invalid(enum_value_name_validator.EnumValueNameValidator,
                        'enum zero value must be named'
                        '.*TEST_ENUM_UNSPECIFIED')

  def test_bad_prefix(self):
    self.get_test_enum().pair_list.append(
        schema.EnumPair('BAD_PREFIX_THREE', 3, ''))
    self.assert_invalid(enum_value_name_validator.EnumValueNameValidator,
                        'expected name to start with.*TEST_ENUM_')

if __name__ == '__main__':
  unittest.main()
