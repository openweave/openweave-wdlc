{#
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

 #
 #    Description:
 #      This file effects a Jinja-based openweave-core device C++ source
 #      trait namespace (i.e., typespace) code generation template for
 #      Weave Data Language (WDL) schema.
 #}
{% from 'common.macros' import include_guard, namespace_blocks, enum_def %}

{% do set_dest_file(c_header_file(typespace)|replace('.h','.cpp')) -%}

{%- with schema_object=typespace -%}
{% include 'copyright.inc' %}
{% endwith %}


#include <{{c_header_file(typespace)}}>

{% call namespace_blocks(typespace) %}
namespace {{typespace.base_name}} {

    using namespace ::nl::Weave::Profiles::DataManagement;

{% if typespace.struct_list %}
  //
  // Event Structs
  //
{% for struct in typespace.struct_list %}

{% include 'event_struct.cpp.inc' %}

{% endfor %}
{% endif %}

} // namespace {{typespace.base_name}}
{% endcall %}{# namespace_blocks #}
