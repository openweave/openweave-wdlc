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
#      validates and enforces naming case conventions and restrictions
#      on object names.
#

"""Validator for name inflection (e.g. CamelCase)."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inflection

from gwv import validator

INFLECTION_MAP = dict(
    Typespace=inflection.camelize,
    Enum=inflection.camelize,
    Struct=inflection.camelize,
    Trait=inflection.camelize,
    Command=inflection.camelize,
    Interface=inflection.camelize,
    Device=inflection.camelize,
    Field=inflection.underscore)


class NameInflectionValidator(validator.VisitorValidator):
  """Validator for name inflection (e.g. CamelCase)."""

  def visit_generic(self, obj):
    inflection_func = INFLECTION_MAP.get(obj.__class__.__name__, None)
    if inflection_func is None:
      return

    name = obj.base_name
    expected = inflection_func(name)
    if name != expected:
      self.add_failure('incorrect name inflection; expected %r' % expected, obj)


process = NameInflectionValidator.process
