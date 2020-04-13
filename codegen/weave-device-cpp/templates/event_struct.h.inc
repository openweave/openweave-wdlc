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
 #      trait code generation template for Weave Data Language (WDL) schema,
 #      specific to event structures.
 #}
struct {{struct.base_name}}
{
      {% for field in struct.field_list if field is not map%}
       {% if field is array %}
        {% if field is struct and field is not standard %}
    {{cpp_type(field)}}_array {{field.base_name|camelize(false)}};
        {% elif field.enum_type and field.enum_type.is_bitmask %}
    {{cpp_type(field)}} {{field.base_name|camelize(false)}};
        {% else %}
    nl::SerializedFieldType{{cpp_type_name(cpp_type(field))}}_array  {{field.base_name|camelize(false)}};
        {% endif %}
       {% else %}
    {{cpp_type(field)}} {{field.base_name|camelize(false)}};
       {% endif %}
       {% if field.is_nullable %}
    void Set{{field.base_name|camelize}}Null(void);
    void Set{{field.base_name|camelize}}Present(void);
#if WEAVE_CONFIG_SERIALIZATION_ENABLE_DESERIALIZATION
    bool Is{{field.base_name|camelize}}Present(void);
#endif
      {% endif %}
     {% endfor %}
      {% if struct.field_list|selectattr('is_nullable')|list %}
    uint8_t __nullified_fields__[{{struct.field_list|selectattr('is_nullable')|list|count}}/8 + 1];
      {% endif %}

    static const nl::SchemaFieldDescriptor FieldSchema;

      {% if struct is event %}
    // Statically-known Event Struct Attributes:
    enum {
        {{ profile_id_const }},
        kEventTypeId = {{ '%#x'|format(struct.number) }}U
    };

    static const nl::Weave::Profiles::DataManagement::EventSchema Schema;
      {% endif %}
};

struct {{struct.base_name}}_array {
    uint32_t num;
    {{struct.base_name}} *buf;
};

    {% for field in struct.field_list|selectattr('is_nullable') %}
inline void {{struct.base_name}}::Set{{field.base_name|camelize}}Null(void)
{
    SET_FIELD_NULLIFIED_BIT(__nullified_fields__, {{loop.index - 1}});
}

inline void {{struct.base_name}}::Set{{field.base_name|camelize}}Present(void)
{
    CLEAR_FIELD_NULLIFIED_BIT(__nullified_fields__, {{loop.index - 1}});
}

#if WEAVE_CONFIG_SERIALIZATION_ENABLE_DESERIALIZATION
inline bool {{struct.base_name}}::Is{{field.base_name|camelize}}Present(void)
{
    return (!GET_FIELD_NULLIFIED_BIT(__nullified_fields__, {{loop.index - 1}}));
}
#endif
    {% endfor %}
