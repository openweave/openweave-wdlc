
# Process this file with autoconf to produce a configure script.

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
#      This file is the GNU autoconf input source file for
#      Weave Data Language (WDL) Compiler (WDLC).
#

#
# Declare autoconf version requirements
#
AC_PREREQ([2.68])

#
# Initialize autoconf for the package
#
AC_INIT([openweave-wdlc],
        m4_esyscmd([third_party/nlbuild-autotools/repo/scripts/mkversion -b `cat .default-version` .]),
        [openweave-users@googlegroups.com],
        [openweave-wdlc],
        [http://openweave.io/])

# Tell the rest of the build system the absolute path where the
# nlbuild-autotools repository is rooted at.

AC_SUBST(nlbuild_autotools_stem,[third_party/nlbuild-autotools/repo])
AC_SUBST(abs_top_nlbuild_autotools_dir,[\${abs_top_srcdir}/\${nlbuild_autotools_stem}])

#
# Check the sanity of the source directory by checking for the
# presence of a key watch file
#
AC_CONFIG_SRCDIR([wdlc.sh.in])

#
# Tell autoconf where to find auxilliary build tools (e.g. config.guess,
# install-sh, missing, etc.)
#
AC_CONFIG_AUX_DIR([third_party/nlbuild-autotools/repo/third_party/autoconf])

#
# Tell autoconf where to find auxilliary M4 macros
#
AC_CONFIG_MACRO_DIRS([build/autoconf/m4 third_party/nlbuild-autotools/repo/third_party/autoconf/m4 third_party/nlbuild-autotools/repo/autoconf/m4])

#
# Tell autoconf what file the package is using to aggregate C preprocessor
# defines.
#
# This is not strictly required for this package at present; however,
# the bootstrap infrastructure runs autoheader and, for now,
# autoheader expects this, even if it is not used.
#
AC_CONFIG_HEADERS([include/wdlc-config.h])

#
# Figure out what the canonical build, host and target tuples are.
#
AC_CANONICAL_BUILD
AC_CANONICAL_HOST
AC_CANONICAL_TARGET

#
# Mac OS X / Darwin ends up putting some versioning cruft on the end of its
# tuple that we don't care about in this script. Create "clean" variables
# devoid of it.
#

NL_FILTERED_CANONICAL_BUILD
NL_FILTERED_CANONICAL_HOST
NL_FILTERED_CANONICAL_TARGET

#
# Configure automake with the desired options, indicating that this is not
# a native GNU package, that we want "silent" build rules, and that we want
# objects built in the same subdirectory as their source rather than collapsed
# together at the top-level directory.
#
# Disable silent build rules by either passing --disable-silent-rules to
# configure or passing V=1 to make
#
AM_INIT_AUTOMAKE([1.14 foreign silent-rules subdir-objects tar-pax])

#
# Silent build rules requires at least automake-1.11. Employ
# techniques for not breaking earlier versions of automake.
#
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])
AM_SILENT_RULES([yes])

#
# Enable maintainer mode to prevent the package from constantly trying
# to rebuild configure, Makefile.in, etc. Rebuilding such files rarely,
# if ever, needs to be done "in the field".
#
# Use the included 'bootstrap' script instead when necessary.
#
AM_MAINTAINER_MODE

#
# Checks for build host programs
#

# Check for other host tools.

AC_PROG_INSTALL
AC_PROG_LN_S

NL_PATH_PROG(DIFF, diff, [diff is required for wdlc unit tests])
NL_PATH_PROG(SED, sed, [sed is required to build wdlc])

# Both the Google Protocol Buffers (protobuf) Compiler (protoc) and
# the Python interpretter are required for WDLC.
#
# Check that they exist and are of the appropriate version and meet
# other minimum requirements.

#
# Python
#

# We have validated that Python 2.7 seems to work suitably with
# WDLC. However, there are, at present, portability issues with some
# of the Python infrastructure in the WDLC backend that preclude the
# use of Python 3. Ensure that the Python requested is within that
# version range, inclusive.

nl_python_major_minor_version_min="2.7"
nl_python_major_minor_version_max="2.7"

# Provide some documentation in 'configure --help' that informs the
# user that 'PYTHON=<python executable> configure' or 'configure
# PYTHON=<python executable' will work to specify precisely which
# python executable to use.

AC_ARG_VAR(PYTHON, [Python executable])
AC_ARG_VAR(WDLC_PYTHON_LOCAL_PACKAGE_DIR, [Pip local packages dir])

