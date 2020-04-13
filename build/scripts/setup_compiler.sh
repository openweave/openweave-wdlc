#!/usr/bin/env bash

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

##
#    @file
#      This file is the setup script for the Weave Data Language (WDL)
#      Compiler (WDLC), wdlc.
#

#
# usage
#
# Display program usage.
#
function usage() {
    local name=`basename ${0}`

    echo "Usage: `basename ${0}` -o <output directory>"

    if [ ${1} -ne 0 ]; then
        echo "Try '${name} -h' for more information."
    fi

    if [ ${1} -ne 1 ]; then
        echo "OpenWeave Weave Data Language (WDL) Compiler (WDLC) setup"
        echo ""
        echo "Options:"
        echo ""
        echo "  --bindir DIR                Set the executable directory to DIR, relative to the output directory."
        echo "  --datadir DIR               Set the read-only data directory to DIR, relative to the output directory."
        echo "  -h, --help                  Print this help, then exit."
        echo "  --includedir DIR            Set the header directory to DIR, relative to the output directory."
        echo "  --libdir DIR                Set the library directory to DIR, relative to the output directory."
        echo "  --srcdir DIR                Find the package sources in DIR (default: ${PWD})."
        echo "  -o, --output DIR            Generate set up to the output directory DIR."
        echo "  --protoc PROTOC             Use the PROTOC protoc executable (default: ${PROTOC})."
        echo "  --python PYTHON             Use the PYTHON python executable (default: ${PYTHON})."
        echo "  -q, --quiet                 Work silently; do not display diagnostic and"
        echo "  -r, --requirement FILE      Install from the given Python PIP requirements file. This option can be used multiple times."
        echo "  -l, --local-packages DIR    Install Python packages from DIR instead of downloading them from the internet."
        echo "  -v, --verbose               Work verbosely; increase the level of diagnostic"
    fi

    exit ${1}
}

#
# progress <ACTION> <target>
#
# Display to standard output the specified action (capitalized by
# convention) and target arguments.
#
function progress() {
    printf "  %-13s %s\n" "${1}" "${2}"
}

function check_dir_option() {
    local variable="${1}"
    local value="${!variable}"
    local option="${2}"

    if [ -z "${value}" ]; then
        echo "error: the ${option} option must be set."

        exit 1
    fi
}

function create_directory() {
    local directory="${1}"

    if [ ! -d "${directory}" ]; then
        progress "MKDIR" "${directory}"

        mkdir -p "${directory}"
    fi
}

OUTPUTDIR=""
SCRIPTDIR="`dirname ${0}`"
PROTOC="protoc"
PYTHON="python"
verbose=1
wdlc_bindir=""
wdlc_datadir=""
wdlc_libdir=""
wdlc_includedir=""
wdlc_srcdir="${PWD}"
local_packages_dir=""

# While there are command line options and arguments to parse, parse
# and consume them.

while [ "${#}" -gt 0 ]; do

    case ${1} in

        --bindir)
            wdlc_bindir="${2}"
            shift 2
            ;;

        --datadir)
            wdlc_datadir="${2}"
            shift 2
            ;;

        --includedir)
            wdlc_includedir="${2}"
            shift 2
            ;;

        --libdir)
            wdlc_libdir="${2}"
            shift 2
            ;;

        -h | --help)
            usage 0
            ;;

        -o | --output)
            OUTPUTDIR="${2}"
            shift 2
            ;;

        --protoc)
            PROTOC="${2}"
            shift 2
            ;;

        --python)
            PYTHON="${2}"
            shift 2
            ;;

        -q | --quiet)
            verbose=0
            shift 1
            ;;

        -l | --local-packages)
            local_packages_dir="${2}"
            shift 2
            ;; 

        -r | --requirement)
            # Accumulate Python PIP requirement paths by appending
            # (preserving order priority) subsequent paths as a space-
            # delimited list.

            requirement_paths="${requirement_paths}${requirement_paths:+ }${2}"
            requirement_options="${requirement_options}${requirement_options:+ }${1} ${2}"
            shift 2
            ;;

        --srcdir)
            wdlc_srcdir="${2}"
            shift 2
            ;;

        -v | --verbose)
            ((verbose += 1))
            shift 1
            ;;

        -*)
            echo "Unknown or invalid option: '${1}'"
            usage 1
            ;;

    esac

done

# If no output directory has been specified, it is a usage invocation
# error: display usage with error status.
#
# Similarly, if the output directory has been specified but does not
# exist, it is an outright error.

