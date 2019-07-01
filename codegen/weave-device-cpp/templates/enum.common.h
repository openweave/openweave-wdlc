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
 #      This file effects a Jinja-based openweave-core device C/C++ header
 #      trait code generation template for Weave Data Language (WDL) schema,
 #      specific to enumerations.
 #}
{% from 'common.macros' import include_guard, imports, namespace_blocks, enum_def %}

{%- if enum.parent is typespace or enum.parent is trait -%}
{%- do stop_parsing() -%}
{%- endif -%}

{% do set_dest_file(c_header_file(enum)) -%}

{%- with schema_object=enum -%}
{% include 'copyright.inc' %}
{% endwith %}

{% call include_guard(enum, suffix='ENUM_H') %}

{% call namespace_blocks(enum) %}

{{ enum_def(enum) }}
{% endcall %}{# namespace_blocks #}
{% endcall %}{# include_guard #}
