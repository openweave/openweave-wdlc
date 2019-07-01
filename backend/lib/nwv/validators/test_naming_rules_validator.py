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
#      validator that validates and enforces naming conventions and
#      restrictions on object names.
#

"""Validator for restrictions on characters within names."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import naming_rules_validator


class NamingRulesValidatorTest(validator.ValidatorTestCase):
  """Validator for restrictions on characters within names."""

  def test_underscore_start(self):
    self.get_test_vendor().trait_list.append(
        schema.Trait('_field_name', 1000, ''))
    self.assert_invalid(naming_rules_validator.NamingRulesValidator,
                        'Names cannot begin with an underscore')

  def test_underscore_end(self):
    self.get_test_vendor().trait_list.append(
        schema.Trait('field_name_', 1000, ''))
    self.assert_invalid(naming_rules_validator.NamingRulesValidator,
                        'Names cannot end with an underscore')

  def test_underscore_double(self):
    self.get_test_vendor().trait_list.append(
        schema.Trait('field__name', 1000, ''))
    self.assert_invalid(naming_rules_validator.NamingRulesValidator,
                        'Names cannot have consecutive underscores')

  def test_digit_start(self):
    self.get_test_vendor().trait_list.append(
        schema.Trait('1field_name', 1000, ''))
    self.assert_invalid(naming_rules_validator.NamingRulesValidator,
                        'Names cannot begin with a number')

  def test_multiple_errors(self):
    self.get_test_vendor().trait_list.append(
        schema.Trait('_field_name_', 1000, ''))
    self.assert_invalid(naming_rules_validator.NamingRulesValidator,
                        'Names cannot', 2)

if __name__ == '__main__':
  unittest.main()
