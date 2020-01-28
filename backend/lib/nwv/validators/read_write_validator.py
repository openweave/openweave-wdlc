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
#      validates and enforces the 'writeable' property, in particular
#      for arrays.
#

"""Validator for read-write option."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class ReadWriteValidator(validator.VisitorValidator):
  """Validator for enum value names."""

  def visit_state_Field(self, field):
    if (field.is_array and field.struct_type and
        (field.metadata.full_name != 'weave.common.ResourceId') and
        field.writable and not field.is_map):
      self.add_failure('Field %s in %s is writable. '
                       'Arrays of structs must not be writable' %
                       (field.base_name, field.parent.full_name))


process = ReadWriteValidator.process
