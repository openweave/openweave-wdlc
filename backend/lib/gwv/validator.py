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
#      This file defines and implements base classes for implementing
#      Weave Data Language (WDL) validators.
#

"""Define classes for implementing schema validators."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from gwv import schema
from gwv import visitor
from six.moves import map

class ValidationWarning(Exception):
  """Exception indicating that schema failed validation."""

  def __init__(self, message, schema_obj=None):
    super(ValidationWarning, self).__init__(message, schema_obj)
    self.message = message
    self.schema_obj = schema_obj

  def __str__(self):
    msg = self.message
    if self.schema_obj:
      msg = '%r in %s has a validation warning: %s' % (
          self.schema_obj, self.schema_obj.source_file, msg)
    return msg


class ValidationError(ValidationWarning):
  """Exception indicating that schema failed validation."""

  def __str__(self):
    msg = self.message
    if self.schema_obj:
      msg = '%r in %s failed validation: %s' % (self.schema_obj,
                                                self.schema_obj.source_file,
                                                msg)
    return msg


class SchemaValidator(object):
  """Base class for schema validators."""

  def __init__(self, **kwargs):
    del kwargs  # Unused by SchemaValidator.
    self.failures = []
    self.warnings = []

  def add_failure(self, message, schema_obj=None):
    """Subclasses should call add_failure for every validation failure."""
    self.failures.append(ValidationError(message, schema_obj))

  def add_warning(self, message, schema_obj=None):
    """Subclasses should call add_failure for every validation failure."""
    self.warnings.append(ValidationWarning(message, schema_obj))

  def validate(self, schema_obj):
    """Subclasses should implement validate to perform validation."""
    raise NotImplementedError('validate not implemented')

  @classmethod
  def process(cls, schema_obj, **kwargs):
    """Run validation, throwing ValidationError on failure."""
    # This makes SchemaValidator compatible with gwvc --processor
    validator = cls(**kwargs)
    validator.validate(schema_obj)
    if validator.failures:
      raise ValidationError('%s validation failed:\n\n  %s\n\n'
                            'For a validation exception, contact your '
                            'organization\'s schema administrator.' %
                            (cls.__name__,
                             '\n  '.join(map(str, validator.failures))))

    if validator.warnings:
      raise ValidationWarning('%s has validation warnings:\n  %s' %
                              (cls.__name__,
                               '\n  '.join(map(str, validator.warnings))))


class VisitorValidator(SchemaValidator, visitor.SchemaVisitor):
  """Base class for visitor based validators.

  Subclasses should implement visit_* methods as with SchemaVisitor and on
  validation failure do one of the following:
  - self.add_failure("failure message")
  - raise
  ValidationError("failure message")

  Validations may also use `assert`:
  - assert validation_test(), "failure message"

  Note that only the add_failure method will allow SchemaVisitor to continue
  validating any children of the failed object.
  """

  _currently_visiting = None

  def __init__(self, **kwargs):
    super(VisitorValidator, self).__init__(**kwargs)

  def visit(self, obj, *args, **kwargs):
    self._currently_visiting = obj
    try:
      super(VisitorValidator, self).visit(obj, *args, **kwargs)
    except AssertionError as ae:
      self.add_failure(ae.message)
    except ValidationError as ve:
      if ve.schema_obj is None:
        ve.schema_obj = obj
      self.failures.append(ve)
    except ValidationWarning as vw:
      if vw.schema_obj is None:
        vw.schema_obj = obj
      self.warnings.append(vw)

  def add_failure(self, message, schema_obj=None):
    if schema_obj is None:
      schema_obj = self._currently_visiting
    super(VisitorValidator, self).add_failure(message, schema_obj)

  def validate(self, schema_obj):
    self.visit(schema_obj)


class VisitorComparisonValidator(VisitorValidator):
  """Compares current schema to previous schema.

  Runs the visitor with the previous schema with methods to lookup objects in
  the current schema.
  """

  def __init__(self, previous_schema, **kwargs):
    self.previous_schema = previous_schema
    super(VisitorValidator, self).__init__(**kwargs)

  def validate(self, schema_obj):
    self.current_schema = schema_obj
    if not self.previous_schema:
      raise Exception('This processor requires a previous schema to be '
                      'specified')
    self.visit(self.previous_schema)

  def get_obj_from_current_schema(self, previous_obj):
    return self._get_obj_from_schema(previous_obj, self.current_schema)

  def get_obj_from_previous_schema(self, current_obj):
    return self._get_obj_from_schema(current_obj, self.previous_schema)

  def _get_obj_from_schema(self, obj, schema_obj):
    """Gets the equivalent object from the new schema.

    Recursive method that climbs to the root of the schema and then walks back
    down using the keys from the given obj to lookup up the equivalent obj in
    the schema.

    Args:
      obj: The object to get.
      schema_obj: The schema.

    Returns:
      The equivalent object.
    """

    # Root of schema_obj
    if isinstance(obj, schema.Schema):
      return schema_obj

    if isinstance(obj, schema.SchemaObject) and obj.parent_list is not None:
      # Use parent_list if it exists
      parent = self._get_obj_from_schema(obj.parent_list, schema_obj)
    else:
      # If no parent_list exists, just use parent
      parent = self._get_obj_from_schema(obj.parent, schema_obj)

    # Couldn't find the parent of obj
    if parent is None:
      return None

    if isinstance(parent, schema.SchemaObjectList):
      # If parent is a list, find obj by name in list
      return parent.by_name(obj.base_name)
    elif (isinstance(parent, schema.Command) and
          isinstance(obj, schema.CommandResponse)):
      # Command responses have a special hierarchy
      return parent.response
    else:
      # Assume obj exists in parent as a property
      # with the same name. This may fail if schema.py changes,
      return getattr(parent, obj.base_name)


class ValidatorTestCase(unittest.TestCase):
  """Base class for validator unit tests.

  A valid Schema is created for each test, accessible via get_test_* methods.
  Tests are expected to modify the valid Schema to make it fail the validator
  under test, and then call e.g.:
      self.assert_invalid(Validator, r'failure message regex')
  """

  def setUp(self):
    self._schema = self.gen_test_schema()

  def gen_test_schema(self):
    schema_obj = schema.Schema()

    vendor = schema.Vendor('test', 0xfe00, '')
    schema_obj.vendor_list.append(vendor)

    resource = schema.Resource('TestResource', 0x0001, '')
    resource.file = schema.File('test_resource', 1, '')
    resource.version = 2
    vendor.resource_list.append(resource)

    iface = schema.Interface('TestIface', 0x0001, '')
    iface.file = schema.File('test_iface', 1, '')
    vendor.interface_list.append(iface)

    trait = schema.Trait('TestTrait', 1, '')
    trait.file = schema.File('test_trait', 1, '')
    vendor.trait_list.append(trait)

    typespace = schema.Typespace('TestTypespace', 1, '')
    typespace.file = schema.File('test_typespace', 1, '')
    vendor.typespace_list.append(typespace)

    trait.version = 2
    trait.stability = schema.Stability.ALPHA

    field = schema.Field('test_field', 1, '', schema.Field.DataType.INT32, None)
    trait.state_list.append(field)

    resource_component = schema.ResourceComponent('test_component', 1, '')
    resource_component.trait = trait
    resource.component_list.append(resource_component)

    interface_component = schema.InterfaceComponent('test_component', 1, '')
    interface_component.trait = trait
    iface.component_list.append(interface_component)

    group = schema.Group('test_group', 1, '')
    group.interface = iface
    resource.group_list.append(group)

    struct = schema.Struct('TestStruct', 1, '')
    trait.struct_list.append(struct)

    enum = schema.Enum('TestEnum', 1, '')
    enum.pair_list.append(schema.EnumPair('TEST_ENUM_UNSPECIFIED', 0, ''))
    enum.pair_list.append(schema.EnumPair('TEST_ENUM_ONE', 1, ''))
    enum.pair_list.append(schema.EnumPair('TEST_ENUM_TWO', 2, ''))
    trait.enum_list.append(enum)

    event = schema.Event('TestEvent', 1, '')
    event.field_list.append(field)
    trait.event_list.append(event)

    response = schema.CommandResponse('TestRequestResponse', 1, '')
    response.field_list.append(field)

    command = schema.Command('TestRequest', 1, '')
    command.parameter_list.append(field)
    trait.command_list.append(command)

    command.response = response
    response.parent = command

    return schema_obj

  def assert_invalid(self,
                     validator_cls,
                     failure_regex,
                     num_expected_failures=1):
    validator = validator_cls()
    validator.validate(self.get_test_schema())
    self.assertEqual(
        len(validator.failures), num_expected_failures,
        'Expected exactly %d failure, got %d' % (num_expected_failures,
                                                 len(validator.failures)))
    for failure in validator.failures:
      self.assertRegexpMatches(str(failure), failure_regex)

  def assert_valid(self, validator_cls):
    validator = validator_cls()
    validator.validate(self.get_test_schema())
    self.assertEqual(
        len(validator.failures), 0,
        'Expected exactly 0 failure, got %d' % len(validator.failures))

  def get_test_schema(self):
    return self._schema

  def get_test_vendor(self):
    return self.get_test_schema().vendor_list.by_name('test')

  def get_test_resource(self):
    return self.get_test_vendor().resource_list.by_name('TestResource')

  def get_test_iface(self):
    return self.get_test_vendor().interface_list.by_name('TestIface')

  def get_test_trait(self):
    return self.get_test_vendor().trait_list.by_name('TestTrait')

  def get_test_typespace(self):
    return self.get_test_vendor().typespace_list.by_name('TestTypespace')

  def get_test_struct(self):
    return self.get_test_trait().struct_list.by_name('TestStruct')

  def get_test_enum(self):
    return self.get_test_trait().enum_list.by_name('TestEnum')

  def get_test_event(self):
    return self.get_test_trait().event_list.by_name('TestEvent')

  def get_test_command(self):
    return self.get_test_trait().command_list.by_name('TestRequest')

  def get_test_response(self):
    return self.get_test_command().response

  def get_test_resource_component(self):
    return self.get_test_resource().component_list.by_name('test_component')

  def get_test_iface_component(self):
    return self.get_test_iface().component_list.by_name('test_component')

  def get_test_group(self):
    return self.get_test_resource().group_list.by_name('test_group')


class ComparisonValidatorTestCase(ValidatorTestCase):
  """Base class for comparison validator unit test."""

  def setUp(self):
    self._schema = self.gen_test_schema()
    self._previous_schema = self.gen_test_schema()

  def assert_invalid(self, validator_cls, failure_regex):
    validator = validator_cls(previous_schema=self._previous_schema)
    validator.validate(self.get_test_schema())
    self.assertEqual(
        len(validator.failures), 1,
        'Expected exactly 1 failure, got %d' % len(validator.failures))
    self.assertRegexpMatches(str(validator.failures[0]), failure_regex)

  def assert_valid(self, validator_cls):
    validator = validator_cls(previous_schema=self._previous_schema)
    validator.validate(self.get_test_schema())
    self.assertEqual(
        len(validator.failures), 0,
        'Expected exactly 0 failure, got %d' % len(validator.failures))

  def get_previous_test_schema(self):
    return self._previous_schema

  def get_previous_test_vendor(self):
    return self.get_previous_test_schema().vendor_list.by_name('test')

  def get_previous_test_trait(self):
    return self.get_previous_test_vendor().trait_list.by_name('TestTrait')

  def get_previous_test_typespace(self):
    return self.get_previous_test_vendor().typespace_list.by_name(
        'TestTypespace')

  def get_previous_test_struct(self):
    return self.get_previous_test_trait().struct_list.by_name('TestStruct')

  def get_previous_test_enum(self):
    return self.get_previous_test_trait().enum_list.by_name('TestEnum')

  def get_previous_test_iface(self):
    return self.get_previous_test_vendor().interface_list.by_name('TestIface')

  def get_previous_test_resource(self):
    return self.get_previous_test_vendor().resource_list.by_name('TestResource')