# Check whether 'python' exists in the current PATH, and if it does,
# set PYTHON to the fully-qualified, absolute path for it. If the user
# has already set PYTHON, either by 'PYTHON=<python executable>
# configure' or 'configure PYTHON=<python executable>', then this
# check is does nothing.

AC_PATH_PROG(PYTHON, python)

# Check the configure cache and, failing that, check the python
# executable for what version it claims to be, saving the result in
# the cache for faster, future reconfiguration runs.

AC_CACHE_CHECK([${PYTHON} version],
	       nl_cv_python_version,
               [
                   nl_cv_python_version=`${PYTHON} --version 2>&1 | ${SED} -n -e 's/^.\{1,\}\([[0-9]]\{1,\}.[[0-9]]\{1,\}.[[0-9]]\{1,\}\)$/\1/gp'`

                   if test "${nl_cv_python_version}" = "" ; then
                       nl_cv_python_version="unknown"
                   fi
               ])

# Check the configure cache and, failing that, check directly whether
# the reported python version is greater than or equal to the minimum,
# using a clever sed and sort trick to indicate 'yes' or 'no'.

AC_CACHE_CHECK([${PYTHON} version is at least ${nl_python_major_minor_version_min}],
               nl_cv_python_version_at_least_major_minor,
               [
                   nl_python_major_minor_version=`echo ${nl_cv_python_version} | ${SED} -n -e 's/^\([[0-9]]\{1,\}.[[0-9]]\{1,\}\).[[0-9]]\{1,\}$/\1/gp'`

                   nl_cv_python_version_at_least_major_minor=`printf "${nl_python_major_minor_version_min}\n${nl_python_major_minor_version}\n" | ${SED} 's/^ *//' | sort | ${SED} "s/${nl_python_major_minor_version_min}/yes/ ; s/${nl_python_major_minor_version}/no/ ; 1q"`
               ])

# Check the configure cache and, failing that, check directly whether
# the reported python version is lesser than or equal to the maximum,
# using a clever sed and sort trick to indicate 'yes' or 'no'.

AC_CACHE_CHECK([${PYTHON} version is at most ${nl_python_major_minor_version_max}],
               nl_cv_python_version_at_most_major_minor,
               [
                   nl_python_major_minor_version=`echo ${nl_cv_python_version} | ${SED} -n -e 's/^\([[0-9]]\{1,\}.[[0-9]]\{1,\}\).[[0-9]]\{1,\}$/\1/gp'`

                   nl_cv_python_version_at_most_major_minor=`printf "${nl_python_major_minor_version}\n${nl_python_major_minor_version_max}\n" | ${SED} 's/^ *//' | sort | ${SED} "s/${nl_python_major_minor_version}/yes/ ; s/${nl_python_major_minor_version_max}/no/ ; 1q"`
               ])

# If the version of python that the user specified is out of the
# allowed range, then fail out with an error message.

if test "${nl_cv_python_version_at_least_major_minor}" = "no" || test "${nl_cv_python_version_at_most_major_minor}" = "no"; then
    if test "${nl_python_major_minor_version_min}" = "${nl_python_major_minor_version_max}"; then
        msg="${nl_python_major_minor_version_min}"
    else
        msg="later than or equal to ${nl_python_major_minor_version_min} or earlier than or equal to ${nl_python_major_minor_version_max}"
    fi

    AC_MSG_ERROR([Python version ${msg} is required. However, ${PYTHON} is version ${nl_cv_python_version}.])
fi

# Emit the python version detected as PYTHON_VERSION in makefiles.

AC_SUBST(PYTHON_VERSION, ${nl_cv_python_version})

# Check whether Python PIP is installed.

