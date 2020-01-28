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
#      validator that validates and enforces naming suffix conventions
#      and restrictions on object names.
#

"""Validator for name suffixes (e.g. Traits must end in "Trait")."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import name_suffix_validator


class NameSuffixValidatorTests(validator.ValidatorTestCase):
  """Validator for name suffixes (e.g. Traits must end in "Trait")."""

  def test_bad_suffix(self):
    self.get_test_vendor().trait_list.append(
        schema.Trait('BadSuffix', 1000, ''))
    self.assert_invalid(name_suffix_validator.NameSuffixValidator,
                        'name should have suffix Trait')

  def test_bad_suffix_tuple(self):
    self.get_test_vendor().interface_list.append(
        schema.Interface('GoodSuffixIface', 1000, ''))
    self.get_test_vendor().resource_list.append(
        schema.Resource('GoodSuffixResource', 1001, ''))
    self.get_test_vendor().interface_list.append(
        schema.Interface('BadSuffix', 1002, ''))
    self.assert_invalid(name_suffix_validator.NameSuffixValidator,
                        'name should have suffix Iface')

  def test_bad_struct_suffix(self):
    self.get_test_trait().struct_list.append(
        schema.Struct('TestStructEvent', 2, ''))
    self.assert_invalid(name_suffix_validator.NameSuffixValidator,
                        'name should not have suffix Event')

if __name__ == '__main__':
  unittest.main()
