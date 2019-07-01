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
#      validator that validates and enforces the nullable constraint.
#

"""Validate that only valid fields are nullable."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import nullable_validator


class NullableValidatorTests(validator.ValidatorTestCase):
  """Validate that only valid fields are nullable."""

  def test_nullable_array(self):

    field = schema.Field('nullable_array', 1000, '',
                         schema.Field.DataType.STRUCT, None)
    field.is_array = True
    field.metadata = self.get_test_struct()
    field.is_nullable = True
    self.get_test_trait().state_list.append(field)

    self.assert_invalid(nullable_validator.NullableValidator,
                        'Arrays cannot be nullable')

  def test_nullable_map(self):

    field = schema.Field('nullable_map', 1000, '', schema.Field.DataType.STRUCT,
                         None)
    field.is_array = True
    field.is_map = True
    field.metadata = self.get_test_struct()
    field.is_nullable = True
    self.get_test_trait().state_list.append(field)

    self.assert_invalid(nullable_validator.NullableValidator,
                        'Maps cannot be nullable')

  def test_nullable_enum(self):

    field = schema.Field('nullable_enum', 1000, '', schema.Field.DataType.ENUM,
                         None)
    field.metadata = self.get_test_enum()
    field.is_nullable = True
    self.get_test_trait().state_list.append(field)

    self.assert_invalid(nullable_validator.NullableValidator,
                        'Enums cannot be nullable')

if __name__ == '__main__':
  unittest.main()
