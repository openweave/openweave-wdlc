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
#      validator that validates and enforces 'extends' syntax and
#      conventions.
#

"""Validate that extends rules are followed."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import extends_validator


class ExtendsValidatorTests(validator.ValidatorTestCase):
  """Validate that extends rules are followed."""

  def test_wrong_number(self):
    trait = self.get_test_trait()
    trait.state_list.append(
        schema.Field('a_field', 1000, '', schema.Field.DataType.INT32, None))
    trait.extends = schema.Trait('super_trait', 1000, '')
    trait.extends.state_list.append(
        schema.Field('a_field', 1001, '', schema.Field.DataType.INT32, None))

    self.assert_invalid(extends_validator.ExtendsValidator,
                        'numbers for field a_field do not match')

  def test_wrong_name(self):
    trait = self.get_test_trait()
    trait.state_list.append(
        schema.Field('a_field', 1000, '', schema.Field.DataType.INT32, None))
    trait.extends = schema.Trait('super_trait', 1000, '')
    trait.extends.state_list.append(
        schema.Field('b_field', 1000, '', schema.Field.DataType.INT32, None))

    self.assert_invalid(extends_validator.ExtendsValidator,
                        'missing field b_field')

  def test_wrong_type(self):
    trait = self.get_test_trait()
    trait.state_list.append(
        schema.Field('a_field', 1000, '', schema.Field.DataType.INT32, None))
    trait.extends = schema.Trait('super_trait', 1000, '')
    trait.extends.state_list.append(
        schema.Field('a_field', 1000, '', schema.Field.DataType.FLOAT, None))

    self.assert_invalid(extends_validator.ExtendsValidator,
                        'types for field a_field do not match')

  def test_wrong_struct_type(self):
    trait = self.get_test_trait()
    sub_field = schema.Field('a_field', 1000, '', schema.Field.DataType.STRUCT,
                             None)
    sub_field.metadata = self.get_test_struct()
    trait.state_list.append(sub_field)

    super_field = schema.Field('a_field', 1000, '',
                               schema.Field.DataType.STRUCT, None)
    super_field.metadata = schema.Struct('SomeStruct', 1, '')

    trait.extends = schema.Trait('super_trait', 1000, '')
    trait.extends.state_list.append(super_field)

    self.assert_invalid(extends_validator.ExtendsValidator,
                        'types for field a_field do not match')

if __name__ == '__main__':
  unittest.main()
