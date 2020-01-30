#
#    Copyright (c) 2019-2020 Google LLC. All rights reserved.
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
#      This file is the GNU automake template for Weave Data Language
#      (WDL) Compiler (WDLC) openweave-core C++ code generation.
#

include $(abs_top_nlbuild_autotools_dir)/automake/pre.am

EXTRA_DIST                                                         = \
    .gitignore                                                       \
    reference/google/protobuf/FieldMaskStructSchema.cpp              \
    reference/google/protobuf/FieldMaskStructSchema.h                \
    reference/nest/test/resource/TraitTestResource.h                 \
    reference/nest/test/trait/TestATrait-c.h                         \
    reference/nest/test/trait/TestATrait.cpp                         \
    reference/nest/test/trait/TestATrait.h                           \
    reference/nest/test/trait/TestBTrait-c.h                         \
    reference/nest/test/trait/TestBTrait.cpp                         \
    reference/nest/test/trait/TestBTrait.h                           \
    reference/nest/test/trait/TestCTrait-c.h                         \
    reference/nest/test/trait/TestCTrait.cpp                         \
    reference/nest/test/trait/TestCTrait.h                           \
    reference/nest/test/trait/TestCommon-c.h                         \
    reference/nest/test/trait/TestCommon.cpp                         \
    reference/nest/test/trait/TestCommon.h                           \
    reference/nest/test/trait/TestCommonVersioned-c.h                \
    reference/nest/test/trait/TestCommonVersioned.cpp                \
    reference/nest/test/trait/TestCommonVersioned.h                  \
    reference/nest/test/trait/TestDTrait-c.h                         \
    reference/nest/test/trait/TestDTrait.cpp                         \
    reference/nest/test/trait/TestDTrait.h                           \
    reference/nest/test/trait/TestETrait-c.h                         \
    reference/nest/test/trait/TestETrait.cpp                         \
    reference/nest/test/trait/TestETrait.h                           \
    reference/nest/test/trait/TestFTrait-c.h                         \
    reference/nest/test/trait/TestFTrait.cpp                         \
    reference/nest/test/trait/TestFTrait.h                           \
    reference/nest/test/trait/TestHTrait-c.h                         \
    reference/nest/test/trait/TestHTrait.cpp                         \
    reference/nest/test/trait/TestHTrait.h                           \
    reference/nest/test/trait/TestMismatchedCTrait-c.h               \
    reference/nest/test/trait/TestMismatchedCTrait.cpp               \
    reference/nest/test/trait/TestMismatchedCTrait.h                 \
    reference/wdl/EventImportanceEnum.h                              \
    reference/weave/common/DayOfWeekEnum.h                           \
    reference/weave/common/EventIdStructSchema.cpp                   \
    reference/weave/common/EventIdStructSchema.h                     \
    reference/weave/common/InterfaceNameStructSchema.cpp             \
    reference/weave/common/InterfaceNameStructSchema.h               \
    reference/weave/common/ProfileSpecificStatusCodeStructSchema.cpp \
    reference/weave/common/ProfileSpecificStatusCodeStructSchema.h   \
    reference/weave/common/ResourceTypeEnum.h                        \
    reference/weave/common/TimeOfDayStructSchema.cpp                 \
    reference/weave/common/TimeOfDayStructSchema.h                   \
    reference/weave/common/TimerStructSchema.cpp                     \
    reference/weave/common/TimerStructSchema.h                       \
    reference/weave/common/TraitTypeInstanceStructSchema.cpp         \
    reference/weave/common/TraitTypeInstanceStructSchema.h           \
    templates/common.macros                                          \
    templates/copyright.inc                                          \
    templates/enum.common.h                                          \
    templates/event_struct.cpp.inc                                   \
    templates/event_struct.h.inc                                     \
    templates/resource.cpp.h                                         \
    templates/struct.cpp                                             \
    templates/struct.cpp.h                                           \
    templates/trait.c.h                                              \
    templates/trait.cpp                                              \
    templates/trait.cpp.h                                            \
    templates/typespace.c.h                                          \
    templates/typespace.cpp                                          \
    templates/typespace.cpp.h                                        \
    $(NULL)

include $(abs_top_nlbuild_autotools_dir)/automake/post.am
