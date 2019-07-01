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
#      validates and enforces consistency of the Java outer class name
#      across two schema corpus revisions.
#

"""Checks if java_outer_classname was removed or added in schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import validator


class NoNewJavaOuterClassnameValidator(validator.VisitorComparisonValidator):
  """Checks if java_outer_classname was removed or added in schema."""

  def _check_for_java_outer_classname(self, previous_obj):
    current_obj = self.get_obj_from_current_schema(previous_obj)

    # Only check on objects that have not been deleted.
    if (current_obj):
        if (current_obj.java_outer_classname is not None and
            (previous_obj is None or previous_obj.java_outer_classname is None)):
          self.add_failure("option java_outer_classname should not be added "
                           "to new schema.")
        elif (current_obj.java_outer_classname is None and
              previous_obj.java_outer_classname is not None):
          self.add_failure("option java_outer_classname should not be removed "
                           "from existing schema.")
        elif current_obj.java_outer_classname != previous_obj.java_outer_classname:
          self.add_failure("option java_outer_classname should not be changed.")

  def visit_Trait(self, previous_obj):
    self._check_for_java_outer_classname(previous_obj)

  def visit_Typespace(self, previous_obj):
    self._check_for_java_outer_classname(previous_obj)

  def visit_Interface(self, previous_obj):
    self._check_for_java_outer_classname(previous_obj)

  def visit_Resource(self, previous_obj):
    self._check_for_java_outer_classname(previous_obj)


process = NoNewJavaOuterClassnameValidator.process
