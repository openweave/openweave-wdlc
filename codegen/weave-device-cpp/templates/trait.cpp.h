{#
 #    Copyright (c) 2019-2020 Google LLC. All Rights Reserved.
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
 #      trait code generation template for Weave Data Language (WDL) schema.
 #}
{% from 'common.macros' import include_guard, imports, namespace_blocks, enum_def %}

{% do set_dest_file(c_header_file(trait)) -%}

{%- with schema_object=trait -%}
{% include 'copyright.inc' %}
{% endwith %}

{% call include_guard(trait) %}

#include <Weave/Profiles/data-management/DataManagement.h>
#include <Weave/Support/SerializationUtils.h>

{{imports(trait)}}

{% call namespace_blocks(trait) %}
namespace {{trait.base_name}} {

extern const nl::Weave::Profiles::DataManagement::TraitSchemaEngine TraitSchema;

  {# TODO: {{HAS_TRAIT_ID}} #}
enum {
  {% set profile_id_const -%}
    {# Reused for events #}
    kWeaveProfileId = ({{ '%#x'|format(trait.parent.number) }}U << 16) | {{ '%#x'|format(trait.number) }}U
  {%- endset %}
  {{ profile_id_const }}
};

  {% set path_handles = get_path_handles(trait) %}
  {% if path_handles %}
//
// Properties
//

enum {
    kPropertyHandle_Root = 1,

    //---------------------------------------------------------------------------------------------------------------------------//
    //  Name                                IDL Type                            TLV Type           Optional?       Nullable?     //
    //---------------------------------------------------------------------------------------------------------------------------//

    {% for path in path_handles %}
      {% set field = path[-1] %}
    //
    //  {{ field.base_name.ljust(36) -}}
          {{ get_idl_type(field, trait.full_name).ljust(36) -}}
          {{ (' ' ~ tlv_type(field)).ljust(19) -}}
          {{ ('YES' if field.is_optional else 'NO').ljust(16) -}}
          {{ 'YES' if field.is_nullable else 'NO' }}
    //
    kPropertyHandle_{{ path|map(attribute='base_name')|map('camelize')|join('_') }} = {{ loop.index + 1 }},

    {% endfor %}
    //
    // Enum for last handle
    //
    kLastSchemaHandle = {{path_handles|length+1}},
};

{% endif %}
{% if trait.struct_list %}
//
// Event Structs
//

{% for struct in trait.struct_list if struct.field_list|length %}
{% include 'event_struct.h.inc' %}
{% endfor %}
{% endif %}
{% if trait.event_list %}
//
// Events
//
    {% for event in trait.event_list %}
      {% with struct=event %}
      {% include 'event_struct.h.inc' %}
      {% endwith %}

    {% endfor %}
  {% endif %}
{% if trait.command_list %}
//
// Commands
//

enum {
    {% for command in trait.command_list %}
    k{{ command.base_name }}Id = {{ '%#x'|format(command.number) }},
    {% endfor %}
};

    {% for command in trait.command_list if command.parameter_list %}
enum {{ command.base_name }}Parameters {
      {% for field in command.parameter_list %}
    k{{ command.base_name }}Parameter_{{ field.base_name|camelize }} = {{ field.number }},
      {% endfor %}
};

    {% endfor %}
    {% for command in trait.command_list if command.response %}
enum {{ command.response.base_name }}Parameters {
      {% for field in command.response.field_list %}
    k{{ command.response.base_name }}Parameter_{{ field.base_name|camelize }} = {{ field.number }},
      {% endfor %}
};

    {% endfor %}
{% endif %}
{% if trait.enum_list %}
//
// Enums
//

{% for enum in trait.enum_list %}
{{ enum_def(enum) }}

{% endfor %}
{% endif %}
{% if trait.constant_group_list %}
//
// Constants
//
{% for constant_group in trait.constant_group_list %}
      {% for constant in constant_group.constant_list %}
#define {{ constant.base_name }} {
        {%- for byte in resource_id_bytes(constant.value) -%}
          0x{{ '%02x'|format(byte) }}{{ ', ' if not loop.last else '' }}
        {%- endfor -%}
        }
      {% endfor %}
{% endfor %}

{% for constant_group in trait.constant_group_list %}
enum {{ constant_group.base_name }} {
      {% for constant in constant_group.constant_list %}
        {{ constant.base_name }}_IMP =
        {{- ' 0x' ~ '%016x'|format(resource_id_number(constant.value)) }}ULL,
        {{- ' // ' ~ constant.value }}
      {% endfor %}
};

{% endfor %}
{% endif %}
} // namespace {{trait.base_name}}
{%- endcall %}{# namespace_blocks #}
{% endcall %}{# include_guard #}
