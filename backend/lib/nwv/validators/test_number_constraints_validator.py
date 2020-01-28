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
#      validator that validates and enforces number constraints.
#

"""Validator for number constraints."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import number_validator


class NumberValidatorTests(validator.ValidatorTestCase):
  """Validator for number constraints."""

  def test_bad_precision(self):
    trait = self.get_test_trait()
    field = schema.Field('some_float', 1000, '')
    field.data_type = schema.Field.DataType.FLOAT
    field.precision = 0.00
    field.max_value = 20.0
    field.min_value = -10.0
    field.fixed_width = 32

    trait.state_list.append(field)

    self.assert_invalid(number_validator.NumberValidator,
                        'Zero or negative precision')

  def test_bad_min_max(self):
    trait = self.get_test_trait()
    field = schema.Field('some_float', 1000, '')
    field.data_type = schema.Field.DataType.FLOAT
    field.precision = 0.01
    field.max_value = 20.0
    field.min_value = 20.0
    field.fixed_width = 32

    trait.state_list.append(field)

    self.assert_invalid(number_validator.NumberValidator,
                        r'Max < min \+ precision')

  def test_too_big(self):
    trait = self.get_test_trait()
    field = schema.Field('some_float', 1000, '')
    field.data_type = schema.Field.DataType.FLOAT
    field.precision = 0.0000000001
    field.max_value = 2**32
    field.min_value = -2**32
    field.fixed_width = 32

    trait.state_list.append(field)

    self.assert_invalid(number_validator.NumberValidator,
                        'fixed_encoding_width > 64')

  def test_bad_fixed_width(self):
    trait = self.get_test_trait()
    field = schema.Field('some_float', 1000, '')
    field.data_type = schema.Field.DataType.FLOAT
    field.precision = 0.01
    field.max_value = 20.0
    field.min_value = -10.0
    field.fixed_width = 128

    trait.state_list.append(field)

    self.assert_invalid(number_validator.NumberValidator, 'Fixed width must be')

if __name__ == '__main__':
  unittest.main()
