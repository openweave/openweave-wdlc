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
#      validates and enforces that all field tags are less than 256.
#

"""Validate that Field tags are < 256."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class OneByteFieldTagValidator(validator.VisitorValidator):
  """Validate that Field tags are < 256."""

  def visit_Field(self, field):
    if field.number < 1 or field.number > 255:
      self.add_failure(
          'Field tags must be in range 1-255; got %d' % field.number, field)


process = OneByteFieldTagValidator.process
