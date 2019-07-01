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
#      restrictions between object names and their corresponding file
#      names.
#

"""Validator for ensuring filenames match object name"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inflection
from gwv import validator


import unittest
from gwv import schema
from gwv import validator
from nwv.validators import filename_validator


class TestFilenameValidator(validator.ValidatorTestCase):

  def test_wrong_name(self):
    trait = self.get_test_trait()
    trait.file.base_name = 'testtrait'

    self.assert_invalid(filename_validator.FilenameValidator, r'Filename .+ should match the schema obj name')

  def test_simple_name(self):
    trait = self.get_test_trait()
    trait.file.base_name = 'test_trait'

    self.assert_valid(filename_validator.FilenameValidator)

  def test_acronym_name(self):
    trait = self.get_test_trait()
    trait.base_name = 'TestXXTrait'
    trait.file.base_name = 'test_xx_trait'

    self.assert_valid(filename_validator.FilenameValidator)