if [ -z "${OUTPUTDIR}" ]; then
    usage 1
elif [ ! -d "${OUTPUTDIR}" ]; then
    echo "The required output directory '${OUTPUTDIR}' does not exist." >&2

    exit 1
fi

# If the various directory options have not been specified, it is an
# outright error.

check_dir_option wdlc_bindir     --bindir
check_dir_option wdlc_datadir    --datadir
check_dir_option wdlc_includedir --includedir
check_dir_option wdlc_libdir     --libdir
check_dir_option wdlc_srcdir     --srcdir

# Concatenate the provided skeleton relative directories with the
# specified output directory.

wdlc_bindir="${OUTPUTDIR}/${wdlc_bindir}"
wdlc_datadir="${OUTPUTDIR}/${wdlc_datadir}"
wdlc_includedir="${OUTPUTDIR}/${wdlc_includedir}"
wdlc_libdir="${OUTPUTDIR}/${wdlc_libdir}"

create_directory "${wdlc_includedir}"

cp -rf ${wdlc_srcdir}/third_party/googleapis/repo/google "${wdlc_includedir}/"
cp -rf ${wdlc_srcdir}/wdl                                "${wdlc_includedir}/"
cp -rf ${wdlc_srcdir}/weave                              "${wdlc_includedir}/"
cp -rf ${wdlc_srcdir}/test/schema/*                      "${wdlc_includedir}/"

# At this point, in the case of a read-only source directory and a
# strict test environment like 'make distcheck', a number of directories
# above were just copied from read-only source locations. Consequently,
# the move attempt, the Python code generation, and Python package directory
# marking below will all fail unless we modify the directory permissions
# appropriately prior to those operations.

find "${wdlc_includedir}/" -type d -exec chmod 775 {} \;

# The wdlc compiler backend is all Python-driven. Code-generate Python
# source for the core wdlc WDL schema library.

progress "PROTOC" "${wdlc_includedir}/..."
${PROTOC} --proto_path "${wdlc_includedir}" --python_out="${wdlc_includedir}" $(find "${wdlc_includedir}" -type f -name "*.proto")

if [ ${?} -ne 0 ]; then
    echo "Could not generate the WDL library for the wdlc backend." >&2

    exit 1
fi

# Mark directories containing the code-generated Python source as
# Python package directories such that they can be imported as
# modules.

find "${wdlc_includedir}" -type d -exec touch {}/__init__.py \;

create_directory "${wdlc_libdir}"

# Copy over the compiler backend, except the Python trampoline script,
# setup.sh. This will be handled outside of this script.

cp -f  ${wdlc_srcdir}/backend/docs_compile.csh             "${wdlc_libdir}"
cp -f  ${wdlc_srcdir}/backend/gwvc                         "${wdlc_libdir}"
cp -Rf ${wdlc_srcdir}/backend/lib                          "${wdlc_libdir}"
cp -f  ${wdlc_srcdir}/backend/pylint.sh                    "${wdlc_libdir}"
cp -f  ${wdlc_srcdir}/backend/README.md                    "${wdlc_libdir}"
cp -f  ${wdlc_srcdir}/backend/schema_tests                 "${wdlc_libdir}"
cp -f  ${wdlc_srcdir}/backend/wdl_plugin                   "${wdlc_libdir}"

# At this point, in the case of a read-only source directory and a
# strict test environment like 'make distcheck', a number of
# directories and files above were just copied from read-only source
# locations. Any subsequent uninstall will fail unless we modify the
# directory permissions appropriately prior to those operations.

find "${wdlc_libdir}/" -type d -exec chmod 775 {} \;

create_directory "${wdlc_datadir}"

progress "SETUP" "python"
"${SCRIPTDIR}/setup_venv.sh" --output "${wdlc_datadir}" --python "${PYTHON}" ${requirement_options} --local-packages "${local_packages_dir}"

if [ ${?} -ne 0 ]; then
    echo "Could not set up Python for the wdlc backend." >&2

    exit 1
fi

# At this point, the wdlc backend infrastructure should be
# complete. Sanity check the results.

progress "PYTHON" "unittest ${OUTPUTDIR}/..."
WDLCROOT=$(pwd)/${OUTPUTDIR} ./${wdlc_libdir}/schema_tests

if [ ${?} -ne 0 ]; then
    echo "Could not validate the wdlc build results."

    exit 1
fi
