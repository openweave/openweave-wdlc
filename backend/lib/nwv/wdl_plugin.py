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
#      This file effects the actual implementation for the Weave Data
#      Language (WDL) Compiler (WDLC) Google Protocol Buffers
#      (protobuf) compiler, protoc plugin used to validate and code
#      generate against WDL schema.
#

"""WDL protoc plugin script."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import sys

from google.protobuf.compiler import plugin_pb2
from gwv import gwvc
from gwv import schema
from gwv import template_set
from nwv import nwv_parser


def codegen(request, response):
  """Generates wdl c code for devices from Jinja templates.

  Args:
    request: CodeGeneratorRequest, see google/protobuf/compiler/plugin.proto
    response: CodeGeneratorResponse, see google/protobuf/compiler/plugin.proto.
      Output files filled with generated files.

  Raises:
    Exception: Valid Jinja template directory required for wdl plugin.
  """

  args = {}
  for argument in request.parameter.split(','):
    (key, value) = argument.split('=', 1)
    values = value.split(':')
    if len(values) == 1:
      args[key] = values[0]
    else:
      args[key] = values

  legacy_mode_enabled = ('legacy_mode_enabled' in args and
                         args['legacy_mode_enabled'].lower() == 'true')

  gen_dependencies = ('gen_dependencies' in args and
                        args['gen_dependencies'].lower() == 'true')

  codegen_reference_mode = ('codegen_reference_mode' in args and
                                args['codegen_reference_mode'].lower() == 'true')

  if isinstance(args['templates'], list):
    template_files = args['templates']
  else:
    template_files = [
        args['templates'],
    ]

  template_languages = {
      'c': template_set.TemplateLanguage.C,
      'cpp': template_set.TemplateLanguage.CPLUSPLUS,
      'java': template_set.TemplateLanguage.JAVA,
      'js': template_set.TemplateLanguage.JAVASCRIPT,
      'md': template_set.TemplateLanguage.MARKDOWN,
      'objc': template_set.TemplateLanguage.OBJECTIVEC,
  }
  if 'language' not in args or args['language'] not in template_languages:
    language = template_set.TemplateLanguage.BASE
  else:
    language = template_languages[args['language']]

  schema_obj = schema.Schema()
  schema_parser = nwv_parser.Parser(schema_obj)

  file_descs_to_gen = [
      proto_file for proto_file in request.proto_file
      if (('semantic' not in proto_file.name)
          and ('retention' not in proto_file.name))
  ]

  dependency_set = []

  # This file needs to get added to the dependency list if we're in
  # codegen mode, since this file doesn't show up as a dependency by
  # default, but is still necessary for some code-generated targets.
  if (codegen_reference_mode):
      dependency_set.append('google/protobuf/field_mask.proto')

  for proto_file in file_descs_to_gen:
    dependency_set.append(proto_file.name)

  schema_parser.add_file_set(file_descs_to_gen)

  gwvc.check(schema_obj)

  # Add two spaces to each log messages to make it line up with our output.
  template_set.log = lambda *a: print(' ', *a)

  templates = template_set.TemplateSet(
    template_files,
    legacy_mode_enabled=legacy_mode_enabled, language=language)

  if gen_dependencies:
    templates.codegen(schema_obj, None, dependency_set)
  else:
    templates.codegen(schema_obj, None, request.file_to_generate)

  for filename, content in templates.output_files:
    out_file = response.file.add()
    out_file.name = filename
    # The newline was added in the legacy template_set file writer,
    # so it's included here to preserve compatibility.
    out_file.content = content.encode('utf-8') + '\n'


if __name__ == '__main__':
  logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARN)

  std_in = sys.stdin.read()

  request_pb2 = plugin_pb2.CodeGeneratorRequest.FromString(std_in)
  response_pb2 = plugin_pb2.CodeGeneratorResponse()

  codegen(request_pb2, response_pb2)

  sys.stdout.write(response_pb2.SerializeToString())
