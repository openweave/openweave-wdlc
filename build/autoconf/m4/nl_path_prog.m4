#
#    Copyright (c) 2019 Google LLC.
#    All rights reserved.
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
#      This file defines a GNU autoconf M4-style macro to check for
#      the absolute pathname of an executable program.
#

#
# NL_PATH_PROG(variable, prog-to-check-for, error-message-if-not-found)
#
#   variable                   - The environment variable to check as the
#                                default and, if empty, to set to the
#                                absolute pathname of prog-to-check-for
#                                when found in PATH.
#
#   prog-to-check-for          - The executable program to search for in
#                                PATH.
#
#   error-message-if-not-found - The error message to display if prog-to-
#                                check-for is not found.
#
# Like AC_PATH_PROG, but fails with the specified error message if the
# absolute name of <prog-to-check-for> cannot be found.
#
# Again, like AC_PATH_PROG, the result of this test can be overridden
# by setting the variable, <variable>. A positive result of this test
# is cached in the ac_cv_path_<variable> variable.
#
# ----------------------------------------------------------------------------
AC_DEFUN([NL_PATH_PROG],
[
    AC_PATH_PROG($1, $2)

    if test "${$1}" = ""; then
        AC_MSG_ERROR([could not find $2: $3])
    fi
])