NL_CHECK_PYTHON_MODULE([pip],
                       [https://pip.pypa.io/en/stable/installing/ and https://docs.python.org/2/library/ensurepip.html])

# Check whether Python Virtual Environment is installed.

NL_CHECK_PYTHON_MODULE([virtualenv],
                       [https://virtualenv.pypa.io/en/stable/installation])

#
# Google Protocol Buffers (protobuf) Compiler (protoc)
#

# We have validated that protoc 3.3.0 through 3.7.1 seems to work
# suitably with WDLC. Ensure that the protoc requested is within that
# version range, inclusive.

nl_protoc_version_min="3.3.0"
nl_protoc_version_max="3.7.1"

# Provide some documentation in 'configure --help' that informs the
# user that 'PROTOC=<protoc executable> configure' or 'configure
# PROTOC=<protoc executable>' will work to specify precisely which
# protoc executable to use.

AC_ARG_VAR(PROTOC, [Google Protocol Buffers (protobuf) Compiler (protoc) executable])
AC_ARG_VAR(PROTOC_INCLUDES, [Google Protocol Buffers (protobuf) Compiler (protoc) header directory])

# Check whether 'protoc' exists in the current PATH, and if it does,
# set PROTOC to the fully-qualified, absolute path for it. If the user
# has already set PROTOC, either by 'PROTOC=<protoc executable>
# configure' or 'configure PROTOC=<protoc executable>', then this
# check is does nothing.

AC_PATH_PROG(PROTOC, protoc)

# If we have a non-empty value for PROTOC, then proceed with version
# validation. Otherwise, skip out to the error and action
# recommendation path.

if test "${PROTOC}" != ""; then
    nl_have_PROTOC="yes"

    # Check the configure cache and, failing that, check the protoc
    # executable for what version it claims to be, saving the result in
    # the cache for faster, future reconfiguration runs.

    AC_CACHE_CHECK([${PROTOC} version],
		   nl_cv_protoc_version,
		   [
		       nl_cv_protoc_version=`${PROTOC} --version 2>&1 | ${SED} -n -E -e 's/^[[^0-9]]*(([[0-9]]+\.)*[[0-9]]+).*/\1/p'`

		       if test "${nl_cv_protoc_version}" = "" ; then
			   nl_cv_protoc_version="unknown"
		       fi
		   ])

    # Check the configure cache and, failing that, check directly whether
    # the reported protoc version is greater than or equal to the minimum,
    # using a clever sed and sort trick to indicate 'yes' or 'no'.

    AC_CACHE_CHECK([${PROTOC} version is at least ${nl_protoc_version_min}],
		   nl_cv_protoc_version_at_least_major_minor_patch,
		   [
		       nl_cv_protoc_version_at_least_major_minor_patch=`printf "${nl_protoc_version_min}\n${nl_cv_protoc_version}\n" | ${SED} 's/^ *//' | sort | ${SED} "s/${nl_protoc_version_min}/yes/ ; s/${nl_cv_protoc_version}/no/ ; 1q"`
		   ])

    # Check the configure cache and, failing that, check directly whether
    # the reported protoc version is lesser than or equal to the maximum,
    # using a clever sed and sort trick to indicate 'yes' or 'no'.

    AC_CACHE_CHECK([${PROTOC} version is at most ${nl_protoc_version_max}],
		   nl_cv_protoc_version_at_most_major_minor_patch,
		   [
		       nl_cv_protoc_version_at_most_major_minor_patch=`printf "${nl_cv_protoc_version}\n${nl_protoc_version_max}\n" | ${SED} 's/^ *//' | sort | ${SED} "s/${nl_cv_protoc_version}/yes/ ; s/${nl_protoc_version_max}/no/ ; 1q"`
		   ])

else
    nl_have_PROTOC="no"

fi

# If protoc cannot be found or if the version of protoc that the user
# specified is out of the allowed range, then set an appropriate error
# to be used below.

if test "${nl_have_PROTOC}" = "no"; then
    nl_protoc_error="protoc cannot be found in PATH"

elif test "${nl_cv_protoc_version_at_least_major_minor_patch}" = "no" || test "${nl_cv_protoc_version_at_most_major_minor_patch}" = "no"; then
    nl_protoc_error="${PROTOC} is version ${nl_cv_protoc_version}"

else
    nl_protoc_error=

fi

# If a protoc probing error has been set, provide the users with an
# actionable URL to fetch that will provide them with, at least, the
# minimum allowed version of protoc.

if test "${nl_protoc_error}" != ""; then

    github_stem="https://github.com/protocolbuffers/protobuf/releases/download/v${nl_protoc_version_min}"

    case "${nl_filtered_target}" in

    i?86-*-darwin)
        action=" "
        github_file=protoc-${nl_protoc_version_min}-osx-x86_32.zip
        ;;

    x86_64-*-darwin)
        action=" "
        github_file=protoc-${nl_protoc_version_min}-osx-x86_64.zip
        ;;

    i?86-*-linux*)
        action=" "
        github_file=protoc-${nl_protoc_version_min}-linux-x86_32.zip
        ;;

    x86_64-*-linux*)
        action=" "
        github_file=protoc-${nl_protoc_version_min}-linux-x86_64.zip
        ;;

    *)
        action=", building, "
        github_file=protobuf-all-${nl_protoc_version_min}.tar.gz
        ;;

    esac

    github_url="${github_stem}/${github_file}"

    # Generate the actual error message giving the user actionable
    # feedback on what they need to do to get a sufficient version of
    # protoc.

    AC_MSG_ERROR([protobuf version between ${nl_protoc_version_min} and ${nl_protoc_version_max}, inclusive, is required. However, ${nl_protoc_error}.
Please try downloading${action}and installing '${github_url}' or later.])
fi

