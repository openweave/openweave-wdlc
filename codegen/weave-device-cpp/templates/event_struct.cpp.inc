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
 #      This file effects a Jinja-based openweave-core device C++ source
 #      trait code generation template for Weave Data Language (WDL) schema,
 #      specific to event structures.
 #}
{% if struct.field_list|length %}
const nl::FieldDescriptor {{struct.base_name}}FieldDescriptors[] =
{
    {% for field in struct.field_list if field is not map %}
        {% if field is array and not (field.enum_type and field.enum_type.is_bitmask) %}
    {
        NULL, offsetof({{struct.base_name}}, {{field.base_name|camelize(false)}}) + offsetof(
            {%- if field.struct_type and field is not standard -%}
                {{full_cpp_name(field.struct_type)}}
            {%- else -%}
                nl::SerializedFieldType{{cpp_type_name(cpp_type(field))}}
            {%- endif -%}
            _array, num), SET_TYPE_AND_FLAGS(nl::SerializedFieldTypeArray, {{'1' if field is nullable else '0'}}), {{field.number}}
    },
        {% endif %}
    {
        {% if field.struct_type and field is not standard %}
        &{{full_cpp_name(field.struct_type)}}::FieldSchema,{{' '}}
        {%- else %}
        NULL,{{' '}}
        {%- endif -%}
        offsetof({{struct.base_name}}, {{field.base_name|camelize(false)}})
        {%- if field is array and not (field.enum_type and field.enum_type.is_bitmask) -%}
        {{' '}}+ offsetof(
            {%- if field.struct_type and field is not standard -%}
                {{full_cpp_name(field.struct_type)}}
            {%- else -%}
                nl::SerializedFieldType{{cpp_type_name(cpp_type(field))}}
            {%- endif -%}
            _array, buf)
        {%- endif -%}
        , SET_TYPE_AND_FLAGS(nl::SerializedFieldType{{cpp_type_name(cpp_type(field))}}, {{'1' if field is nullable else '0'}}), {{field.number}}
    },

    {% endfor %}
};

const nl::SchemaFieldDescriptor {{struct.base_name}}::FieldSchema =
{
    .mNumFieldDescriptorElements = sizeof({{struct.base_name}}FieldDescriptors)/sizeof({{struct.base_name}}FieldDescriptors[0]),
    .mFields = {{struct.base_name}}FieldDescriptors,
    .mSize = sizeof({{struct.base_name}})
};
{% else %}
const nl::SchemaFieldDescriptor {{struct.base_name}}::FieldSchema =
{
    .mNumFieldDescriptorElements = 0,
    .mFields = NULL,
    .mSize =  sizeof({{struct.base_name}})
};

{% endif %}
