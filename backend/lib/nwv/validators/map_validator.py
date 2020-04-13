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
#      validates and enforces the validity of map keys.
#

"""Check that map keys are valid."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator

# Can't change existing Prod schemas.
_EXCEPTION_WHITELIST = [
    'nest.trait.located.CustomLocatedAnnotationsTrait.wheres_list',
    'nest.trait.located.CustomLocatedAnnotationsTrait.fixtures_list',
]


class MapValidator(validator.VisitorValidator):
  """Check that map keys are valid."""

  def visit_Field(self, field):
    if field.is_map:
      if field.full_name in _EXCEPTION_WHITELIST:
        return
      if field.map_key.data_type in (schema.Field.DataType.UINT64,
                                     schema.Field.DataType.INT64):
        self.add_failure('64 bit keys are not allowed in map keys.')


process = MapValidator.process
