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
#      This file effects a Weave Data Language (WDL) validator that
#      validates and enforces number constraints.
#

"""Validator for number constraints."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

from gwv import schema
from gwv import validator


class NumberValidator(validator.VisitorValidator):
  """Validator for number constraints."""

  def visit_Field(self, field):
    if field.data_type not in (schema.Field.DataType.FLOAT,
                               schema.Field.DataType.DOUBLE):
      return

    if (field.min_value is not None or field.max_value is not None or
        field.precision is not None):

      # If one of these constraints is defined, they all must be defined
      if (field.max_value is None or field.min_value is None or
          field.precision is None or field.fixed_width is None):
        self.add_failure('Numbers must specify max_value, '
                         'min_value, fixed_width, and precision.')
        return

      fixed_encoding_width = self.fpn(field.min_value, field.max_value,
                                      field.precision)
      if field.fixed_width < fixed_encoding_width:
        self.add_failure('Fixed width not large enough for given '
                         'min, max and precision.')

    if field.fixed_width is not None:
      if field.fixed_width > 64 or field.fixed_width < 8:
        self.add_failure('Fixed width must be <= 64 and >= 8')
        return

      if field.fixed_width not in (64, 32, 16, 8):
        self.add_failure('Fixed width must be a power of 2')
        return

  def fpn(self, min_value, max_value, precision):

    if max_value < min_value + precision:
      self.add_failure('Max < min + precision')
      return

    if precision <= 0.0:
      self.add_failure('Zero or negative precision')
      return

    fractional_bits = math.ceil(-math.log(precision, 2))
    lower_bound = math.ceil((min_value - precision / 2) * 2**fractional_bits)
    upper_bound = math.floor((max_value + precision / 2) * 2**fractional_bits)
    fixed_encoding_width = math.ceil(math.log(upper_bound - lower_bound + 1, 2))

    # TODO(robbarnes) this value is not used, but is kept for completeness
    # integer_bits = fixed_encoding_width - fractional_bits

    if fixed_encoding_width > 64:
      self.add_failure('fixed_encoding_width > 64')
      return

    return fixed_encoding_width


process = NumberValidator.process
