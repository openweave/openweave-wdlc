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

{% do set_dest_file(c_header_file(typespace,suffix='-c')) -%}

{%- with schema_object=typespace -%}
{% include 'copyright.inc' %}
{% endwith %}

{% call include_guard(typespace, suffix='C_H') %}


{% if typespace.enum_list %}
    //
    // Enums
    //

    {% for enum in typespace.enum_list %}
    // {{enum.base_name}}
    typedef enum
    {
    {% for pair in enum.pair_list if pair.number != 0 %}
    {{ pair.base_name | underscore | upper }} = {{ pair.number }},
    {% endfor %}
    } {{full_c_name(enum)}}_t;
    {% endfor %}

{% endif %}

{% if typespace.constant_group_list %}
    //
    // Constants
    //

    {% for constant_group in typespace.constant_group_list %}
      {% for constant in constant_group.constant_list %}
    #define {{ (full_c_name(constant_group) ~ '_' ~ constant.base_name|replace(constant_group.base_name|underscore|upper~'_',''))|upper }} {
        {%- for byte in resource_id_bytes(constant.value) -%}
          0x{{ '%02x'|format(byte) }}{{ ', ' if not loop.last else '' }}
        {%- endfor -%}
    }
      {% endfor %}
    {% endfor %}

    {% for constant_group in typespace.constant_group_list %}
      {% for constant in constant_group.constant_list %}
    #define {{ (full_c_name(constant_group) ~ '_' ~ constant.base_name|replace(constant_group.base_name|underscore|upper~'_',''))|upper }}_IMP = (
        {%- for byte in resource_id_bytes(constant.value) -%}
          {{- '0x' ~ '%016x'|format(resource_id_number(constant.value)) }}ULL)
          {{- ' // ' ~ constant.value }}
        {%- endfor %}

      {% endfor %}
    {% endfor %}

{% endif %}

{% endcall %}{# include_guard #}
