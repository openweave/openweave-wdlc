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
#      This file effects a Weave Data Language (WDL) validator that
#      validates and enforces the nullable constraint.
#

"""Validate that only valid fields are nullable."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator


class NullableValidator(validator.VisitorValidator):
  """Validate that only valid fields are nullable."""

  def visit_Field(self, field):
    if field.is_nullable:
      if field.is_map:
        self.add_failure('Maps cannot be nullable', field)
      elif field.is_array:
        self.add_failure('Arrays cannot be nullable', field)
      elif field.data_type == schema.Field.DataType.ENUM:
        self.add_failure('Enums cannot be nullable', field)


process = NullableValidator.process
