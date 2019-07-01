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
#      validator that validates and enforces the validity of map keys.
#

"""Check that map keys are valid."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import map_validator


class MapValidatorTests(validator.ValidatorTestCase):
  """Check that map keys are valid."""

  def test_bad_map(self):

    map_key = schema.Field('key', 1, '', schema.Field.DataType.UINT64, None)

    field = schema.Field('invalid_map', 1000, '', schema.Field.DataType.STRUCT,
                         None)
    field.is_map = True
    field.map_key = map_key
    self.get_test_trait().state_list.append(field)

    self.assert_invalid(map_validator.MapValidator,
                        '64 bit keys are not allowed in map keys.')

if __name__ == '__main__':
  unittest.main()
