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
#      This file fetches proto files from googleapis repos on github
#      that are used by wdlc.
#

#
# usage <exit status>
#
# Display program usage.
#
function usage() {
    local name=`basename ${0}`

    echo "Usage: `basename ${0}` [ options ] [ -b BRANCH | -c COMMIT ] -o <output directory>"

    if [ ${1} -ne 0 ]; then
        echo "Try '${name} -h' for more information."
    fi

    if [ ${1} -ne 1 ]; then
        echo "Options:"
        echo ""
        echo "  -b, --branch BRANCH     Fetch files from the head of branch BRANCH."
        echo "  -c, --commit COMMIT     Fetch files from commit COMMIT."
        echo "  -o, --output DIR        Fetch files to the output directory DIR."
        echo "  -q, --quiet             Work silently; do not display diagnostic and"
        echo "  -v, --verbose           Work verbosely; increase the level of diagnostic"
    fi

    exit ${1}
}

#
# error_on_exclusive_options <first option> <second option>
#
# Displays a message to standard output indicating that the specified
# option arguments are mutually- exclusive and that one or the other
# should be chosen. The program then exits with error status.
#
function error_on_exclusive_options() {
    local first_option="${1}"
    local second_option="${2}"

    echo "The ${first_option} and ${second_option} options are mutually-exclusive. Please pick one or the other." >&2

    exit 1
}

#
# error <...>
#
# Display to standard error the specified arguments
#
function error() {
    echo "${*}" >&2
}

#
# verbose <...>
#
# Display to standard error the specified arguments
#
function verbose() {
    echo "${*}" >&2
}

#
# fetch_url_with_command <fetchdir> <url> <command ...>
#
# Attempt to fetch the specified URL to the provided directory with
# the provided command.
#
function fetch_url_with_command() {
    local fetchdir="${1}"
    local url="${2}"
    local executable="`which ${3}`"
    local curdir="`pwd`"
    local status=1

    shift 2
    
    if [ -x "${executable}" ]; then
        cd "${fetchdir}"
        
            verbose "  `echo ${1} | tr '[[:lower:]]' '[[:upper:]]'`     ${url}"

            ${*} "${url}"

            status=${?}

            if [ ${status} -ne 0 ]; then
                    error "Failed to fetch ${url} with ${1}."
            fi

        cd "${curdir}"
    fi
    
    return ${status}
}

#
# fetch_url <fetchdir> <url> <local path>
#
# Attempt to fetch the specified URL to the provided directory with curl.
#
function fetch_url() {
    local outputdir="${1}"
    local url="${2}"
    local path="${3}"

    # Try to fetch the package using curl

    fetch_url_with_command "${outputdir}" "${url}" curl --silent --location --fail --create-dirs --output "${path}"
}

function getFileFromGithub {
    local project="${1}"
    local branch_or_commit="${2}"
    local outputdir="${3}"
    local path="${4}"

    fetch_url "${outputdir}" "https://github.com/${project}/raw/${branch_or_commit}/${path}" "${path}"
}

function getFilesFromGithub {
    local project="${1}"
    local branch_or_commit="${2}"
    local outputdir="${3}"

    for file in "${@:4}"; do
        getFileFromGithub "${project}" "${branch_or_commit}" "${outputdir}" "${file}";
    done
}

OUTPUTDIR=""
project=google/googleapis
branch_or_commit=""
branch_or_commit_option=""
googleapis_files=( "LICENSE" "google/api/annotations.proto" "google/api/http.proto" "google/longrunning/operations.proto" "google/rpc/code.proto" "google/rpc/error_details.proto" "google/rpc/status.proto" "google/type/color.proto" "google/type/date.proto" "google/type/dayofweek.proto" "google/type/latlng.proto" "google/type/money.proto" "google/type/timeofday.proto" );
verbose=1

# While there are command line options and arguments to parse, parse
# and consume them.

while [ "${#}" -gt 0 ]; do

    case ${1} in

        -b | --branch)
            if [ -n "${branch_or_commit}" ]; then
                error_on_exclusive_options "${branch_or_commit_option}" "${1}"
            fi
	    branch_or_commit_option=${1}
	    branch_or_commit=${2}
            shift 2
            ;;

        -c | --commit)
            if [ -n "${branch_or_commit}" ]; then
                error_on_exclusive_options "${branch_or_commit_option}" "${1}"
            fi
	    branch_or_commit_option=${1}
	    branch_or_commit=${2}
            shift 2
            ;;

        -h | --help)
            usage 0
            ;;

        -o | --output)
            OUTPUTDIR="${2}"
            shift 2
            ;;

        -q | --quiet)
            verbose=0
            shift 1
            ;;

        -v | --verbose)
            ((verbose += 1))
            shift 1
            ;;

        -*)
            echo "Unknown or invalid option: '${1}'" >&2
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

# If no branch or commit option has been specified, it is a usage
# invocation error: display usage with error status.

if [ -z "${branch_or_commit}" ]; then
   echo "Please specify either a branch or commit to retrieve." >&2

   usage 1
fi

getFilesFromGithub "${project}" "${branch_or_commit}" "${OUTPUTDIR}" "${googleapis_files[@]}"
