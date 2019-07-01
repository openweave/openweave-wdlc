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
#      validator that validates and enforces object removal or type
#      change across two schema corpus revisions.
#

"""Checks if any objects were removed or changed type in the schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import removed_object_validator


class RemovedObjectValidatorTests(validator.ComparisonValidatorTestCase):
  """Checks if any objects were removed or changed type in the schema."""

  def test_missing_field(self):
    last_struct = self.get_test_trait().struct_list.pop()
    self.get_previous_test_trait().stability = schema.Stability.BETA
    self.assert_invalid(removed_object_validator.RemovedObjectValidator,
                        '%s.*is missing' % last_struct.base_name)

  def test_missing_trait_from_resource(self):
    last_trait = self.get_test_resource().component_list.pop()
    self.get_previous_test_resource().stability = schema.Stability.ALPHA
    self.assert_invalid(removed_object_validator.RemovedObjectValidator,
                        '%s.*is missing' % last_trait.base_name)

if __name__ == '__main__':
  unittest.main()
