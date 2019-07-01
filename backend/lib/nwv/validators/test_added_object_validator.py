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
#      validator that validates and enforces object addition or type
#      change across two schema corpus revisions.
#

"""Checks if any objects were removed or changed type in the schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import validator
from nwv.validators import added_object_validator


class AddedObjectValidatorTest(validator.ComparisonValidatorTestCase):
  """Checks if any objects were removed or changed type in the schema."""

  NEW_OBJECT_ON_PROD_ERR_MSG = (r'.*Objects cannot be added to PROD .* without '
                                r'incrementing the .* version.*')
  NEW_OBJECT_ADDED_ERR_MSG = (r'.*New objects added to .* with version > 1 must'
                              r' specify min_version.*')

  def test_field_added_to_prod_trait_correctly(self):
    self.get_test_trait().version = 2
    self.get_previous_test_trait().version = 1

    self.get_test_trait().stability = schema.Stability.PROD
    self.get_previous_test_trait().stability = schema.Stability.PROD

    added_field = schema.Field('new_field', 1000, '',
                               schema.Field.DataType.INT32, None)
    added_field.min_version = 2

    self.assert_valid(added_object_validator.AddedObjectValidator)

  def test_event_added_to_prod_trait_without_increment_trait_version(self):

    self.get_test_trait().stability = schema.Stability.PROD
    self.get_previous_test_trait().stability = schema.Stability.PROD

    added_event = schema.Event('NewEvent', 1000, '')
    added_event.min_version = self.get_test_trait().version
    self.get_test_trait().event_list.append(added_event)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ON_PROD_ERR_MSG)

  def test_field_added_to_prod_trait_without_increment_trait_version(self):

    self.get_test_trait().stability = schema.Stability.PROD
    self.get_previous_test_trait().stability = schema.Stability.PROD

    added_field = schema.Field('new_field', 1000, '',
                               schema.Field.DataType.INT32, None)
    added_field.min_version = self.get_test_trait().version
    self.get_test_trait().state_list.append(added_field)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ON_PROD_ERR_MSG)

  def test_command_added_to_prod_trait_without_increment_trait_version(self):

    self.get_test_trait().stability = schema.Stability.PROD
    self.get_previous_test_trait().stability = schema.Stability.PROD

    added_command = schema.Command('NewRequest', 1000, '')
    added_command.min_version = self.get_test_trait().version
    self.get_test_trait().command_list.append(added_command)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ON_PROD_ERR_MSG)

  def test_field_added_to_trait_without_min_version(self):

    added_field = schema.Field('new_field', 1000, '',
                               schema.Field.DataType.INT32, None)
    self.get_test_trait().state_list.append(added_field)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_event_added_to_trait_without_min_version(self):

    added_event = schema.Event('NewEvent', 1000, '')
    self.get_test_trait().event_list.append(added_event)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_field_added_to_event_without_min_version(self):

    added_field = schema.Field('new_field', 1000, '',
                               schema.Field.DataType.INT32, None)
    self.get_test_event().field_list.append(added_field)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_command_without_min_version(self):

    added_command = schema.Command('NewCommand', 1000, '')
    self.get_test_trait().command_list.append(added_command)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_field_added_to_command_without_min_version(self):

    added_field = schema.Field('new_field', 1000, '',
                               schema.Field.DataType.INT32, None)
    self.get_test_command().parameter_list.append(added_field)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_field_added_to_response_without_min_version(self):

    added_field = schema.Field('new_field', 1000, '',
                               schema.Field.DataType.INT32, None)
    self.get_test_response().field_list.append(added_field)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_enum_pair_added_without_min_version(self):

    added_pair = schema.EnumPair('new_pair', 1000, '')
    self.get_test_enum().pair_list.append(added_pair)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_enum_added_without_min_version(self):

    added_enum = schema.Enum('new_Enum', 1000, '')
    self.get_test_trait().enum_list.append(added_enum)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_trait_added_to_resource_without_min_version(self):

    new_trait = schema.Trait('NewTrait', 2, '')
    resource_component = schema.ResourceComponent('new_test_component', 1000,
                                                  '')
    resource_component.trait = new_trait

    self.get_test_vendor().trait_list.append(new_trait)
    self.get_test_resource().component_list.append(resource_component)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_struct_added_without_min_version(self):

    added_struct = schema.Struct('new_Struct', 1000, '')
    self.get_test_typespace().struct_list.append(added_struct)
    self.get_test_typespace().version = 2

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_interface_added_to_resource_without_min_version(self):

    new_iface = schema.Interface('NewTestIface', 0x100, '')
    group = schema.Group('new_test_group', 1000, '')
    group.iface = new_iface

    self.get_test_resource().group_list.append(group)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

  def test_trait_added_to_interface_without_min_version(self):

    new_trait = schema.Trait('NewTrait', 2, '')
    interface_component = schema.InterfaceComponent('new_test_component', 1000,
                                                    '')
    interface_component.trait = new_trait

    self.get_test_vendor().trait_list.append(new_trait)
    self.get_test_iface().version = 2
    self.get_test_iface().component_list.append(interface_component)

    self.assert_invalid(added_object_validator.AddedObjectValidator,
                        self.NEW_OBJECT_ADDED_ERR_MSG)

if __name__ == '__main__':
  unittest.main()
