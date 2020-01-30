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
#      This file effects the actual implementation for the Weave Data
#      Language (WDL) Compiler (WDLC) backend used for schema
#      validation checking and comparison.
#

"""Google Weave schema compiler front end script."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
import logging
import os
import re
import sys
import getopt

from google.protobuf import descriptor_pb2
from gwv import file_utils
from gwv import schema
from gwv import template_set
from gwv import validator
from nwv import nwv_parser
from nwv.validators import added_object_validator
from nwv.validators import changed_number_validator
from nwv.validators import changed_type_validator
from nwv.validators import duration_validator
from nwv.validators import enum_value_name_validator
from nwv.validators import extends_validator
from nwv.validators import filename_validator
from nwv.validators import iface_mapping_validator
from nwv.validators import map_validator
from nwv.validators import min_version_validator
from nwv.validators import name_inflection_validator
from nwv.validators import name_suffix_validator
from nwv.validators import naming_rules_validator
from nwv.validators import no_new_java_outer_classname_validator
from nwv.validators import nullable_validator
from nwv.validators import number_validator
from nwv.validators import one_interface_type_validator
from nwv.validators import read_write_validator
from nwv.validators import removed_object_validator
from nwv.validators import stability_reference_validator
from nwv.validators import stability_validator
from nwv.validators import timestamp_validator
from nwv.validators import trait_instance_id_validator
from nwv.validators import unique_name_per_vendor_validator


def parse_schema_descriptor(proto_descriptor):
  """Parse schema descriptor and return schema object.

  Args:
    proto_descriptor: Path to a protobuf file set descriptor binary
      containing schema files.

  Returns:
    A schema.Schema object built from the provided schema_files.

  Raises:
    Exception: No schema files found.
  """

  schema_obj = schema.Schema()
  schema_parser = nwv_parser.Parser(schema_obj)

  logging.debug('Parse schema descriptor.')
  schema_parser.add_file_set(proto_descriptor.file)

  return schema_obj


def get_schema_object(args):
  """Parse schema descriptor and return schema object.

  Args:
    args: Commandline arguments

  Returns:
    A schema.Schema object built from the provided schema_files.

  Raises:
    Exception: Error in command line arguments.
  """
  parser = argparse.ArgumentParser(description='Schema validator.')
  parser.add_argument(
      '--proto_descriptor',
      help='Pre generated schema protobuf descriptor',
      default=None)

  (parsed_args, _) = parser.parse_known_args(args)

  if parsed_args.proto_descriptor:
    with open(parsed_args.proto_descriptor, 'rb') as f:
      proto_descriptor = descriptor_pb2.FileDescriptorSet.FromString(f.read())
      return parse_schema_descriptor(proto_descriptor)


def check(schema_object, *_):
  """Checks that the given schema compiles and can be loaded.

  Args:
    schema_object: The WDL schema object to be checked.

  Returns:
    A schema.Schema object representing the schema that was checked, or
    None if no schema files were found.

  Raises:
    Exception: Error in command line arguments.
  """
  validation_errors = []
  validation_warnings = []

  validator_objects = [
      iface_mapping_validator,
      name_inflection_validator,
      name_suffix_validator,
      enum_value_name_validator,
      read_write_validator,
      nullable_validator,
      extends_validator,
      one_interface_type_validator,
      number_validator,
      timestamp_validator,
      duration_validator,
      trait_instance_id_validator,
      unique_name_per_vendor_validator,
      stability_reference_validator,
      naming_rules_validator,
      min_version_validator,
      map_validator,
      filename_validator,
  ]

  for validator_object in validator_objects:
    try:
      logging.debug('Running validator %s', validator_object)
      validator_object.process(schema_object)
    except validator.ValidationError as ve:
      validation_errors.append(ve)
    except validator.ValidationWarning as vw:
      validation_warnings.append(vw)
    except:
      logging.error('error running validator %r', validator_object)
      raise

  if validation_warnings:
    logging.warn('Validation warnings.\n')
    for validation_warning in validation_warnings:
      logging.warn(validation_warning)

  if validation_errors:
    logging.error('Validation failed!\n')
    for validation_error in validation_errors:
      logging.error(validation_error)
    sys.exit(1)


def compare(current_schema, *args):
  """Compares the given schema against the previous schema.

  Args:
    current_schema: The current WDL schema object to be compared against.
    *args: The other command line arguments.

  Returns:
    A schema.Schema object representing the schema that was checked, or
    None if no schema files were found.

  Raises:
    Exception: Error in command line arguments.
  """

  parser = argparse.ArgumentParser(description='Schema validator.')
  parser.add_argument(
      '--previous_proto_descriptor',
      help='Pre generated previous schema protobuf descriptor',
      required=True)

  (parsed_args, _) = parser.parse_known_args(args)

  with open(parsed_args.previous_proto_descriptor, 'rb') as f:
    previous_proto_descriptor = descriptor_pb2.FileDescriptorSet.FromString(
        f.read())
    previous_schema = parse_schema_descriptor(previous_proto_descriptor)

  validation_errors = []
  validation_warnings = []

  validator_objects = [
      added_object_validator,
      removed_object_validator,
      stability_validator,
      changed_number_validator,
      changed_type_validator,
      no_new_java_outer_classname_validator,
  ]

  for validator_object in validator_objects:
    try:
      logging.debug('Running validator %s', validator_object)
      validator_object.process(current_schema, previous_schema=previous_schema)
    except validator.ValidationError as ve:
      validation_errors.append(ve)
    except validator.ValidationWarning as vw:
      validation_warnings.append(vw)
    except:
      logging.error('error running validator %r', validator_object)
      raise

  if validation_warnings:
    logging.warn('Validation warnings.\n')
    for validation_warning in validation_warnings:
      logging.warn(validation_warning)

  if validation_errors:
    logging.error('Validation failed!\n')
    for validation_error in validation_errors:
      logging.error(validation_error)
    sys.exit(1)


def info(schema_object, *_):
  """Dumps information about a schema.

  Outputs each trait and resource in the schema, in order of profile id.
  Consecutive traits or resources in the same package will be grouped together.

  Vendors
    common.......................................................... 0x0000
  Traits
    weave.trait.locale.LocaleTrait.................................. 0x0011
    weave.trait.heartbeat.LowPowerHeartbeatSettingsTrait............ 0x0013
    weave.trait.locale.LocaleSettingsTrait.......................... 0x0014
    weave.trait.locale.LocaleCapabilitiesTrait...................... 0x0015
    weave.trait.description.LabelSettingsTrait...................... 0x0016
    weave.trait.description.DeviceIdentityTrait..................... 0x0017
    weave.trait.power.PowerSourceCapabilitiesTrait.................. 0x0018
    weave.trait.power.PowerSourceTrait.............................. 0x0019
    weave.trait.power.PowerSourcesTrait............................. 0x001A
    weave.trait.power.BatteryPowerSourceCapabilitiesTrait........... 0x001B

    etc.....

  Args:
    schema_object: The WDL schema object to print the info for.
  """

  # Run check first
  check(schema_object)

  def schema_cmp(a, b):
    return cmp(a.number, b.number)

  print('Vendors')
  indent = ' ' * 2
  for vendor in sorted(schema_object.vendor_list, schema_cmp):
    print('{:.<70} 0x{:04X}'.format(indent * 1 + vendor.base_name,
                                    vendor.number))
    if vendor.trait_list:
      print(indent * 2 + 'Traits')

      for trait in sorted(vendor.trait_list, schema_cmp):
        print('{:.<70} 0x{:04X}'.format(indent * 3 + trait.full_name,
                                        trait.number))
      print('')

    if vendor.resource_list:
      print(indent * 2 + 'Resources')

      for resource in sorted(vendor.resource_list, schema_cmp):
        print('{:.<70} 0x{:04X}'.format(indent * 3 + resource.full_name,
                                        resource.number))
      print('')


def codegen(schema_object, *args):
  """Generates code from Jinja templates.

  Templates should be named in the form:

    <object-type>.*.<extension>

  <object-type> must be one of (case insensitive):
    * "schema", "vendor", "interface", "trait", or "struct"

  <extension> can be anything.  However, certain extensions will trigger
  specialized templating environments.

  See template_set.codegen_template_mapping for the exact mapping from
  extension to template subclass.

  In between <object-type> and <extension> can be any text.

  Args:
    schema_object: The WDL schema object to codegen.
    *args: The other command line arguments.
  """

  parser = argparse.ArgumentParser(description='Code generator.')
  parser.add_argument(
      '--template_path',
      help='The directory to locate the template files.  '
      'Defaults to the common prefix among all template_files',
      type=str)
  parser.add_argument(
      '--out',
      required=True,
      help='The root directory to write generated files.',
      type=str)
  parser.add_argument(
      '--define',
      help='Additional data to define in the template '
      'environment, specified as a name=value pair.',
      type=str,
      action='append')

  (parsed_args, _) = parser.parse_known_args(args)

  if parsed_args.template_path:
    template_path = os.path.abspath(parsed_args.template_path)
  else:
    logging.error('--template_path must be provided.')
    sys.exit(1)

  # Run check because codegen makes assumptions based on this passing
  check(schema_object)

  template_files = [
      os.path.join(template_path, f)
      for f in os.listdir(template_path)
  ]

  env_data = {}
  if parsed_args.define:
    for pair in parsed_args.define:
      m = re.match(r'\s*([^=\s]+)\s*=\s*(.*)', pair)
      if not m:
        logging.error('Unable to parse user data: %s', pair)
        sys.exit(1)
      env_data[m.group(1)] = m.group(2)

  # Add two spaces to each log messages to make it line up with our output.
  template_set.log = lambda *a: logging.info(' ', *a)

  logging.info('Loading templates: %s', template_files)
  templates = template_set.TemplateSet(template_files)

  if env_data:
    logging.info('Additional environment data:')
    logging.info(json.dumps(env_data, indent=2, separators=(',', ': ')))
  else:
    logging.info('No additional environment data.')

  logging.info('Generating code: %s', parsed_args.out)
  templates.codegen(schema_object, env_data)

  for filename, contents in templates.output_files:
    dest_file = os.path.join(parsed_args.out, filename)
    file_utils.mkdir_p(os.path.dirname(dest_file))
    file_utils.enable_writes([dest_file])
    fh = open(dest_file, 'wb')
    fh.write(contents.encode('utf-8') + '\n')
    fh.close()


def usage(status, commands):
  name = os.path.basename(__file__)

  print("Usage: %s [ option ... ] <command>" % name)

  if status != 0:
    print("Try '%s -h' for more information." % name)

  if status != 1:
    print("")
    print("Supported commands: %s" % (', '.join(sorted(commands.keys()))))
    print("")
    print("Options:")
    print("")
    print("  -h, --help     Display this help, then exit.")
    print("  -q, --quiet    Work silently; do not display diagnostic and "
          "progress output")
    print("                 unless an error occurs.")
    print("  -v, --verbose  Work verbosely; increase the level of diagnostic "
          "and progress")
    print("                 output.")

  sys.exit(status)

def main():
  commands = {
    'check'   : check,
    'codegen' : codegen,
    'compare' : compare,
    'info'    : info
  }
  options = { "verbose" : 1 }

  # Parse command line options

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hqv",
                               [ "help", "quiet", "verbose" ])

  except getopt.GetoptError as err:
    sys.exit("%s: Failed to parse options and arguments: %s" %
             (__file__, str(err)))

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage(0, commands)

    elif opt in ("-q", "--quiet"):
      options["verbose"] = 0

    elif opt in ("-v", "--verbose"):
      options["verbose"] += 1

    else:
      logger.error("unrecognized or unsupported option %s" % opt)
      usage(1, commands)

  # Modulate the logging level based on the verbosity flag

  if options["verbose"] == 0:
    logging.basicConfig(level=logging.WARNING)

  elif options["verbose"] == 1:
    logging.basicConfig(level=logging.INFO)

  elif options["verbose"] >= 2:
    logging.basicConfig(level=logging.DEBUG)

  # Dispatch the actual command

  if len(args) > 1 and args[0] in commands:
    schema_object = get_schema_object(args[1:])
    return commands[args[0]](schema_object, *args[1:])

  usage(1, commands)

if __name__ == '__main__':
  main()
