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
#      validator that validates and enforces forward object stability
#      progression.
#

"""Checks if stability of an object moved backwards."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import stability_validator


class StabilityValidatorTest(validator.ComparisonValidatorTestCase):
  """Checks if stability of an object moved backwards."""

  def test_trait_version_moved_backwards(self):
    self.get_test_trait().version = 1
    self.get_previous_test_trait().version = 2

    self.assert_invalid(stability_validator.StabiltyValidator,
                        r'.*Versions must always increase.*')

  def test_trait_stability_moved_backwards(self):
    self.get_previous_test_trait().version = 2
    self.get_previous_test_trait().stability = schema.Stability.BETA
    self.get_test_trait().version = 2
    self.get_test_trait().stability = schema.Stability.ALPHA

    self.assert_invalid(stability_validator.StabiltyValidator,
                        r'.*Stability may only increase.*')

  def test_trait_stability_and_version_moved_backwards(self):
    self.get_previous_test_trait().version = 1
    self.get_previous_test_trait().stability = schema.Stability.BETA
    self.get_test_trait().version = 2
    self.get_test_trait().stability = schema.Stability.ALPHA

    self.assert_valid(stability_validator.StabiltyValidator)

if __name__ == '__main__':
  unittest.main()
