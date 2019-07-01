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
 #      This file effects a Jinja-based openweave-core device C header
 #      trait code generation template for Weave Data Language (WDL) schema.
 #}
{% from 'common.macros' import include_guard, namespace_blocks, enum_def %}

{% do set_dest_file(c_header_file(trait,suffix='-c')) -%}

{%- with schema_object=trait -%}
{% include 'copyright.inc' %}
{% endwith %}

{% call include_guard(trait, suffix='C_H') %}



{% if trait.command_list %}
    //
    // Commands
    //

    typedef enum
    {
    {% for command in trait.command_list %}
      k{{ command.base_name }}Id = {{ '%#x'|format(command.number) }},
    {% endfor %}
    } {{full_c_name(trait)}}_command_id_t;


    {% for command in trait.command_list if command.parameter_list %}
    // {{command.base_name}} Parameters
    typedef enum
    {
      {% for field in command.parameter_list %}
        k{{ command.base_name }}Parameter_{{ field.base_name|camelize }} = {{ field.number }},
      {% endfor %}
    } {{full_c_name(command)}}_param_t;
    {% endfor %}


    {% for command in trait.command_list if command.response %}
    // {{command.response.base_name}} Parameters
    typedef enum
    {
      {% for field in command.response.field_list %}
        k{{ command.response.base_name }}Parameter_{{ field.base_name|camelize }} = {{ field.number }},
      {% endfor %}
    } {{full_c_name(command.response)}}_param_t;
    {% endfor %}
{% endif %}

{% if trait.enum_list %}
    //
    // Enums
    //

    {% for enum in trait.enum_list %}
    // {{enum.base_name}}
    typedef enum
    {
    {% for pair in enum.pair_list if pair.number != 0 %}
    {{ pair.base_name }} = {{ pair.number }},
    {% endfor %}
    } {{full_c_name(enum)}}_t;
    {% endfor %}

{% endif %}

{% if trait.constant_group_list %}
    //
    // Constants
    //

    {% for constant_group in trait.constant_group_list %}
      {% for constant in constant_group.constant_list %}
    #define {{ (full_c_name(constant_group) ~ '_' ~ constant.base_name|replace(constant_group.base_name|underscore|upper~'_',''))|upper }} {
        {%- for byte in resource_id_bytes(constant.value) -%}
          0x{{ '%02x'|format(byte) }}{{ ', ' if not loop.last else '' }}
        {%- endfor -%}
    }
      {% endfor %}
    {% endfor %}

    {% for constant_group in trait.constant_group_list %}
      {% for constant in constant_group.constant_list %}
    #define {{ (full_c_name(constant_group) ~ '_' ~ constant.base_name|replace(constant_group.base_name|underscore|upper~'_',''))|upper }}_IMP (
        {{- '0x' ~ '%016x'|format(resource_id_number(constant.value)) }}ULL)
        {{- ' // ' ~ constant.value }}
      {% endfor %}
    {% endfor %}

{% endif %}

{% endcall %}{# include_guard #}
