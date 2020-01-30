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
#      validates and enforces enumeration syntax and conventions.
#

"""Validator for enum value names."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inflection

from gwv import validator


class EnumValueNameValidator(validator.VisitorValidator):
  """Validator for enum value names."""

  def visit_Enum(self, enum):
    prefix = inflection.underscore(enum.base_name).upper() + '_'
    for pair in enum.pair_list:
      if pair.number == 0:
        zero_name = prefix + 'UNSPECIFIED'
        if pair.base_name != zero_name:
          self.add_failure('enum zero value must be named %r' % zero_name, pair)
      elif not pair.base_name.startswith(prefix):
        self.add_failure('expected name to start with %r' % prefix, pair)


process = EnumValueNameValidator.process
