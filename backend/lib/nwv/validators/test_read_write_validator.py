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
#      validator that validates and enforces the 'writeable' property,
#      in particular for arrays.
#

"""Validator for read-write option."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import read_write_validator


class ReadWriteValidatorTests(validator.ValidatorTestCase):
  """Validator for read-write option."""

  def test_writable_array(self):

    field = schema.Field('writable_array', 1000, '',
                         schema.Field.DataType.STRUCT, None)
    field.is_array = True
    field.metadata = self.get_test_struct()
    field.struct_type = field.metadata
    field.writable = True
    self.get_test_trait().state_list.append(field)

    self.assert_invalid(read_write_validator.ReadWriteValidator,
                        'Field writable_array in TestTrait is writable. '
                        'Arrays of structs must not be writable')

if __name__ == '__main__':
  unittest.main()
