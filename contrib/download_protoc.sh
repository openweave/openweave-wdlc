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
#     	Script to help download a minimum-viable version of Google
#       Protocol Buffers (protobuf) compiler, protoc.
#

dest_dir="/usr/local"

function usage() {
    local name=`basename ${0}`

    if [ ${1} -ne 0 ]; then
        echo "Try '${name} -h' for more information."
    fi

    if [ ${1} -ne 1 ]; then
        echo "OpenWeave Weave Data Language (WDL) Compiler - Protoc Installation Script"
        echo ""
        echo "Options:"
        echo ""
        echo "  -h, --help         Print this help, then exit."
        echo "  -f, --force        Over-ride the local installation of protoc regardless of version"
        echo "  -d, --destdir DIR  Over-ride the destination directory (default: ${dest_dir})"
    fi

    exit ${1}
}

force_install=false

# While there are command line options and arguments to parse, parse
# and consume them.

while [ "${#}" -gt 0 ]; do

    case ${1} in

        -h | --help)
            usage 0
            ;;

        
        -f | --force)
            force_install=true
            shift 1
            ;;

        -d | --destdir)
            dest_dir="${2}"
            shift 2
            ;;

        -*)
            echo "Unknown or invalid option: '${1}'"
            usage 1
            ;;

    esac

done

#
# progress <ACTION> <target>
#
# Display to standard output the specified action (capitalized by
# convention) and target arguments.
#
function progress() {
    printf "  %-13s %s\n" "${1}" "${2}"
}

# If the destination directory doesn't exist, error out.
if [ ! -d "${dest_dir}" ]; then
    usage 1
fi

protoc_version_min="3.5.1"
protoc_version_max="3.7.1"
VERSION="3.7.1"

if [ -f "${dest_dir}/bin/protoc" ]; then
    protoc_version=`${dest_dir}/bin/protoc --version 2>&1 | sed -n -e 's/^.\{1,\}\([0-9]\{1,\}.[0-9]\{1,\}.[0-9]\{1,\}\)$/\1/gp'`

    protoc_at_least_major_minor_patch=`printf "${protoc_version_min}\n${protoc_version}\n" | sed 's/^ *//' | sort | sed "s/${protoc_version_min}/yes/ ; s/${protoc_version}/no/ ; 1q"`
    protoc_at_most_major_minor_patch=`printf "${protoc_version}\n${protoc_version_max}\n" | sed 's/^ *//' | sort | sed "s/${protoc_version}/yes/ ; s/${protoc_version_max}/no/ ; 1q"`

    if [[ "${protoc_at_most_major_minor_patch}" = "yes" && "${protoc_at_least_major_minor_patch}" = "yes" ]]; then
        version_in_range=true
    else
        version_in_range=false
    fi

    if [ "${force_install}" = false ]; then
        if [ "${version_in_range}" = true ]; then
            echo "Existing installation of version ${protoc_version} already meets the min and max requirements - nothing else to be done!"
            exit 0
        else
           echo "Error: Existing installation present but no --force option provided, so exiting without doing anything"
           exit 1
        fi
   else
       echo "**WARNING** Existing installation found - over-riding..."

       # Remove the existing installation
       rm ${dest_dir}/bin/protoc
       rm -rf ${dest_dir}/include/google/protobuf
   fi 
fi

# Figure out the platform we're running on, and deduce the appropriate platform prefix for the download image.
if [[ "$(uname -s)" == "Linux" ]]; then
    platform="linux-x86_64"
elif [[ "$(uname -s)" == "Darwin" ]]; then
    platform="osx-x86_64"
else
    echo "Error: Unknown OS: Please run on a Linux or Darwin system, or manually download the relevant image"
    echo "from https://github.com/google/protobuf/releases/tag/v${VERSION}"
    exit 1
fi

filename="protoc-${VERSION}-${platform}.zip"
github_url="https://github.com/google/protobuf/releases/download/v${VERSION}/${filename}"

echo ${github_url}

if ! (curl -L --fail "${github_url}" > "${dest_dir}/temp.zip"); then
    >&2 echo "Error: Unable to reach github, cannot download protoc"
    exit 1
fi

unzip -o -q "${dest_dir}/temp.zip" -d "${dest_dir}"
rm "${dest_dir}/temp.zip"
