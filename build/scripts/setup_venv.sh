#!/bin/bash -e

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
#      This file is a script that will retrieve and set up the
#      Python virtual environment required to sandbox the Python
#      modules required by the Weave Data Language (WDL) Compiler
#      (WDLC), wdlc.
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
        echo "OpenWeave Weave Data Language (WDL) Compiler (WDLC) Python setup."
        echo ""
        echo "Options:"
        echo ""
        echo "  -h, --help              Print this help, then exit."
        echo "  -o, --output DIR        Generate set up to the output directory DIR."
        echo "  --python PYTHON         Use the PYTHON python executable (default: ${PYTHON})."
        echo "  -q, --quiet             Work silently; do not display diagnostic and"
        echo "  -r, --requirement FILE  Install from the given requirements file. This option can be used multiple times."
        echo "  -v, --verbose           Work verbosely; increase the level of diagnostic"
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

function create_directory() {
    local directory="${1}"

    if [ ! -d "${directory}" ]; then
        progress "MKDIR" "${directory}"

        mkdir -p "${directory}"
    fi
}

OUTPUTDIR=""
SCRIPTDIR="`dirname ${0}`"
PYTHON="python"
requirement_options=""
requirement_paths=""
verbose=1

# While there are command line options and arguments to parse, parse
# and consume them.

while [ "${#}" -gt 0 ]; do

    case ${1} in

        -h | --help)
            usage 0
            ;;

        -o | --output)
            OUTPUTDIR="${2}"
            shift 2
            ;;

        --python)
            PYTHON=`which ${2} 2> /dev/null`
            shift 2
            ;;

        -q | --quiet)
            verbose=0
            shift 1
            ;;

        -r | --requirement)
            # Accumulate requirement paths by appending (preserving
            # order priority) subsequent paths as a space- delimited
            # list.

            requirement_paths="${requirement_paths}${requirement_paths:+ }${2}"
            requirement_options="${requirement_options}${requirement_options:+ }${1} ${2}"
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

venv_path="${OUTPUTDIR}/venv"

create_directory "${venv_path}"

"${SCRIPTDIR}/install_python_modules.sh" --python "${PYTHON}" --output "${venv_path}" ${requirement_options} --python "${PYTHON}"

if [ ${?} -ne 0 ]; then
    echo "Could not install Python modules specified in ${requirements_paths} to ${OUTPUTDIR}" >&2

    exit 1
fi
