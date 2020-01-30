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
#      validates and enforces naming conventions and restrictions on
#      object names.
#

"""Validator for restrictions on characters within names."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class NamingRulesValidator(validator.VisitorValidator):
  """Validator for restrictions on characters within names."""

  def visit_generic(self, obj):
    name = obj.base_name

    if name[0] == ('_'):
      self.add_failure('Names cannot begin with an underscore.')

    if name[-1] == ('_'):
      self.add_failure('Names cannot end with an underscore.')

    if name[0].isdigit():
      self.add_failure('Names cannot begin with a number.')

    if '__' in name:
      self.add_failure('Names cannot have consecutive underscores.')


process = NamingRulesValidator.process
