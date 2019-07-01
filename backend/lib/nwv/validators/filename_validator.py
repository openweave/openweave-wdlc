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
#      validates and enforces naming conventions and restrictions
#      between object names and their corresponding file names.
#

"""Validator for ensuring filenames match object name"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inflection
from gwv import validator


class FilenameValidator(validator.VisitorValidator):
  """Validator for ensuring filenames match object name"""

  def validate_filename(self, obj):
    if obj.file.base_name != inflection.underscore(obj.base_name):
      self.add_failure(
          "Filename {} should match the schema obj name {}, except underscore".
          format(obj.file.base_name, obj.base_name))

  def visit_Trait(self, trait):
    self.validate_filename(trait)

  def visit_Typespace(self, typespace):
    self.validate_filename(typespace)

  def visit_Interface(self, iface):
    self.validate_filename(iface)

  def visit_Resource(self, resource):
    self.validate_filename(resource)


process = FilenameValidator.process
