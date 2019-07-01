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
 #      This file effects a Jinja-based openweave-core device C++ header
 #      trait namespace (i.e., typespace) code generation template for
 #      Weave Data Language (WDL) schema.
 #}
{% from 'common.macros' import include_guard, imports, namespace_blocks, enum_def %}

{% do set_dest_file(c_header_file(typespace)) -%}

{%- with schema_object=typespace -%}
{% include 'copyright.inc' %}
{% endwith %}

{% call include_guard(typespace) %}

#include <Weave/Profiles/data-management/DataManagement.h>
#include <Weave/Support/SerializationUtils.h>

{{imports(typespace)}}

{% call namespace_blocks(typespace) %}
namespace {{typespace.base_name}} {

  extern const nl::Weave::Profiles::DataManagement::TraitSchemaEngine TraitSchema;

  {% if typespace.struct_list %}
  //
  // Event Structs
  //

    {% for struct in typespace.struct_list %}

      {% include 'event_struct.h.inc' %}

    {% endfor %}
 {% endif %}


  {% if typespace.enum_list %}
    //
    // Enums
    //

    {% for enum in typespace.enum_list %}
      {{ enum_def(enum) }}
    {% endfor %}
  {% endif %}

  {% if typespace.constant_group_list %}
    //
    // Constants
    //

    {% for constant_group in typespace.constant_group_list %}
      {% for constant in constant_group.constant_list %}
        #define {{ constant.base_name }} {
        {%- for byte in resource_id_bytes(constant.value) -%}
          0x{{ '%02x'|format(byte) }}{{ ', ' if not loop.last else '' }}
        {%- endfor -%}
        }
      {% endfor %}
    {% endfor %}

    {% for constant_group in typespace.constant_group_list %}
      enum {{ constant_group.base_name }} {
      {% for constant in constant_group.constant_list %}
        {{ constant.base_name }}_IMP =
        {{- ' 0x' ~ '%016x'|format(resource_id_number(constant.value)) }}ULL,
        {{- ' // ' ~ constant.value }}
      {% endfor %}
      };
    {% endfor %}
  {% endif %}

} // namespace {{typespace.base_name}}
{% endcall %}{# namespace_blocks #}
{% endcall %}{# include_guard #}
