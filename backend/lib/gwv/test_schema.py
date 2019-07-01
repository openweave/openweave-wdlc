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
#      This file effects a Python class, based on unittest, that
#      serves as a base class for implementing schema functional and
#      unit tests.
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

from gwv import exception
from gwv import schema


class SchemaTests(unittest.TestCase):

  @classmethod
  def setUp(cls):
    cls.schema = schema.Schema()
    cls.vendor = schema.Vendor('test', 1, '')
    cls.trait = schema.Trait('Test', 1, '')
    cls.schema.vendor_list.append(cls.vendor)
    cls.vendor.trait_list.append(cls.trait)

  def test_schema_list_append_bad_type(self):
    with self.assertRaisesRegexp(
        exception.InvalidValue,
        r'Expected <class \'.*\.Trait\'> instance, got'):
      self.vendor.trait_list.append(schema.Command('Dupe', 1, ''))

  def test_duplicate_trait_ids(self):
    with self.assertRaisesRegexp(
        exception.DuplicateObject,
        r'Duplicate <class \'.*\.Trait\'> object by_number'):
      self.vendor.trait_list.append(schema.Trait('Dupe', 1, ''))

  def test_duplicate_trait_name(self):
    with self.assertRaisesRegexp(
        exception.DuplicateObject,
        r'Duplicate <class \'.*\.Trait\'> object by_name'):
      self.vendor.trait_list.append(schema.Trait('Test', 2, ''))

  def test_duplicate_command_ids(self):
    self.trait.command_list.append(schema.Command('Cmd', 1, ''))
    with self.assertRaisesRegexp(
        exception.DuplicateObject,
        r'Duplicate <class \'.*\.Command\'> object by_number'):
      self.trait.command_list.append(schema.Command('Dupe', 1, ''))

  def test_duplicate_trait_namespace_name(self):
    with self.assertRaisesRegexp(exception.DuplicateObject,
                                 r'Duplicate Typespace/Trait object by_name'):
      self.vendor.typespace_list.append(schema.Typespace('Test', 2, ''))


if __name__ == '__main__':
  unittest.main()
