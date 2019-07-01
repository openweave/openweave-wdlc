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
#      validator that validates and enforces consistency of the Java
#      outer class name across two schema corpus revisions.
#

"""Checks if java_outer_classname was removed or added in schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import validator
from nwv.validators import no_new_java_outer_classname_validator


class NoNewJavaOuterClassnameValidatorTest(
    validator.ComparisonValidatorTestCase):
  """Checks if java_outer_classname was removed or added in schema."""

  def test_trait_new_option(self):
    self.get_test_trait().java_outer_classname = 'something'
    self.assert_invalid(
        no_new_java_outer_classname_validator.NoNewJavaOuterClassnameValidator,
        'should not be added')

  def test_typespace_existing_option(self):
    self.get_test_typespace().java_outer_classname = None
    self.get_previous_test_typespace().java_outer_classname = 'something'
    self.assert_invalid(
        no_new_java_outer_classname_validator.NoNewJavaOuterClassnameValidator,
        'should not be removed')

  def test_resource_new_existing_option(self):
    self.get_test_resource().java_outer_classname = 'something'
    self.get_previous_test_resource().java_outer_classname = 'something_else'
    self.assert_invalid(
        no_new_java_outer_classname_validator.NoNewJavaOuterClassnameValidator,
        'should not be changed')

  def test_interface_new_existing_valid_with(self):
    self.get_previous_test_iface().java_outer_classname = 'something'
    self.get_test_iface().java_outer_classname = 'something'
    self.assert_valid(
        no_new_java_outer_classname_validator.NoNewJavaOuterClassnameValidator)

  def test_interface_new_existing_valid_without(self):
    self.get_previous_test_iface().java_outer_classname = None
    self.get_test_iface().java_outer_classname = None
    self.assert_valid(
        no_new_java_outer_classname_validator.NoNewJavaOuterClassnameValidator)

if __name__ == '__main__':
  unittest.main()