# At this point, we have a valid version of protoc. We next need to
# figure out where it sources its header files from.
#
# Check the configure cache and, failing that, check directly for the
# location where protoc sources its headers from, respecting PROTOC_INCLUDES
# if the user specified it.

# Effect a Python-based workalike equavalent to GNU readlink -f, which
# will not exist on pure POSIX or BSD sytems like Darwin / Mac OS X.

readlink_f() {
    ${PYTHON} -c "import os,sys; print(os.path.expanduser(os.path.realpath(sys.argv[[1]])))" "${1}"
}

# Ultimately, we want to resolve the real location of protoc (hence
# the 'readlink_f' below), no matter what symbolic link to it might
# exist, such that we can intuit the location of its header
# directory. When protoc is a symbolic link, either relative or
# absolute, the header directory likely will not share the same
# directory stem as the symbolic link.

AC_CACHE_CHECK([where ${PROTOC} sources its headers from],
	       nl_cv_protoc_includes,
	       [
                   if test "${PROTOC_INCLUDES}" != ""; then
                       nl_maybe_protoc_includes="${PROTOC_INCLUDES}"

                   else
                       protoc_dirname=`dirname $(readlink_f "${PROTOC}")`
                       nl_maybe_protoc_includes="${protoc_dirname}/../include"

                   fi

                   path_to_match=google/protobuf/descriptor.proto

                   if test -f "${nl_maybe_protoc_includes}/${path_to_match}"; then
                       nl_cv_protoc_includes="`echo ${nl_maybe_protoc_includes} | ${SED} -e 's,[[^/]]*/\.\.,,g' -e 's,\/*$,,g' -e 's,\([[^/]]\)\/\/\([[^/]]\),\1/\2,g'`"

                   else
                       AC_MSG_ERROR([could not find '${path_to_match}' in '${nl_maybe_protoc_includes}'. Please specify PROTOC_INCLUDES at a working protoc header directory; otherwise, your protoc installation maybe invalid or incomplete.])

                   fi
	       ])

# Emit the protoc version detected as PROTOC_VERSION in makefiles.

AC_SUBST(PROTOC_VERSION, ${nl_cv_protoc_version})

# Emit the protoc header file directory as PROTOC_INCLUDES in makefiles.

AC_SUBST(PROTOC_INCLUDES, ${nl_cv_protoc_includes})

#
# Tests
#
AC_MSG_CHECKING([whether to build tests])

# Tests



AM_CONDITIONAL([WDLC_BUILD_TESTS], [test "${nl_cv_build_tests}" = "yes"])

#
# Identify the various makefiles and auto-generated files for the package
#
AC_CONFIG_FILES([
Makefile
include/Makefile
backend/Makefile
codegen/Makefile
codegen/weave-device-cpp/Makefile
test/Makefile
third_party/Makefile
third_party/googleapis/Makefile
])

#
# Generate the auto-generated files for the package
#
AC_OUTPUT

#
# Summarize the package configuration
#

AC_MSG_NOTICE([

  Configuration Summary
  ---------------------
  Package                                   : ${PACKAGE_NAME}
  Version                                   : ${PACKAGE_VERSION}
  Build system                              : ${nl_filtered_build}
  Host system                               : ${nl_filtered_host}
  Target system                             : ${nl_filtered_target}
  Target architecture                       : ${nl_filtered_target_cpu}
  Target OS                                 : ${nl_filtered_target_os}
  Build tests                               : ${nl_cv_build_tests}
  Protoc                                    : ${PROTOC:--}
  Protoc version                            : ${nl_cv_protoc_version:--}
  Protoc headers                            : ${PROTOC_INCLUDES:--}
  Python                                    : ${PYTHON:--}
  Python version                            : ${nl_cv_python_version:--}
  Prefix                                    : ${prefix}

])
