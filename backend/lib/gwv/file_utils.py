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
#      This file implements utilities functions for working with and
#      manipulating files on a file system.
#

"""Collection of utility functions related to files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import errno
import fnmatch
import os
import stat


def enable_writes(filenames):
  for filename in filenames:
    if not os.path.exists(filename):
      continue

    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IWUSR)


def disable_writes(filenames):
  for filename in filenames:
    if not os.path.exists(filename):
      continue

    st = os.stat(filename)
    os.chmod(filename,
             st.st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def glob_r(directory, pattern):
  """Recursively scan a directory looking for files matching the given pattern.

  The pattern matches the full path relative to the given directory. Matches are
  checked using the fnmatch module.

  Args:
    directory: The directory to start searching in.
    pattern: A fnmatch pattern.

  Returns:
    A list of absolute paths that match.
  """

  full_paths = []
  for root, _, filenames in os.walk(directory):
    for filename in filenames:
      full_paths.append(os.path.join(root, filename))

  rv = []
  for full_path in full_paths:
    if fnmatch.fnmatch(full_path[len(directory) + 1:], pattern):
      rv.append(full_path)

  return rv


def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise
