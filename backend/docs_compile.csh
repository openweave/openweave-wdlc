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
#      This file is a front-end wrapper around the Google Protocol
#      Buffers (protobuf) Compiler (protoc) and the protoc-gen-doc
#      plug-in for extracting and documentation from Weave Data
#      Language (WDL) schema.
#

#

# Requires doxygen generator found here https://github.com/estan/protoc-gen-doc
mkdir -p ../../platform/doc
find ../../schema/src/ -name "*.proto" | xargs protoc -I../../schema/src/ --doc_out=html,index.html:../../platform/doc
