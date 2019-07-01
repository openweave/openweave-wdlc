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
#      validates and enforces naming suffix conventions and
#      restrictions on object names.
#

"""Validator for name suffixes (e.g. Traits must end in "Trait")."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

from gwv import validator

_SUFFIX_MAP = dict(
    Trait=('Trait',),
    Command=('Request',),
    Interface=('Iface',),
    Resource=('Resource',),
    Event=('Event',),
    CommandResponse=('Response',),
    # TODO(robbarnes) Resource, Event, Response (Event), UpdateParameters
)

_ALL_SUFFIXES = frozenset(itertools.chain(*_SUFFIX_MAP.values()))

# These violate the rules, but are allowed since they can't be changed anymore.
_LEGACY_WHITELIST = frozenset([
    'weave.trait.security.UserNFCTokenManagementTrait.NFCTokenEvent',
    'nest.trait.firmware.UpgradeStateTrait.UpgradeEvent',
    'nest.trait.resourcedirectory.RelatedResourcesTrait.RelatedResource',
    'nest.trait.history.OccupancyHistoryTrait.FindOccupancyEventsResponse',
])


class NameSuffixValidator(validator.VisitorValidator):
  """Validator for name suffixes (e.g. Traits must end in "Trait")."""

  def visit_generic(self, obj):
    if obj.full_name in _LEGACY_WHITELIST:
      return

    suffixes = _SUFFIX_MAP.get(obj.__class__.__name__, None)
    if suffixes is None:
      for suffix in _ALL_SUFFIXES:
        if obj.base_name.endswith(suffix):
          self.add_failure('name should not have suffix %s' % suffix, obj)
      return

    for suffix in suffixes:
      if obj.base_name.endswith(suffix):
        break
    else:
      self.add_failure('name should have suffix %s' % ', '.join(suffixes), obj)


process = NameSuffixValidator.process
