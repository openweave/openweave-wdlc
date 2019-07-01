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
#      This file defines a GNU autoconf M4-style macro to check for the
#      presence of a Python module.
#

#
# NL_CHECK_PYTHON_MODULE(module, URL)
#
#   module  - The python module to check.
#
#   URL     - A URL to display on failure to guide the user on installing
#             <module>.
#
# This checks the configuration cache and, failing that, checks
# directly with python, via the PYTHON variable, whether the specified
# python module, <module>, is installed. If the module is not
# installed, the user is provided actionable instructions in the form
# of a URL, <URL>, to download and install the module.
#
# The value 'nl_cv_python_has_module_<module>' will be set to the result.
#
# ----------------------------------------------------------------------------
AC_DEFUN([NL_CHECK_PYTHON_MODULE],
[
    AC_CACHE_CHECK([if python $1 is installed],
                   [nl_cv_python_has_module_$1],
                   [
                       if ! ${PYTHON} -c "import $1" > /dev/null 2>&1; then
                           nl_cv_python_has_module_$1="no"
                       else
                           nl_cv_python_has_module_$1="yes"
                       fi
                   ])

    if test "${nl_cv_python_has_module_$1}" = "no"; then
        AC_MSG_ERROR([python $1 module is not installed, please install $1.
Please follow the instructions at $2.])
    fi
])
