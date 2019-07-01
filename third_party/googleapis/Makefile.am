#
#    Copyright (c) 2019 Google LLC. All rights reserved.
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
#    Description:
#      This file is the GNU automake template for the googleapis
#      protobuf definitions used by the Weave Data Language (WDL)
#      Compiler (WDLC).
#
#      These are snapshot according to the commit in
#      README.third_party using the update_googleapis.sh script in the
#      project build script directory.
#

include $(abs_top_nlbuild_autotools_dir)/automake/pre.am

EXTRA_DIST                                 = \
    README.third_party                       \
    repo/LICENSE                             \
    repo/google                              \
    repo/google/api                          \
    repo/google/api/annotations.proto        \
    repo/google/api/http.proto               \
    repo/google/longrunning                  \
    repo/google/longrunning/operations.proto \
    repo/google/rpc                          \
    repo/google/rpc/code.proto               \
    repo/google/rpc/error_details.proto      \
    repo/google/rpc/status.proto             \
    repo/google/type                         \
    repo/google/type/color.proto             \
    repo/google/type/date.proto              \
    repo/google/type/dayofweek.proto         \
    repo/google/type/latlng.proto            \
    repo/google/type/money.proto             \
    repo/google/type/timeofday.proto         \
    $(NULL)

include $(abs_top_nlbuild_autotools_dir)/automake/post.am
