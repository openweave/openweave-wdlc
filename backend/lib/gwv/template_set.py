#
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
#      This file effects the main code generation dispatch for
#      generating code (or any output) from Weave Data Language (WDL)
#      schema.
#

"""Generates code from a set of template files and a schema.Schema object."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import datetime
import logging
import os
import re
import enum

from gwv.templates import base
from gwv.templates import c
from gwv.templates import cpp
from gwv.templates import java
from gwv.templates import js
from gwv.templates import md
from gwv.templates import objc
import six

# Mapping from file extension to a codegen template constructor.
codegen_template_mapping = collections.OrderedDict([
    (r'.*(?<!\.objc)(?<!\.cpp)\.(c|h)$', c.CodegenTemplate),
    (r'.*(?<!\.objc)(?<!\.c)\.(cc|cpp|h|hpp)$', cpp.CodegenTemplate),
    (r'.*(?<!\.cpp)(?<!\.c)\.(m|h)$', objc.CodegenTemplate),
    (r'.*\.java$', java.CodegenTemplate),
    (r'.*\.js.jinja$', js.CodegenTemplate),
    (r'.*\.md$', md.CodegenTemplate),
    (r'.*\.swift$', objc.CodegenTemplate),
    (r'.*', base.CodegenTemplate)
])  # pyformat: disable


class TemplateLanguage(enum.Enum):
  """Template Language Enum."""

  BASE = 0
  C = 1
  CPLUSPLUS = 2
  JAVA = 3
  JAVASCRIPT = 4
  MARKDOWN = 5
  OBJECTIVEC = 6

  def get_codegen_template(self, template_filename):
    codegen_template_classes = {
        TemplateLanguage.BASE: base.CodegenTemplate,
        TemplateLanguage.C: c.CodegenTemplate,
        TemplateLanguage.CPLUSPLUS: cpp.CodegenTemplate,
        TemplateLanguage.JAVA: java.CodegenTemplate,
        TemplateLanguage.JAVASCRIPT: js.CodegenTemplate,
        TemplateLanguage.MARKDOWN: md.CodegenTemplate,
        TemplateLanguage.OBJECTIVEC: objc.CodegenTemplate,
    }
    return codegen_template_classes[self](template_filename)


class TemplateSet(object):
  """Manages a set of codegen templates."""

  def __init__(self,
               template_filenames,
               legacy_mode_enabled=False,
               language=TemplateLanguage.BASE):
    self.language = language
    self.legacy_mode_enabled = legacy_mode_enabled
    self.output_files = []

    # This map will contain an appropriate CodegenTemplate instance for
    # each template file, categorized by the schema object type they
    # require.
    self.template_types = {
        'command': [],
        'command_response': [],
        'device': [],
        'enum': [],
        'event': [],
        'file': [],
        'interface': [],
        'resource': [],
        'schema': [],
        'struct': [],
        'trait': [],
        'typespace': [],
        'vendor': [],
    }

    # Load the provided template files.
    self.add_template_files(template_filenames)

  def add_template_files(self, template_filenames):
    """Adds a template file to the template set."""

    # Fill out the template_types configuration.
    for filename in template_filenames:
      if self.legacy_mode_enabled:
        codegen_template = self.get_codegen_template(filename)
        schema_object_type = codegen_template.schema_object_type
      else:
        codegen_template = self.language.get_codegen_template(filename)
        schema_object_type = 'file'

      if schema_object_type not in self.template_types:
        continue

      self.template_types[schema_object_type].append(codegen_template)

  def get_codegen_template(self, template_filename):
    """Returns a new CodegenTemplate instance for the given template_filename.

    Find an appropriate CodegenTemplate subclass for the given file, construct a
    new instance, and return it.

    Args:
      template_filename: A template filename.

    Returns:
      A CodegenTemplate instance appropriate for the given template filename.

    Raises:
      Exception: No template class for the given filename. The base template
      class should match for unknown file types, so this should never happen.
    """

    for (pattern, template_class) in six.iteritems(codegen_template_mapping):
      if re.match(pattern, template_filename):
        return template_class(template_filename)

    raise Exception(
        'Didn\'t find a CodegenTemplate class for %s' % template_filename)

  def codegen_template(self, user_data, codegen_template):
    """Process a single codegen template.

    The resulting file will be marked as read-only to prevent accidental edits.

    Args:
      user_data: Additional data to pass to the template.
      codegen_template: The template to process.

    Returns:
      The actual destination file.

    Raises:
      Exception: Error while rendering.
    """

    utcnow = datetime.datetime.utcnow()
    data = {
        'year': str(utcnow.year),
        'date': str(utcnow),
        'dest_file': None,
    }
    data.update(user_data)

    class ParsingException(Exception):
      pass

    def stop_parsing():
      raise ParsingException

    if self.legacy_mode_enabled:
      codegen_template.jinja_env.globals['stop_parsing'] = stop_parsing

    def set_dest_file(*args):
      data['dest_file'] = os.path.join(*args)

    codegen_template.jinja_env.globals['set_dest_file'] = set_dest_file

    try:
      contents = codegen_template.get_jinja_template().render(data)
    except ParsingException:
      # Stop parsing the template
      return
    except:
      logging.error("Error while rendering '%s' into '%s",
                    codegen_template.template_filename, data['dest_file'])
      raise

    dest_file = data['dest_file']

    if not dest_file:
      raise Exception('No dest_file set in \'{}\''.format(
          codegen_template.template_filename))

    self.output_files.append((dest_file, contents))

  def codegen_schema_object_type(self, typename, schema_object, env_data):
    """Generates templates of a given schema type with the given schema object.

    Args:
      typename: The schema object type name, 'schema', 'vendor', 'typespace',
        'trait', 'interface', or 'device'.
      schema_object: The schema object to pass to the template.
      env_data: Additional data to provide in the template environment.
    """

    # The object passed in to interface templates is shortened to 'iface', for
    # fun.
    keyname = typename if typename != 'interface' else 'iface'

    for codegen_template in self.template_types[typename]:
      _ = self.codegen_template({
          keyname: schema_object,
          'env': env_data
      }, codegen_template)

  def codegen(self, schema, env_data, target_files):
    """Create code for the given schema out of the templates in this set.

    Args:
      schema: The root schema object.
      env_data: Additional data to define in the template environment.
    """

    def return_match(file_list, target_files):
        for file in file_list:
            if target_files is None or file.source_file in target_files:
                yield file

    self.codegen_schema_object_type('schema', schema, env_data)

    for vendor in schema.vendor_list:
      self.codegen_schema_object_type('vendor', vendor, env_data)

      for file_obj in return_match(vendor.file_list, target_files):
        self.codegen_schema_object_type('file', file_obj, env_data)

      for trait in return_match(vendor.trait_list, target_files):
        self.codegen_schema_object_type('trait', trait, env_data)

        for command in trait.command_list:
          self.codegen_schema_object_type('command', command, env_data)

          if command.response:
            self.codegen_schema_object_type('command_response',
                                            command.response, env_data)

        for event in trait.event_list:
          self.codegen_schema_object_type('event', event, env_data)

        # TODO(robbarnes): Remove this later, all clients must embed structs in
        # traits
        for struct in trait.struct_list:
          self.codegen_schema_object_type('struct', struct, env_data)

        # TODO(robbarnes): Remove this later, all clients must embed enums in
        # traits
        for enum_obj in trait.enum_list:
          self.codegen_schema_object_type('enum', enum_obj, env_data)

      for typespace in return_match(vendor.typespace_list, target_files):
        self.codegen_schema_object_type('typespace', typespace, env_data)

        # TODO(robbarnes): Remove this later, all clients must embed structs in
        # traits
        for struct in typespace.struct_list:
          self.codegen_schema_object_type('struct', struct, env_data)

        # TODO(robbarnes): Remove this later, all clients must embed enums in
        # traits
        for enum_obj in typespace.enum_list:
          self.codegen_schema_object_type('enum', enum_obj, env_data)

      for interface in return_match(vendor.interface_list, target_files):
        self.codegen_schema_object_type('interface', interface, env_data)

      for resource in return_match(vendor.resource_list, target_files):
        self.codegen_schema_object_type('resource', resource, env_data)

      # This should only contain structs not inside traits or typespaces
      for struct in return_match(vendor.struct_list, target_files):
        self.codegen_schema_object_type('struct', struct, env_data)

      # This should only contain enums not inside traits or typespaces
      for enum_obj in return_match(vendor.enum_list, target_files):
        self.codegen_schema_object_type('enum', enum_obj, env_data)

