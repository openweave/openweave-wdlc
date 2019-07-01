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
#      validates and enforces duration constraints.
#

"""Validator for duration constraints."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class DurationValidator(validator.VisitorValidator):
  """Validator for duration constraints."""

  def visit_Field(self, field):
    if not (field.struct_type and
            field.struct_type.full_name == "google.protobuf.Duration"):
      return

    signed = field.is_signed
    precision = field.precision
    width = field.fixed_width

    if signed is None and precision is None and width is None:
      return

    if signed is None or precision is None or width is None:
      self.add_failure("Duration constraints, if specified, "
                       "must include signed, precision, and "
                       "width constraints.")
      return

    if not ((signed and precision == 0.001 and width == 64) or
            (not signed and precision == 0.001 and width == 32) or
            (not signed and precision == 1.0 and width == 32)):
      self.add_failure(
          "Invalid duration constraints, (must be int64 milliseconds "
          "or uint32 milliseconds or uint32 seconds) \n"
          "go/phoenix-idl-standard-types has more information")


process = DurationValidator.process
