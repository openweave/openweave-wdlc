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
#      validator that validates and enforces naming case conventions
#      and restrictions on object names.
#

"""Validator for name inflection (e.g. CamelCase)."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import name_inflection_validator


class NameInflectionValidatorTests(validator.ValidatorTestCase):
  """Validator for name inflection (e.g. CamelCase)."""

  def test_bad_camelcase(self):
    self.get_test_vendor().trait_list.append(
        schema.Trait('badCamelTrait', 1000, ''))
    self.assert_invalid(name_inflection_validator.NameInflectionValidator,
                        'incorrect name inflection; expected.*BadCamelTrait')

  def test_bad_underscore(self):
    self.get_test_trait().state_list.append(
        schema.Field('badUnderScore', 1000, '', schema.Field.DataType.STRING,
                     None))
    self.assert_invalid(name_inflection_validator.NameInflectionValidator,
                        'incorrect name inflection; expected.*bad_under_score')

if __name__ == '__main__':
  unittest.main()
