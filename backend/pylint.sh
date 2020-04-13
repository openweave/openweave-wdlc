#!/bin/bash -e

#
#    Copyright (c) 2019-2020 Google LLC.
#    Copyright (c) 2016-2018 Nest Labs, Inc.
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

##
#    @file
#      This file effects a pylint linter wrapper, using either gpylint
#      or pylint, that will lint the Weave Data Language (WDL)
#      Compiler (WDLC) backend Python implementation files.
#

OS=$(uname -s)

if [ "$OS" == 'Darwin' ]; then
    TOOLS_DIR="$(cd -P -- "$(dirname -- "$0")" && pwd -P)"
else
    TOOLS_DIR=$(dirname $(readlink -f "$0"))
fi

# gpylint is a Google specific version of pylint which is a little pickier
# than the default pylint.
PYLINT=$(which gpylint)
if [ "${PYLINT}" == "" ]; then
  # External contributors won't have it, so fall back to the less picky pylint.
  PYLINT=$(which pylint)
fi

if [ "${PYLINT}" == "" ]; then
  echo "Unable to find gpylint or pylint."
  exit 1
fi

# These files are skipped for now.  Backup files and the generated gwv_pb2.py
# file will always be skipped.  The rest will either go away when schema2 is
# done or be updated in future CLs.
PYLINT_FILES=$(find ${TOOLS_DIR} \
  -name '*.py' \
  ! -name '.*' \
  ! -name schema.py \
  ! -name json_generator.py)

${PYLINT} ${PYLINT_FILES}
