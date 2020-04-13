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
#      validates and enforces object removal or type change across two
#      schema corpus revisions.
#

"""Checks if any objects were removed or changed type in the schema."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from gwv import schema
from gwv import validator


class RemovedObjectValidator(validator.VisitorComparisonValidator):
  """Checks if any objects were removed or changed type in the schema."""

  def visit_generic(self, previous_obj):
    current_obj = self.get_obj_from_current_schema(previous_obj)

    if current_obj is None or not isinstance(current_obj, type(previous_obj)):
      msg = ("Previous schema item %s is missing from current "
             "schema. Schema items cannot be removed without breaking "
             "backward compatibility." % (previous_obj.full_name))
      # hasattr needed until PHX-3696 is finished adding min_version to structs.

      # Check to ensure that the object being removed has a greater version than the current parent. If not, it is going to break backward compatibility.
      # This check ony applies to objects that can be encapsulated within other objects. Traits, Typespaces don't qualify.
      if not(isinstance(previous_obj, schema.Trait) or isinstance(previous_obj, schema.Typespace)) and (previous_obj.min_version < previous_obj.parent.get_version()):
        self.add_failure(msg)
      elif previous_obj.get_stability() is schema.Stability.ALPHA:
        self.add_warning(msg)
      else:
        self.add_failure(msg)


process = RemovedObjectValidator.process
