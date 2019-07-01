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
 #      trait code generation template for Weave Data Language (WDL) schema.
 #}
{% from 'common.macros' import include_guard, namespace_blocks, enum_def %}

{% do set_dest_file(c_header_file(trait)|replace('.h','.cpp')) -%}

{%- with schema_object=trait -%}
{% include 'copyright.inc' %}
{% endwith %}


#include <{{c_header_file(trait)}}>

{% call namespace_blocks(trait) %}
namespace {{trait.base_name}} {

using namespace ::nl::Weave::Profiles::DataManagement;

    {% set path_handles = get_path_handles(trait) %}
//
// Property Table
//

const TraitSchemaEngine::PropertyInfo PropertyMap[] = {
        {% for path in path_handles %}
        {% if path|length > 1 %}
    { kPropertyHandle_{{ path[:-1]|map(attribute='base_name')|map('camelize')|join('_') }}, {{path[-1].number}} }, // {{path[-1].base_name}}
        {% else %}
    { kPropertyHandle_Root, {{path[-1].number}} }, // {{path[-1].base_name}}
        {% endif %}
        {% endfor %}
};

    {% set is_dictionary_bitfield = list_to_bitfield(path_handles|map('last')|map(attribute='is_map')|list) %}
{% if is_dictionary_bitfield | any %}
//
// IsDictionary Table
//

uint8_t IsDictionaryTypeHandleBitfield[] = {
##- Squish to one line because whitespace formatting in jinja is a pain
{{' '*8}}{% for byte in is_dictionary_bitfield %}{{'0x%0x' % byte}}{{', ' if not loop.last else '\n'}}{% endfor %}
};

{% endif %}
{% set is_optional_bitfield = list_to_bitfield(path_handles|map('last')|map(attribute='is_optional')|list) %}
{% if is_optional_bitfield | any %}
//
// IsOptional Table
//

uint8_t IsOptionalHandleBitfield[] = {
##- Squish to one line because whitespace formatting in jinja is a pain
{{' '*8}}{% for byte in is_optional_bitfield %}{{'0x%0x' % byte}}{{', ' if not loop.last else '\n'}}{% endfor %}
};

{% endif %}
{% set is_nullable_bitfield = list_to_bitfield(path_handles|map('last')|map(attribute='is_nullable')|list) %}
{% if is_nullable_bitfield | any %}
//
// IsNullable Table
//

uint8_t IsNullableHandleBitfield[] = {
##- Squish to one line because whitespace formatting in jinja is a pain
{{' '*8}}{% for byte in is_nullable_bitfield %}{{'0x%0x' % byte}}{{', ' if not loop.last else '\n'}}{% endfor %}
};

{% endif %}
{% set is_ephemeral_bitfield = list_to_bitfield(path_handles|map('last')|map(attribute='is_ephemeral')|list) %}
{% if is_ephemeral_bitfield | any %}
//
// IsEphemeral Table
//

uint8_t IsEphemeralHandleBitfield[] = {
##- Squish to one line because whitespace formatting in jinja is a pain
{{' '*8}}{% for byte in is_ephemeral_bitfield %}{{'0x%0x' % byte}}{{', ' if not loop.last else '\n'}}{% endfor %}
};

{% endif %}
{%  if trait.version > 1 %}
//
// Supported version
//
const ConstSchemaVersionRange traitVersion = { .mMinVersion = 1, .mMaxVersion = {{trait.version}} };

{% endif %}
//
// Schema
//

const TraitSchemaEngine TraitSchema = {
    {
        kWeaveProfileId,
        PropertyMap,
        sizeof(PropertyMap) / sizeof(PropertyMap[0]),
        {{(path_handles|map('length')|list or [1]) |max}},
#if (TDM_EXTENSION_SUPPORT) || (TDM_VERSIONING_SUPPORT)
        {{2 if not trait.extends else get_path_handles(trait.extends)|length+2}},
#endif
        {{'IsDictionaryTypeHandleBitfield' if is_dictionary_bitfield|any else 'NULL'}},
        {{'&IsOptionalHandleBitfield[0]' if is_optional_bitfield|any else 'NULL'}},
        NULL,
        {{'&IsNullableHandleBitfield[0]' if is_nullable_bitfield|any else 'NULL'}},
        {{'&IsEphemeralHandleBitfield[0]' if is_ephemeral_bitfield|any else 'NULL'}},
#if (TDM_EXTENSION_SUPPORT)
        {% if trait.extends %}
        &{{full_cpp_name(trait.extends)|replace('Schema::','')}}::TraitSchema,
        {% else %}
        NULL,
        {% endif %}
#endif
#if (TDM_VERSIONING_SUPPORT)
{%  if trait.version > 1 %}
        &traitVersion,
{% else %}
        NULL,
{% endif %}
#endif
    }
};

    {% if trait.event_list|length %}
    //
    // Events
    //

    {% for event in trait.event_list %}
    {% with struct=event %}
    {% include 'event_struct.cpp.inc' %}
    {% endwith %}
const nl::Weave::Profiles::DataManagement::EventSchema {{event.base_name}}::Schema =
{
    .mProfileId = kWeaveProfileId,
    .mStructureType = {{'%#x'|format(event.number)}},
    .mImportance = {{{event.importance.PRODUCTION_CRITICAL: "nl::Weave::Profiles::DataManagement::ProductionCritical",
                      event.importance.PRODUCTION_STANDARD: "nl::Weave::Profiles::DataManagement::Production",
                      event.importance.INFO: "nl::Weave::Profiles::DataManagement::Info",
                      event.importance.DEBUG: "nl::Weave::Profiles::DataManagement::Debug"}
                      [event.importance]}},
    .mDataSchemaVersion = {{trait.version}},
    .mMinCompatibleDataSchemaVersion = 1,
};

    {% endfor %}
    {% endif %}
{% if trait.struct_list|length %}
//
// Event Structs
//
{% for struct in trait.struct_list %}

{% include 'event_struct.cpp.inc' %}

{% endfor %}
{% endif %}
} // namespace {{trait.base_name}}{% endcall %}{# namespace_blocks #}
