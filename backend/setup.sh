#!/bin/bash -e

#
#    Copyright (c) 2019 Google LLC.
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
#      This file is the setup trampoline to ensure the Python virtual
#      environment is in place prior to invoking the Weave Data
#      Language (WDL) Compiler (WDLC), wdlc, backend.
#

wdlc_datadir="${WDLCROOT}/@WDLC_DATADIR@"
wdlc_includedir="${WDLCROOT}/@WDLC_INCLUDEDIR@"

source "${wdlc_datadir}/venv/bin/activate"

export PYTHONPATH="${wdlc_includedir}:${PYTHONPATH}"

# Linux uses the c++ implementation of protobuf and Mac uses the python
# implementation of protobuf by default. There is a bug in the c++
# implementation of protobuf. This forces Linux to use the python
# implementation.

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Exit if sourced; show message if run as a script
set +e
return 2>/dev/null
echo "Setup complete. To configure your shell for development, run:"
echo "$ source $0"
