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
#      This file implements exception handlers used by the the Weave
#      Data Language (WDL) Compiler (WDLC) backend.
#

"""Exception classes used in the gwv package."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class DuplicateObject(Exception):
  """An object with the same identifier already exists in the container."""


class InvalidArgument(Exception):
  """The provided argument is invalid."""


class InvalidType(Exception):
  """The field type cannot be used in this context."""


class InvalidUsage(Exception):
  """The given usage is not valid in this context."""


class InvalidValue(Exception):
  """Invalid definition of a common error value."""


class MissingArgument(Exception):
  """A required argument is missing."""


class NotFound(Exception):
  """The requested object was not found."""
