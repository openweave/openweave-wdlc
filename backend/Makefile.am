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
#      (WDL) Compiler (WDLC) backend.
#

include $(abs_top_nlbuild_autotools_dir)/automake/pre.am

EXTRA_DIST                                                         = \
    .gitignore                                                       \
    README.md                                                        \
    docs_compile.csh                                                 \
    gwvc                                                             \
    lib/gwv/__init__.py                                              \
    lib/gwv/exception.py                                             \
    lib/gwv/file_utils.py                                            \
    lib/gwv/gwvc.py                                                  \
    lib/gwv/json_utils.py                                            \
    lib/gwv/schema.py                                                \
    lib/gwv/template_set.py                                          \
    lib/gwv/templates/__init__.py                                    \
    lib/gwv/templates/base.py                                        \
    lib/gwv/templates/c.py                                           \
    lib/gwv/templates/cpp.py                                         \
    lib/gwv/templates/java.py                                        \
    lib/gwv/templates/js.py                                          \
    lib/gwv/templates/md.py                                          \
    lib/gwv/templates/objc.py                                        \
    lib/gwv/test_schema.py                                           \
    lib/gwv/validator.py                                             \
    lib/gwv/visitor.py                                               \
    lib/nwv/__init__.py                                              \
    lib/nwv/nwv_parser.py                                            \
    lib/nwv/proto_pool.py                                            \
    lib/nwv/validators/__init__.py                                   \
    lib/nwv/validators/added_object_validator.py                     \
    lib/nwv/validators/changed_number_validator.py                   \
    lib/nwv/validators/changed_type_validator.py                     \
    lib/nwv/validators/duration_validator.py                         \
    lib/nwv/validators/enum_value_name_validator.py                  \
    lib/nwv/validators/extends_validator.py                          \
    lib/nwv/validators/filename_validator.py                         \
    lib/nwv/validators/iface_mapping_validator.py                    \
    lib/nwv/validators/map_validator.py                              \
    lib/nwv/validators/min_version_validator.py                      \
    lib/nwv/validators/name_inflection_validator.py                  \
    lib/nwv/validators/name_suffix_validator.py                      \
    lib/nwv/validators/naming_rules_validator.py                     \
    lib/nwv/validators/no_new_java_outer_classname_validator.py      \
    lib/nwv/validators/nullable_validator.py                         \
    lib/nwv/validators/number_validator.py                           \
    lib/nwv/validators/one_byte_field_tag_validator.py               \
    lib/nwv/validators/one_interface_type_validator.py               \
    lib/nwv/validators/removed_object_validator.py                   \
    lib/nwv/validators/stability_reference_validator.py              \
    lib/nwv/validators/stability_validator.py                        \
    lib/nwv/validators/test_added_object_validator.py                \
    lib/nwv/validators/test_enum_value_name_validator.py             \
    lib/nwv/validators/test_extends_validator.py                     \
    lib/nwv/validators/test_filename_validator.py                    \
    lib/nwv/validators/test_iface_mapping_validator.py               \
    lib/nwv/validators/test_map_validator.py                         \
    lib/nwv/validators/test_min_version_validator.py                 \
    lib/nwv/validators/test_name_inflection_validator.py             \
    lib/nwv/validators/test_name_suffix_validator.py                 \
    lib/nwv/validators/test_naming_rules_validator.py                \
    lib/nwv/validators/test_no_new_java_outer_classname_validator.py \
    lib/nwv/validators/test_nullable_validator.py                    \
    lib/nwv/validators/test_number_constraints_validator.py          \
    lib/nwv/validators/test_one_byte_field_tag_validator.py          \
    lib/nwv/validators/test_removed_object_validator.py              \
    lib/nwv/validators/test_stability_reference_validator.py         \
    lib/nwv/validators/test_stability_validator.py                   \
    lib/nwv/validators/timestamp_validator.py                        \
    lib/nwv/validators/trait_instance_id_validator.py                \
    lib/nwv/validators/trait_instance_options_validator.py           \
    lib/nwv/validators/unique_name_per_vendor_validator.py           \
    lib/nwv/wdl_plugin.py                                            \
    pip-install-requirements.txt                                     \
    pylint.sh                                                        \
    schema_tests                                                     \
    setup.sh                                                         \
    wdl_plugin                                                       \
    $(NULL)

include $(abs_top_nlbuild_autotools_dir)/automake/post.am
