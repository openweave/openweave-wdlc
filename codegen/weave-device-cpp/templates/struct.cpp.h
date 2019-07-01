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
 #      trait code generation template for Weave Data Language (WDL) schema
 #      specific to event structures.
 #}
{% from 'common.macros' import include_guard, imports, namespace_blocks, enum_def %}

{%- if struct.parent is typespace or struct.parent is trait or struct is standard -%}
{%- do stop_parsing() -%}
{%- endif -%}

{% do set_dest_file(c_header_file(struct)) -%}

{%- with schema_object=struct -%}
{% include 'copyright.inc' %}
{% endwith %}

{% call include_guard(struct, suffix='STRUCT_SCHEMA_H') %}

#include <Weave/Support/SerializationUtils.h>
#include <Weave/Profiles/data-management/DataManagement.h>

{{imports(struct)}}

{% call namespace_blocks(struct) %}

    {% include 'event_struct.h.inc' %}

{% endcall %}{# namespace_blocks #}
{% endcall %}{# include_guard #}
