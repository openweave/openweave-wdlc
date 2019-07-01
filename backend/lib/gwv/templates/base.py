#
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
#      This file implements a base Jinja code generation
#      target-independent specialized template for generating any
#      output from Weave Data Language (WDL) schema.k
#

"""Base class to represent a code generation template.

This class can handle arbitrary file types.  The specialized subclasses for
C, Java, and Markdown are more appropriate to use for those types of files.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import itertools
import json
import os
import re
import inflection
import jinja2

# from google3.pyglib import resources
from gwv import exception
from gwv import json_utils
from gwv import schema

TYPE_URL_PREFIX = 'type.nestlabs.com/'


class TemplateLoader(jinja2.BaseLoader):
  """Loads jinja2 templates from resources."""

  def __init__(self, path):
    super(TemplateLoader, self).__init__()
    self.path = path

  def get_source(self, unused_environment, template):
    path = os.path.join(self.path, template)
    return (resources.GetResource(path).decode('utf-8'), None, lambda: True)


class CodegenTemplate(object):
  """Base codegen template class.

  This template can be used to generate arbitrary file types.  Specialized
  subclasses for C, Java, and Markdown add language-specific configuration and
  utility functions to the templating environment.
  """

  def __init__(self, template_path, jinja_args=None):
    """Initialze this CodegenTemplate.

    This will create a configured Jinja Environment with the basic global
    functions provided to all templates.

    Args:
      template_path: The path to the template.
      jinja_args: Optional additional named arguments to pass to the Jinja
        environment constructor.

    Raises:
      Exception: Unable to parse the template type and extension from the
        template_path.
    """

    # Short description for the template class.
    self.desc = 'Generic'

    self.template_filename = os.path.basename(template_path)

    m = re.match(r'([^.]*).*\.([^.]*)$', self.template_filename)
    if not m:
      raise Exception(
          'Error matching template filename: %s' % self.template_filename)

    self.schema_object_type = m.group(1).lower()
    self.extension = m.group(2)

    default_jinja_args = {
        'loader': jinja2.FileSystemLoader(os.path.dirname(template_path)),
        'undefined': jinja2.StrictUndefined,
        'trim_blocks': True,
        'lstrip_blocks': True,
        'extensions': ['jinja2.ext.do', 'jinja2.ext.loopcontrols'],
        'line_statement_prefix': '%%',
        'line_comment_prefix': '##'
    }

    if jinja_args:
      default_jinja_args.update(jinja_args)

    self.jinja_env = jinja2.Environment(**default_jinja_args)

    self.jinja_env.globals.update({
        'template_filename': self.template_filename,
        'error': error,
        'full_id': full_id,
        'quote': json.dumps,
        'is_object': is_object,
        'is_field': is_field,
        'is_map': is_map,
        'has_visibility': has_visibility,
        'hasattr': hasattr,
        'json_schema': json_schema,
        'data_as_json': data_as_json,
        'camelize': inflection.camelize,
        'dasherize': inflection.dasherize,
        'humanize': inflection.humanize,
        'underscore': inflection.underscore,
        'regex_replace': regex_replace,
        'print': print,
        'map_key': map_key,
        'map_value': map_value,
        'get_enum_dependencies': get_enum_dependencies,
        'get_struct_dependencies': get_struct_dependencies,
        'get_dependencies': get_dependencies,
        'get_direct_dependencies': get_direct_dependencies,
        'get_nested_enums': get_nested_enums,
        'get_nested_structs': get_nested_structs,
        'get_all_files': get_all_files,
        'get_all_structs': get_all_structs,
        'get_all_enums': get_all_enums,
        'get_all_typespaces': get_all_typespaces,
        'get_all_traits': get_all_traits,
        'get_all_commands': get_all_commands,
        'get_all_command_responses': get_all_command_responses,
        'get_all_events': get_all_events,
        'get_all_interfaces': get_all_interfaces,
        'get_all_resources': get_all_resources,
        'type_url_prefix': TYPE_URL_PREFIX,
        'get_object_type': get_object_type,
        'get_object_type_url': get_object_type_url,
        'get_idl_type': idl_type,
    })

    self.jinja_env.tests.update({
        'array': is_array,
        'command': is_command,
        'command_response': is_command_response,
        'common': is_common,
        'duration': is_duration,
        'event': is_event,
        'field': is_field,
        'nullable': is_nullable,
        'map': is_map,
        'object': is_object,
        'standard': is_standard,
        'protobuf': is_protobuf,
        'wdl': is_wdl,
        'resource_id': is_resource_id,
        'resource_name': is_resource_name,
        'timestamp': is_timestamp,
        'writable': is_writable,
        'false': lambda x: not x,
        'struct': is_struct,
        'oneof': is_oneof,
        'enum': is_enum,
        'trait': is_trait,
        'typespace': is_typespace,
        'vendor': is_vendor,
    })

    self.jinja_env.filters.update({
        'all': all,
        'any': any,
        'camelize': inflection.camelize,
        'chain': itertools.chain,
        'dasherize': inflection.dasherize,
        'humanize': inflection.humanize,
        'max': max,
        'min': min,
        'underscore': inflection.underscore,
        'unique': unique,
    })

  def get_jinja_template(self):
    return self.jinja_env.get_template(self.template_filename)

  def post_codegen_all(self, filenames):
    for filename in filenames:
      self.post_codegen(filename)

  def post_codegen(self, filename):
    pass


def json_schema(schema_obj, json_format='DEVICE_RESOURCE', compact=True):
  """Returns a JSON representation of the given trait.

  At the moment, only Traits are supported.

  Args:
    schema_obj: The trait or interface to convert.
    json_format: Name of an attribute of JsonFormat.
    compact: True for compact JSON, False to include newlines and indentation.

  Returns:
    A string representation of the JSON device draft.

  Raises:
    Exception: The given parameter is not a Trait or Interface instance.
  """

  json_format = getattr(json_utils.JsonFormat, json_format)

  if isinstance(schema_obj, schema.Trait):
    json_dict = json_utils.trait_as_json(schema_obj, json_format)
  else:
    raise Exception('Invalid object passed to json_schema: %s' % (schema_obj))

  return data_as_json(json_dict, compact)


def data_as_json(data, compact=False):
  """Converts a Python value into JSON.

  Args:
    data: The data to convert.
    compact: True for compact JSON, False to include newlines and indentation.

  Returns:
    A JSON representation of the data, as a string.
  """

  if compact:
    return json.dumps(data)
  return json.dumps(data, indent=2, separators=(',', ': '))


def is_field(field, type_name):
  """Checks if a field object is of the given data type name.

  Args:
    field: The field in question.
    type_name: The string name of a Field.DataType.

  Returns:
    True or False.
  """

  # Backward compatibility from when Component was Field
  if type_name == 'TRAIT' or isinstance(field, schema.Component):
    return type_name == 'TRAIT' and isinstance(field, schema.Component)

  return field.data_type == getattr(schema.Field.DataType, type_name)


def has_visibility(trait, visibility_name):
  """Checks if a trait object has the given visibility.

  Args:
    trait: The trait in question.
    visibility_name: The string name of a Trait.Visibility.

  Returns:
    True or False.
  """

  return trait.visibility == getattr(schema.Trait.Visibility, visibility_name)


def is_object(value, class_name):
  """Checks if a given value is an instance of a schema class name.

  Args:
    value: The value in question.
    class_name: The string name of a schema class.

  Returns:
    True or False.
  """

  return isinstance(value, getattr(schema, class_name))


def full_id(schema_obj):
  """Returns the full 32 bit id of trait or interface as a hex number string."""

  return '0x%08x' % ((schema_obj.parent.number << 16) | schema_obj.number)


def error(msg):
  """Raises an exception.

  Used to flag an error condition from a Jinja template.

  Args:
    msg: The error message.

  Raises:
    Exception: Yep.
  """

  raise Exception(msg)


def unique(items, attribute=None):
  """Returns the list with only the unique items.

  Args:
    items: List of items.
    attribute: An attribute.

  Returns:
    List: Unique list of items.
  """

  if attribute is not None:
    return list(
        collections.OrderedDict.fromkeys(
            [getattr(item, attribute) for item in items]))
  else:
    return list(collections.OrderedDict.fromkeys(items))


def is_writable(schema_obj):
  """Checks if the schema objects is writable."""

  if isinstance(schema_obj, schema.Field):
    # Events and response can never be writable
    if (isinstance(schema_obj.parent, schema.Event) or
        isinstance(schema_obj.parent, schema.CommandResponse)):
      return False
    # Command parameters are always writable
    elif isinstance(schema_obj.parent, schema.Command):
      return True
    else:
      return schema_obj.writable
  else:
    raise Exception('Expecting a field')


def is_map(field):
  """Checks if the field is a mpa."""

  if isinstance(field, schema.Field):
    return field.is_map
  else:
    raise Exception('Expecting a field')


def is_array(schema_obj):
  """Checks if the schema objects is an array."""

  if isinstance(schema_obj, schema.Field):
    return schema_obj.is_array
  return False


def is_command(schema_obj):
  """Checks if the schema objects is a command."""

  return isinstance(schema_obj, schema.Command)


def is_event(schema_obj):
  """Checks if the schema objects is an event."""

  return isinstance(schema_obj, schema.Event)


def is_struct(schema_obj):
  """Checks if the schema objects is a struct."""

  return (isinstance(schema_obj, schema.Struct) or
          (isinstance(schema_obj, schema.Field) and schema_obj.struct_type))


def is_enum(schema_obj):
  """Checks if the schema objects is a enum."""

  return (isinstance(schema_obj, schema.Enum) or
          (isinstance(schema_obj, schema.Field) and schema_obj.enum_type))


def is_command_response(schema_obj):
  """Checks if the schema objects is a command response."""

  return isinstance(schema_obj, schema.CommandResponse)


def is_trait(schema_obj):
  """Checks if the schema objects is a trait."""

  return isinstance(schema_obj, schema.Trait)


def is_typespace(schema_obj):
  """Checks if the schema objects is a typespace."""

  return isinstance(schema_obj, schema.Typespace)


def is_vendor(schema_obj):
  """Checks if the schema objects is a vendor."""

  return isinstance(schema_obj, schema.Vendor)


def is_nullable(schema_obj):
  """Checks if the schema objects is nullable."""

  if isinstance(schema_obj, schema.Field):
    return schema_obj.is_nullable
  return False


def is_oneof(schema_obj):
  """Checks if the schema objects is a one_of."""

  if isinstance(schema_obj, schema.Field):
    return schema_obj.is_oneof
  return False


def is_standard(schema_obj):
  """Checks if the schema objects is a standard type."""

  if isinstance(schema_obj, schema.Field):
    return is_standard(schema_obj.struct_type)
  elif isinstance(schema_obj, schema.Struct):
    standard_types = [
        'google.protobuf.Duration',
        'google.protobuf.Timestamp',
        'weave.common.ResourceId',
        'weave.common.ResourceName',
    ]
    return schema_obj.full_name in standard_types
  return False


def is_common(schema_obj):
  """Checks if the schema objects is a common type."""

  return is_protobuf(schema_obj) or is_wdl(schema_obj)


def is_protobuf(schema_obj):
  """Checks if in protobuf module."""

  if isinstance(schema_obj, schema.Field):
    if schema_obj.data_type == schema.Field.DataType.ENUM:
      return is_protobuf(schema_obj.enum_type)
    elif schema_obj.data_type == schema.Field.DataType.STRUCT:
      return is_protobuf(schema_obj.struct_type)
  else:
    protobuf_prefixes = ('google.protobuf.',)
    return schema_obj.full_name.startswith(protobuf_prefixes)


def is_wdl(schema_obj):
  """Checks if in wdl module."""

  if isinstance(schema_obj, schema.Field):
    if schema_obj.data_type == schema.Field.DataType.ENUM:
      return is_wdl(schema_obj.enum_type)
    elif schema_obj.data_type == schema.Field.DataType.STRUCT:
      return is_wdl(schema_obj.struct_type)
  else:
    wdl_prefixes = (
        'wdl.',
        'weave.common.',
    )
    return schema_obj.full_name.startswith(wdl_prefixes)


def is_resource_id(schema_obj):
  """Checks if the schema objects is a resource id."""

  if isinstance(schema_obj, schema.Field):
    return is_resource_id(schema_obj.metadata)
  elif isinstance(schema_obj, schema.Struct):
    return schema_obj.full_name == 'weave.common.ResourceId'
  return False


def is_resource_name(schema_obj):
  """Checks if the schema objects is a resource name."""

  if isinstance(schema_obj, schema.Field):
    return is_resource_name(schema_obj.metadata)
  elif isinstance(schema_obj, schema.Struct):
    return schema_obj.full_name == 'weave.common.ResourceName'
  return False


def is_timestamp(schema_obj):
  """Checks if the schema objects is a timestamp."""

  if isinstance(schema_obj, schema.Field):
    return is_timestamp(schema_obj.metadata)
  elif isinstance(schema_obj, schema.Struct):
    return schema_obj.full_name == 'google.protobuf.Timestamp'
  return False


def is_duration(schema_obj):
  """Checks if the schema objects is a duration."""

  if isinstance(schema_obj, schema.Field):
    return is_duration(schema_obj.metadata)
  elif isinstance(schema_obj, schema.Struct):
    return schema_obj.full_name == 'google.protobuf.Duration'
  return False


def map_key(field):
  """Returns a map key."""

  if is_map(field):
    return field.map_key


def map_value(field):
  """Returns a map value."""

  if is_map(field):
    return field
  return None


def regex_replace(s, old, new, count=0):
  """Performs a regex replace."""

  return re.sub(old, new, s, count=count)


def get_struct_dependencies(*objs):
  """Gets only struct dependencies for all the given objects.

  Args:
    *objs: List of schema objects.

  Returns:
    List: List of struct object dependencies.
  """

  return [
      obj for obj in get_dependencies(*objs) if isinstance(obj, schema.Struct)
  ]


def get_enum_dependencies(*objs):
  """Gets only enum dependencies for all the given objects.

  Args:
    *objs: List of schema objects.

  Returns:
    List: List of enum object dependencies.
  """

  return [
      obj for obj in get_dependencies(*objs) if isinstance(obj, schema.Enum)
  ]


def get_dependencies(*objs):
  """Gets the dependencies for all the given objects.

  Map entries are included, filter them out with ` | reject('map') `

  Args:
    *objs: List of schema objects.

  Returns:
    List: List of enum and struct object dependencies.
  """

  deps = set()
  for obj in objs:
    if isinstance(obj, schema.File):
      deps |= get_dependencies(*obj.trait_list)
      deps |= get_dependencies(*obj.typespace_list)
      deps |= get_dependencies(*obj.struct_list)
    elif isinstance(obj, schema.SchemaObjectList):
      deps |= get_dependencies(*obj)
    elif isinstance(obj, schema.Schema):
      deps |= get_dependencies(*obj.vendor_list)
    elif isinstance(obj, schema.Vendor):
      deps |= get_dependencies(*obj.trait_list)
      deps |= get_dependencies(*obj.typespace_list)
      deps |= get_dependencies(*obj.struct_list)
    elif isinstance(obj, schema.Trait):
      deps |= get_dependencies(*obj.command_list)
      deps |= get_dependencies(*obj.event_list)
      deps |= get_dependencies(*obj.state_list)
      deps |= get_dependencies(*obj.struct_list)
    elif isinstance(obj, schema.Command):
      deps |= get_dependencies(*obj.parameter_list)
      deps |= get_dependencies(obj.response)
    elif isinstance(obj, schema.CommandResponse):
      deps |= get_dependencies(*obj.field_list)
    elif isinstance(obj, schema.Event):
      deps |= get_dependencies(*obj.field_list)
    elif isinstance(obj, schema.Typespace):
      deps |= get_dependencies(*obj.struct_list)
    elif isinstance(obj, schema.Enum):
      pass
    elif isinstance(obj, schema.Struct):
      deps |= get_dependencies(*obj.field_list)
    elif isinstance(obj, schema.Field):
      if obj.data_type == schema.Field.DataType.ENUM:
        deps.add(obj.enum_type)
      elif obj.data_type == schema.Field.DataType.STRUCT:
        deps.add(obj.struct_type)
        deps |= get_dependencies(obj.struct_type)
  return deps


def get_direct_dependencies(*objs):
  """Gets the direct dependencies for all the given objects.

  Args:
    *objs: List of schema objects.

  Returns:
    List: List of enum and struct object dependencies.
  """

  deps = set()
  for obj in objs:
    if isinstance(obj, schema.File):
      for enum in obj.enum_list:
        deps.add(enum)
      for interface in obj.interface_list:
        deps.add(interface)
      for struct in obj.struct_list:
        deps.add(struct)
      for trait in obj.trait_list:
        deps.add(trait)
      deps |= get_direct_dependencies(*obj.interface_list)
      deps |= get_direct_dependencies(*obj.struct_list)
      deps |= get_direct_dependencies(*obj.resource_list)
      deps |= get_direct_dependencies(*obj.trait_list)
      deps |= get_direct_dependencies(*obj.typespace_list)
    elif isinstance(obj, schema.SchemaObjectList):
      deps |= get_direct_dependencies(*obj)
    elif isinstance(obj, schema.Schema):
      deps |= get_direct_dependencies(*obj.vendor_list)
    elif isinstance(obj, schema.Vendor):
      for enum in obj.enum_list:
        deps.add(enum)
      for interface in obj.interface_list:
        deps.add(interface)
      for struct in obj.struct_list:
        deps.add(struct)
      for trait in obj.trait_list:
        deps.add(trait)
      deps |= get_direct_dependencies(*obj.interface_list)
      deps |= get_direct_dependencies(*obj.struct_list)
      deps |= get_direct_dependencies(*obj.resource_list)
      deps |= get_direct_dependencies(*obj.trait_list)
      deps |= get_direct_dependencies(*obj.typespace_list)
    elif isinstance(obj, schema.Resource):
      for component in obj.component_list:
        deps.add(component.trait)
      for group in obj.group_list:
        deps.add(group)
    elif isinstance(obj, schema.Interface):
      for component in obj.component_list:
        deps.add(component.trait)
    elif isinstance(obj, schema.Typespace):
      for enum in obj.enum_list:
        deps.add(enum)
      for struct in obj.struct_list:
        deps.add(struct)
      deps |= get_direct_dependencies(*obj.struct_list)
    elif isinstance(obj, schema.Trait):
      for command in obj.command_list:
        deps.add(command)
      for enum in obj.enum_list:
        deps.add(enum)
      for event in obj.event_list:
        deps.add(event)
      for struct in obj.struct_list:
        deps.add(struct)
      deps |= get_direct_dependencies(*obj.command_list)
      deps |= get_direct_dependencies(*obj.event_list)
      deps |= get_direct_dependencies(*obj.state_list)
      deps |= get_direct_dependencies(*obj.struct_list)
    elif isinstance(obj, schema.Command):
      if obj.response is not None:
        deps.add(obj.response)
      deps |= get_direct_dependencies(*obj.parameter_list)
    elif isinstance(obj, schema.CommandResponse):
      deps |= get_direct_dependencies(*obj.field_list)
    elif isinstance(obj, schema.Event):
      deps |= get_direct_dependencies(*obj.field_list)
    elif isinstance(obj, schema.Struct):
      deps |= get_direct_dependencies(*obj.field_list)
    elif isinstance(obj, schema.Field):
      if obj.data_type == schema.Field.DataType.ENUM:
        deps.add(obj.enum_type)
      elif obj.data_type == schema.Field.DataType.STRUCT:
        deps.add(obj.struct_type)
  return deps


def get_nested_enums(*objs):
  """Gets the nested enums for all the given objects.

  Args:
    *objs: List of schema objects.

  Returns:
    List: List of enum object.
  """

  deps = []
  for obj in objs:
    if isinstance(obj, schema.File):
      deps.extend(get_nested_enums(*obj.enum_list))
      deps.extend(get_nested_enums(*obj.typespace_list))
      deps.extend(get_nested_enums(*obj.trait_list))
    elif isinstance(obj, schema.SchemaObjectList):
      deps.extend(get_nested_enums(*obj))
    elif isinstance(obj, schema.Schema):
      deps.extend(get_nested_enums(*obj.vendor_list))
    elif isinstance(obj, schema.Vendor):
      deps.extend(get_nested_enums(*obj.enum_list))
      deps.extend(get_nested_enums(*obj.typespace_list))
      deps.extend(get_nested_enums(*obj.trait_list))
    elif isinstance(obj, schema.Trait):
      deps.extend(get_nested_enums(*obj.enum_list))
    elif isinstance(obj, schema.Typespace):
      deps.extend(get_nested_enums(*obj.enum_list))
    elif isinstance(obj, schema.Enum):
      deps.append(obj)
  return deps


def get_nested_structs(*objs):
  """Gets the nested structs for all the given objects.

  Args:
    *objs: List of schema objects.

  Returns:
    List: List of structs object.
  """

  deps = []
  for obj in objs:
    if isinstance(obj, schema.File):
      deps.extend(get_nested_structs(*obj.struct_list))
      deps.extend(get_nested_structs(*obj.typespace_list))
      deps.extend(get_nested_structs(*obj.trait_list))
    elif isinstance(obj, schema.SchemaObjectList):
      deps.extend(get_nested_structs(*obj))
    elif isinstance(obj, schema.Schema):
      deps.extend(get_nested_structs(*obj.vendor_list))
    elif isinstance(obj, schema.Vendor):
      deps.extend(get_nested_structs(*obj.struct_list))
      deps.extend(get_nested_structs(*obj.typespace_list))
      deps.extend(get_nested_structs(*obj.trait_list))
    elif isinstance(obj, schema.Trait):
      deps.extend(get_nested_structs(*obj.struct_list))
    elif isinstance(obj, schema.Typespace):
      deps.extend(get_nested_structs(*obj.struct_list))
    elif isinstance(obj, schema.Struct):
      deps.append(obj)
  return deps


def get_all_files(schema_obj):
  """Gets all files for a schema object."""

  files = []
  for vendor in schema_obj.vendor_list:
    for file_obj in vendor.file_list:
      files.append(file_obj)
  return files


def get_all_structs(schema_obj):
  """Gets all structs for a schema object."""

  structs = []
  for vendor in schema_obj.vendor_list:
    for typespace in vendor.typespace_list:
      for struct in typespace.struct_list:
        structs.append(struct)
    for trait in vendor.trait_list:
      for struct in trait.struct_list:
        structs.append(struct)
    for struct in vendor.struct_list:
      structs.append(struct)
  return structs


def get_all_enums(schema_obj):
  """Gets all enums for a schema object."""

  enums = []
  for vendor in schema_obj.vendor_list:
    for typespace in vendor.typespace_list:
      for enum in typespace.enum_list:
        enums.append(enum)
    for trait in vendor.trait_list:
      for enum in trait.enum_list:
        enums.append(enum)
    for enum in vendor.enum_list:
      enums.append(enum)
  return enums


def get_all_typespaces(schema_obj):
  """Gets all typespaces for a schema object."""

  typespaces = []
  for vendor in schema_obj.vendor_list:
    for typespace in vendor.typespace_list:
      typespaces.append(typespace)
  return typespaces


def get_all_traits(schema_obj):
  """Gets all traits for a schema object."""

  traits = []
  for vendor in schema_obj.vendor_list:
    for trait in vendor.trait_list:
      traits.append(trait)
  return traits


def get_all_commands(schema_obj):
  """Gets all commands for a schema object."""

  commands = []
  for vendor in schema_obj.vendor_list:
    for trait in vendor.trait_list:
      for command in trait.command_list:
        commands.append(command)
  return commands


def get_all_command_responses(schema_obj):
  """Gets all command responses for a schema object."""

  command_responses = []
  for vendor in schema_obj.vendor_list:
    for trait in vendor.trait_list:
      for command in trait.command_list:
        if command.response is not None:
          command_responses.append(command.response)
  return command_responses


def get_all_events(schema_obj):
  """Gets all events for a schema object."""

  events = []
  for vendor in schema_obj.vendor_list:
    for trait in vendor.trait_list:
      for event in trait.event_list:
        events.append(event)
  return events


def get_all_interfaces(schema_obj):
  """Gets all interfaces for a schema object."""

  interfaces = []
  for vendor in schema_obj.vendor_list:
    for interface in vendor.interface_list:
      interfaces.append(interface)
  return interfaces


def get_all_resources(schema_obj):
  """Gets all resources for a schema object."""

  resource_objs = []
  for vendor in schema_obj.vendor_list:
    for resource_obj in vendor.resource_list:
      resource_objs.append(resource_obj)
  return resource_objs


def get_object_type(schema_obj):
  """Gets the object type."""

  if isinstance(schema_obj, schema.Field):
    raise exception.InvalidArgument(schema_obj)
  return schema_obj.full_name


def get_object_type_url(schema_obj):
  """Gets the object type url."""

  if (isinstance(schema_obj, schema.Command) or
      isinstance(schema_obj, schema.CommandResponse) or
      isinstance(schema_obj, schema.Event) or
      isinstance(schema_obj, schema.Trait)):
    return TYPE_URL_PREFIX + get_object_type(schema_obj)
  else:
    raise exception.InvalidArgument(schema_obj)


def idl_type(field, namespace):
  """Get the field type as it would be defined in protobuf idl.

  Args:
    field: field to get type of.
    namespace: namespace of field, this will used to strip redundant scoping
      from names.

  Returns:
    A string representing the idl type.
  """

  out = ''
  if field.is_map:
    out = 'map <{0},'.format(idl_type(field.map_key, namespace))

  if field.is_array:
    out += 'repeated '

  if field.data_type in (schema.Field.DataType.STRUCT,
                         schema.Field.DataType.ENUM):
    out += field.metadata.full_name.replace(namespace, '').strip('.')
  else:
    out += field.data_type.value

  if field.is_map:
    out += '>'

  return out
