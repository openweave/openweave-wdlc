# Weave Codegen Tools

## Setup

You can install dependencies using just pip or pip + virtualenv.
`setup.sh` is provided as a convenience script for setting up the virutalenv.

### Pip

[Pip](https://en.wikipedia.org/wiki/Pip_(package_manager) is a package
management system used to install and manage software packages written in
Python.

Install pip (or pip3 for python3) if it is not already installed:

```bash
# Ubuntu/Linux 64-bit
$ sudo apt-get install python-pip python-dev

# Mac OS X
$ sudo easy_install pip
$ sudo easy_install --upgrade six
```

The packages that will be installed or upgraded during the pip install
are listed in pip-install-requirements.txt. Install these required
packages using pip.


```bash
$ pip install -r pip-install-requirements.txt
```


### Virtualenv

[Virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) is a tool
to keep the dependencies required by different Python projects in separate
places.  The Virtualenv installation of Google Weave Tools will not override
pre-existing versions of the Python packages. `setup.sh` will run the below steps for you.


*  Install pip and Virtualenv.
*  Create a Virtualenv environment.
*  Activate the Virtualenv environment and install dependencies in it.
*  After the install you will activate the Virtualenv environment each time you
   want to use Google Weave Tools.

Install pip (see above).

Install Virtualenv:

```bash
# Ubuntu/Linux 64-bit
$ sudo apt-get install python-virtualenv

# Mac OS X
$ sudo easy_install virtualenv
$ sudo easy_install --upgrade six
```

Virutalenv can also be installed using pip:

```bash
$ pip install virtualenv
```

Create a Virtualenv environment:

```bash
$ virtualenv venv
```

Activate the environment:

```bash
$ source venv/bin/activate
```

Install dependencies:

```bash
$ pip install -r pip-install-requirements.txt
```

Deactive the environment:

```bash
(venv)$ deactivate
$  # Your prompt should change back
```

# OLD Codegen Overview
Code generation tool for processing phoenix IDL and generating Apps SDK code.
This tool is intended to be run as part of the build process for each SDK
platform.

To run this tool:
- Install Bazel according to http://bazel.io/docs/install.html
- bazel run :apps-codegen -- --idl=[proto.message.Name] --platform=[platform]
                             --output=[output_dir]

To build all enabled outputs for a given platform use the steps outlined in the
top level README file.

# Template Documentation and Schema Reference
This document describes how templates are processed by the code generator and
the schema of tags that are available within the templates.

## Template Directory and File Structure

The codegen tool automatically discovers templates following the correct
directory and filename structure and uses them to generate code.

All templates should be in the templates directory within the corresponding platform. (platform/[platform]/templates/).

Within the template directory, code is generated for all files that end in .tpl.
Files that generate only whitespace will not be output. This allows files to be
generated only for Traits, Resources, etc by using the appropriate section
around the entire file.

The first line of the generated file will be used as the output path and
filename and will be removed from the output. This allows flexibility in
defining output filenames. As a result, the first line of the template should
look something like:

> {{! Filename}}{{PACKAGE:x-replace=.,/}}/{{NAME:x-snake=l-}}.js

The above declaration would cause weave.trait.security.LockTrait to generate a
file weave/trait/security/lock-trait.js.

## Tag Schema

These are the tags that may be filled in for templates. **Bold** indicates tags
that have values, while *italic* indicates tags that are sections. Nested tags
are only available in the section that they appear under. Details for each tag
follow the list.

- *CAN_UPDATE*
- *CANNOT_UPDATE*
- **PACKAGE**
- *PACKAGE_PART*
    - **PACKAGE_PART**
- **JAVA_CLASS**
- *IMPORT*
    - **IMPORT**
    - **IMPORT_PACKAGE**
    - **IMPORT_NAME**
- **NAME**
- **FULL_NAME**
- **OBJC_CLASS**
- **TYPE_URL**
- **TRAIT_NAME**
- **TRAIT_OBJC_NAME**
- **SOURCE_FILEPATH**
- **SOURCE_FILENAME**
- *TRAIT*
    - **TRAIT_ID**
    - **VENDOR_ID**
    - **TRAIT_VERSION**
- *RESOURCE*
    - **VENDOR_ID**
    - **RESOURCE_VERSION**
- *COMMAND*
    - *HAS_COMPLETION_EVENT*
    - *NO_COMPLETION_EVENT*
    - **COMPLETION_EVENT**
- *EVENT*
- *MESSAGE*
- *DEPENDENCY*
- *NO_FIELDMASK_REF*
- *SUB_MESSAGE_TYPE*
    - *SUB_MESSAGE_NON_WRAPPED*
    - **SUB_MESSAGE_TYPE**
    - **SUB_MESSAGE_PACKAGE**
    - **SUB_MESSAGE_FULL_TYPE**
    - **SUB_MESSAGE_OBJC_TYPE**
- *ENUM*
    - **ENUM_NAME**
    - **ENUM_FULL_NAME**
    - *ENUM_VALUE*
        - **ENUM_VALUE_NAME**
        - **ENUM_VALUE_SHORT_NAME**
        - **ENUM_VALUE_NUMBER**
        - *ENUM_VALUE_UNSPECIFIED*
        - *ENUM_VALUE_SPECIFIED*
- *FIELD*
    - *HAS_FIELDS*
    - *NO_FIELDS*
    - **FIELD_NAME**
    - **FIELD_TYPE**
    - **FIELD_TAG_NUMBER**
    - **FIELD_INDEX**
    - *FIELD_COMMENTS*
        - **FIELD_COMMENTS_LEADING**
        - **FIELD_COMMENTS_TRAILING**
    - *REPEATED*
    - *SINGULAR*
    - *OPTIONAL*
    - *REQUIRED*
    - *NULLABLE*
    - *NON_NULLABLE*
    - *MAP*
        - **MAP_KEY_TYPE**
    - *ONEOF*
        - **ONEOF_NAME**
        - **ONEOF_FULL_NAME**
    - *WRITABLE*
    - *FIELD_TYPE_BASIC*
    - *FIELD_TYPE_ENUM*
        - **ENUM_FIELD_ENUM_NAME**
        - **ENUM_FIELD_ENUM_FULL_NAME**
        - **ENUM_FIELD_OBJC_ENUM_NAME**
    - *FIELD_TYPE_BOOL*
    - *FIELD_TYPE_NUMBER*
        - **NUMBER_FIELD_TYPE**
        - **NUMBER_FIELD_CPP_TYPE**
        - **NUMBER_FIELD_BITS**
        - *NUMBER_FIELD_SIGNED*
        - *NUMBER_FIELD_UNSIGNED*
        - *NUMBER_FIELD_INTEGRAL*
        - *NUMBER_FIELD_FLOATING_POINT*
    - *FIELD_TYPE_FLOATING_POINT*
        - **FLOATING_POINT_FIELD_FIXED_ENCODING_WIDTH**
        - **FLOATING_POINT_FIELD_PRECISION**
    - *FIELD_TYPE_STRING*
        - **STRING_FIELD_MAX_LENGTH**
        - **STRING_FIELD_ALLOWED_CHARACTERS**
    - *FIELD_TYPE_BYTES*
        - **BYTES_FIELD_MAX_LENGTH**
    - *FIELD_TYPE_MESSAGE*
        - **MESSAGE_FIELD_TYPE**
        - **MESSAGE_FIELD_PACKAGE**
        - **MESSAGE_FIELD_FULL_TYPE**
        - **MESSAGE_FIELD_JAVA_CLASS**
        - **MESSAGE_FIELD_OBJC_CLASS**
        - *MESSAGE_FIELD_WRAPPED*
            - *WRAPPED_FIELD_NUMBER*
            - *WRAPPED_FIELD_INT32*
            - *WRAPPED_FIELD_UINT32*
            - *WRAPPED_FIELD_INT64*
            - *WRAPPED_FIELD_UINT32*
            - *WRAPPED_FIELD_BOOL*
            - *WRAPPED_FIELD_FLOAT*
            - *WRAPPED_FIELD_DOUBLE*
            - *WRAPPED_FIELD_BYTES*
            - *WRAPPED_FIELD_STRING*
            - **WRAPPED_FIELD_TYPE**
        - *MESSAGE_FIELD_NON_WRAPPED*
        - *MESSAGE_FIELD_SPECIAL_TIMESTAMP*
            - *TIMESTAMP_FIELD_SIGNED*
            - *TIMESTAMP_FIELD_UNSIGNED*
            - **TIMESTAMP_FIELD_WIDTH**
            - **TIMESTAMP_FIELD_PRECISION**
        - *MESSAGE_FIELD_SPECIAL_RESOURCE_ID*
        - *MESSAGE_FIELD_NON_SPECIAL*
        - *MESSAGE_FIELD_IDENTIFIER*
        - *MESSAGE_FIELD_NON_IDENTIFIER*
- *TRAIT_COMMAND*
    - **COMMAND_INDEX**
    - **COMMAND_NAME**
    - *HAS_COMPLETION_EVENT*
    - *NO_COMPLETION_EVENT*
        - **COMPLETION_EVENT**
- *TRAIT_EVENT*
    - **EVENT_INDEX**
    - **EVENT_NAME**
    - **EVENT_FULL_NAME**
    - **EVENT_ID**
- *TRAIT_RESPONSE_EVENT*
    - **EVENT_INDEX**
    - **EVENT_NAME**
    - **EVENT_FULL_NAME**
    - **EVENT_ID**
- *PATH_HANDLE*
    - **PATH_HANDLE_NAME**
    - **PATH_HANDLE_NUMBER**
    - **PATH_HANDLE_PARENT_NAME**
    - **PATH_HANDLE_FIELD_NAME**
    - **PATH_HANDLE_FIELD_TAG_NUMBER**
    - **PATH_HANDLE_FIELD_IDL_TYPE**
    - **PATH_HANDLE_FIELD_TLV_TYPE**
- **PATH_HANDLE_MAX_DEPTH**
- **PATH_HANDLE_START_OFFSET**
- *PATH_HANDLE_EXTENDS_TRAIT*
    - **FULL_NAME**
    - **FULL_CPP_NAME**
- *PATH_HANDLE_NO_EXTENDS_TRAIT*
- *IFACE*
    - **VENDOR_ID**
    - **IFACE_VERSION**
- *IFACE_IMPLEMENTATIONS*
- *IFACE_IMPL*
    - **IFACE_IMPL_NAME**
    - **IFACE_IMPL_TYPE**
    - *IFACE_IMPL_TRAIT_MAPPING*
      - **IFACE_IMPL_FROM_TRAIT**
      - **IFACE_IMPL_TO_TRAIT**


### CAN_UPDATE

This section exists if the Trait or Resource has fields that can be modified.
This means that there are commands, they can be filtered, the state can be
updated, etc. This is the common case.

### CANNOT_UPDATE

This section exists if the Trait or Resource does not have any fields that can
be modified. This means that there are no commands, no filtering, and no state
to modify. This is often the case with sensors, as they can provide data but
there is no way to modify the data.

### PACKAGE

This is the name of the package that the proto message is in. For example,
"weave.trait.security"

### PACKAGE_PART

This section is included for each part (dot-separated) of the package. For example,
the package "weave.trait.security" will produce sections for "weave", "trait", and "security".

#### PACKAGE_PART

The package part.

### JAVA_CLASS

This is the fully qualified class name for the message that will be generated for java.

### IMPORT

This section is included if the proto has import statements

#### IMPORT

This is the full package and type for the import. For example
"weave.common.Timer"

#### IMPORT_PACKAGE

This is the package for the import without the type. For example
"weave.common"

#### IMPORT_NAME

This is the type name for the import without the package. For example
"Timer"

### NAME

This is the name of the proto message that code is being generated from. For
example "LockEvent"

### FULL_NAME

This is the full name of the proto message that code is being generated from.
For example "weave.trait.security.LockTrait.LockEvent"

### TYPE_URL

This is the type URL (see any.proto) of the proto message that code is being
generated from. For example
"type.nestlabs.com/weave.trait.security.LockTrait.LockEvent"

### TRAIT_NAME

This is the name of the trait that the class is a part of. For example
"LockTrait".

### SOURCE_FILEPATH

This is the relative path to the proto file from the base of the idl. For
example "weave/trait/security/lock_trait.proto"

### SOURCE_FILENAME

This is the filename for the proto file. For example
"lock_trait.proto"

### TRAIT

This section is included if the message is a Trait (as opposed to a Resource,
Command, Event, etc).

#### TRAIT_ID

This is the wdl trait ID found in the file options for the Trait. It is
formatted in hex with a leading 0x. For example "0x1234"

#### VENDOR_ID

This is the wdl vendor ID found in the file options for the Trait. It is
formatted in hex with a leading 0x. For example "0xABCD"

#### TRAIT_VERSION

This is the wdl version found in the file options for the Trait. For example "1"

### RESOURCE

This section is included if the message is a Resource (as opposed to a Trait,
Command, Event, etc).

#### VENDOR_ID

This is the wdl vendor ID found in the file options for the Resource. It is
formatted in hex with a leading 0x. For example "0xABCD"

#### RESOURCE_VERSION

This is the wdl version found in the file options for the Resource. For example
"1"

### COMMAND

This section is included if the message is a Command (as opposed to a Trait,
Resource, Event, etc).

#### HAS_COMPLETION_EVENT

This section is included if the command has a completion event defined.

#### NO_COMPLETION_EVENT

This section is included if the command has no completion event defined.

#### COMPLETION_EVENT

This is the name of the completion event if there is one, without the package.
For example "InviteGuestResponse".

### EVENT

This section is included if the message is an Event (as opposed to a Trait,
Resource, Command, etc).

### MESSAGE

This section is included is the message is not any recognized special type of
message (Trait, Resource, etc) but just a regular proto message.

### DEPENDENCY

This section is included if the message is included in code generation because
of a message of special type (Trait, Command) referencing it. This can be used
to generate extra code required to manipulate this message in a public
interface.

### NO_FIELDMASK_REF

This section is included if the message does not reference
google.protobuf.FieldMask. This is special-cased because many messages may not
directly depend on FieldMask yet we need to use FieldMask in the generated code,
but other messages do directly depend on FieldMask and we don't want to
duplicate the dependency.

### SUB_MESSAGE_TYPE

This section is included once for every message type referenced by this message.
This is different from the similar structure in FIELD_TYPE_MESSAGE because there
can be multiple fields with the same message type and relying on that structure
could result in duplicate references to sub-message types. This section is the
set of all unique types in those fields.

#### SUB_MESSAGE_TYPE

This is the type name for the sub message without the package. For example
"Timer"

#### SUB_MESSAGE_PACKAGE

This is the package for the sub message without the type. For example
"weave.common"

#### SUB_MESSAGE_FULL_TYPE

This is the full package and type name or the sub message. For example
"weave.common.Timer"

### ENUM

This section is included for every Enum referenced by fields in the message. For
example, if a Trait has a field of enum type Blob, this section will be included
for Blob. Duplicate enum names will be ignored, so it is not a problem to have
more than one field with the same enum type. Enums defined in the message but
not references will not be included here.

#### ENUM_NAME

This is the name of the enum. For example "LockState"

#### ENUM_FULL_NAME

This is the fully qualified name of the enum. For example
"weave.trait.security.LockState"

#### ENUM_VALUE

This section is included for every value defined in the enum.

##### ENUM_VALUE_NAME

This is the name of the enum value, e.g. "LOCK_STATE_LOCKED"

##### ENUM_VALUE_SHORT_NAME

This is the name of the enum value, but with the enum_name removed if present, e.g. "LOCKED"

##### ENUM_VALUE_NUMBER

This is the number assigned to the enum value, for example "2"

##### ENUM_VALUE_UNSPECIFIED

This section is included if the enum value is 0 (UNSPECIFIED).

##### ENUM_VALUE_SPECIFIED

This section is included if the enum value is not 0 (UNSPECIFIED).

### FIELD

This section is included for every field defined in the message.

#### HAS_FIELDS

This section is included if there is at least one field.

#### NO_FIELDS

This section is included if there are no fields.

#### FIELD_NAME

This is the field name of the field, for example "lockState"

#### FIELD_TYPE

This is the protobuf type of the field. For enum types it is the name of the
enum. This is commonly used with the x-type modifier to generate
language-specific type names for the field for basic types.

#### FIELD_TAG_NUMBER

This is the proto tag number of the field. For example "1"

#### FIELD_INDEX

This is the index of this field within the message's field array.

#### FIELD_COMMENTS

This section is included if the field has either a leading or trailing comment.

##### FIELD_COMMENTS_LEADING

This the the leading comment for the field

##### FIELD_COMMENTS_TRAILING

This the the trailing comment for the field. This is not typically used.

#### REPEATED

This section is included if the field is a repeated field.

#### SINGULAR

This section is included if the field is not a repeated field nor a map

#### OPTIONAL

This section is included if the field is a optional field.

#### REQUIRED

This section is included if the field is a required (non-optional) field.

#### NULLABLE

This section is included if the field is a nullable field.

#### NON_NULLABLE

This section is included if the field is a non-nullable field.

#### MAP

This section is included if the field is a map field.

##### MAP_KEY_TYPE

This is the protobuf type of the key for the map field.

#### ONEOF

This section is included if the field is contained inside a oneof.

##### ONEOF_NAME

This is the name of the oneof that contains the field.

##### ONEOF_FULL_NAME

This is the full name of the oneof that contains the field.

#### WRITABLE

This section is included if the field can be written. This is not included if
the field has a wdl.field option specifying writable as READ_ONLY.

#### FIELD_TYPE_BASIC

This section is included if the field has a non-message type.

#### FIELD_TYPE_ENUM

This section is included if the field has an enum type.

##### ENUM_FIELD_ENUM_NAME

This is the name of the enum that the field is typed with. For example
"LockState"

##### ENUM_FIELD_ENUM_FULL_NAME

This is the full name of the enum that the field is typed with. For example
"weave.trait.security.LockState"

##### ENUM_FIELD_OBJC_ENUM_NAME

This is the full name of the Objective-C enum that the field is typed with. For example
"BoltLockTrait_BoltState"

#### FIELD_TYPE_BOOL

This section is included if the field has a bool type.

#### FIELD_TYPE_NUMBER

This section is included if the field has a numerical type.

##### NUMBER_FIELD_TYPE

This is the proto-style type of the number. For example "int64" or "uint32"

##### NUMBER_FIELD_CPP_TYPE

This is the C++ style type of the number that includes any constraints. For example "uint16_t"

##### NUMBER_FIELD_BITS

This is the number of bits in the number. For example "32"

##### NUMBER_FIELD_SIGNED

This section is included if the number is signed.

##### NUMBER_FIELD_UNSIGNED

This section is included if the number is unsigned.

##### NUMBER_FIELD_INTEGRAL

This section is included if the number is integral.

##### NUMBER_FIELD_FLOATING_POINT

This section is included if the number is floating point.

##### FIELD_TYPE_FLOATING_POINT

This section is included if the number is floating point.

#### FIELD_TYPE_STRING

This section is included if the field has a string type.

#### FIELD_TYPE_BYTES

This section is included if the field has a bytes type.

#### FIELD_TYPE_MESSAGE

This section is included if the field has a message type.

##### MESSAGE_FIELD_TYPE

This is the short name of the message type that the field is typed with, for
example "CountdownTimer"

##### MESSAGE_FIELD_PACKAGE

This is the package of the message type that the field is typed with, for
example "weave.common"

##### MESSAGE_FIELD_FULL_TYPE

This is the full name of the message that the field is typed with, for example
"weave.common.CountdownTimer"

##### MESSAGE_FIELD_JAVA_CLASS

This is the fully qualified Java class for this message type

##### MESSAGE_FIELD_OBJC_CLASS

This is the fully qualified Objective C class for this message type

##### FIELD_TYPE_TIMESTAMP

This section is included if the field has a google.protobuf.timestamp type.

### FIELD_TYPE_WRAPPED_INT32

This section is included if the field has a google.protobuf.Int32Value type.
Also includes sub tags of of FIELD_TYPE_NUMBER.

### FIELD_TYPE_WRAPPED_UINT32

This section is included if the field has a google.protobuf.UInt32Value type.
Also includes sub tags of of FIELD_TYPE_NUMBER.

### FIELD_TYPE_WRAPPED_INT64

This section is included if the field has a google.protobuf.Int64Value type.
Also includes sub tags of of FIELD_TYPE_NUMBER.

### FIELD_TYPE_WRAPPED_UINT64

This section is included if the field has a google.protobuf.UInt64Value type.
Also includes sub tags of of FIELD_TYPE_NUMBER.

### FIELD_TYPE_WRAPPED_FLOAT

This section is included if the field has a google.protobuf.FloatValue type.
Also includes sub tags of of FIELD_TYPE_NUMBER and FIELD_TYPE_FLOATING_POINT.

### FIELD_TYPE_WRAPPED_DOUBLE

This section is included if the field has a google.protobuf.DoubleValue type.
Also includes sub tags of of FIELD_TYPE_NUMBER and FIELD_TYPE_FLOATING_POINT.

### FIELD_TYPE_WRAPPED_BYTES

This section is included if the field has a google.protobuf.BytesValue type.
Also includes sub tags of of FIELD_TYPE_BYTES.

### FIELD_TYPE_WRAPPED_STRING

This section is included if the field has a google.protobuf.StringValue type.
Also includes sub tags of of FIELD_TYPE_STRING.

### FIELD_TYPE_WRAPPED_BOOL

This section is included if the field has a google.protobuf.BoolValue type.
Also includes sub tags of of FIELD_TYPE_BOOL.

### TRAIT_COMMAND

This section is included for every command defined in the same trait as the
message. This can be used to enumerate the commands supported by a Trait. This
was previously called FILE_COMMAND, which can still be used for backwards
compatibility, but is deprecated in favor of TRAIT_COMMAND.

#### COMMAND_INDEX

This is the index into the set of commands defined in the same file, starting
with 1. For example "2"

#### COMMAND_NAME

This is the name of the command. For example "AddPincodeCommand"

#### HAS_COMPLETION_EVENT

This section is included if the command has a completion event defined.

#### NO_COMPLETION_EVENT

This section is included if the command has no completion event defined.

##### COMPLETION_EVENT

This is the name of the completion event if there is one, without the package.
For example "InviteGuestResponse".

### TRAIT_EVENT

This section is included for every non-response event defined in the same trait as the
message. This can be used to enumerate the events supported by a Trait. This
used to be called FILE_EVENT, which is still supported for backwards
compatibility, but deprecated in favor of TRAIT_EVENT.

### TRAIT_RESPONSE_EVENT

This section is included for every response event defined in the same trait as the
message.

#### EVENT_INDEX

This is the index into the set of event defined in the same file, starting with
1. For example "2"

#### EVENT_NAME

This is the name of the event. For example "BoltActuatorStateChangeEvent"

#### EVENT_FULL_NAME

This is the full name of the event. For example
"weave.trait.security.BoltLockTrait.BoltActuatorStateChangeEvent"

#### EVENT_ID

This is the wdl event ID found in the event options. It is
formatted in hex with a leading 0x. For example "0x1234"

### PATH_HANDLE

This section is included for every property field defined in a trait. If any
fields are STRUCTs, PATH_HANDLE sections are also created for the nested fields,
recursively.

#### PATH_HANDLE_NAME

The name of the path handle. This is the name of the field, prefixed with the
names of parent fields, if any.

#### PATH_HANDLE_NUMBER

The number of the path handle. This starts with 1 for the root of the trait,
then increments for each field in the trait, including all nested fields.

#### PATH_HANDLE_PARENT_NAME

The PATH_HANDLE_NAME for the parent of this field.

#### PATH_HANDLE_FIELD_NAME

The FIELD_NAME for this field.

#### PATH_HANDLE_FIELD_TAG_NUMBER

The FIELD_TAG_NUMBER for this field.

#### PATH_HANDLE_FIELD_IDL_TYPE

The IDL type for this field.

Basic types: proto primitive type
Wrapped types: proto wrapped type
Enums: full name of enum
Arrays: "repeated"
Structs: full name of message
Standard WDL types: full name of message
Unions: full name of message
Dictionaries: not yet supported

proto primitive types: int32 / uint32 / int64 / uint64 / float / double / string / bool / bytes

#### PATH_HANDLE_FIELD_TLV_TYPE

The Weave TLV type for this field.

Basic types: TLV primitive type
Wrapped types: TLV primitive type
Enums: "unsigned int"
Arrays: "array"
Structs: "structure"
Standard WDL types: varies by type
Unions: "union"
Dictionaries: not yet supported

TLV primitive types: int / unsigned int / float / string / bool / bytes

### PATH_HANDLE_MAX_DEPTH

The maximum depth of nested fields in the trait.

### PATH_HANDLE_START_OFFSET

The starting path handle number in the trait. This is 2 for a base trait.

### PATH_HANDLE_EXTENDS_TRAIT

This section is include if the trait extends a parent trait.

#### FULL_NAME

The full name of the parent trait. For example "weave.trait.power.PowerSourceTrait"

#### FULL_CPP_NAME

The full C++ name of the parent trait. For example "Weave::Trait::Power::PowerSourceTrait"

### PATH_HANDLE_NO_EXTENDS_TRAIT

This section is include if the trait is a base trait.


## Message dependencies

If a field has a message type, the resulting output will likely depend on code
generation for that message type as well. Because of this, the code generator
will automatically generate code for all message types it encounters
recursively. Message types are deduped, so cycles are allowed.

As a result, many files may be output for a single requested message. For
example, generating weave.trait.security.LockTrait could output both
weave/trait/security/lock-trait.js as well as weave/common/countdown-timer.js,
as that message is referenced by LockTrait. This automatic dependency generation
prevents the user from having to manually manage all dependencies in the IDL.

Dependencies of Traits and Commands included this way will have the DEPENDENCY
section added at the top level.

## Modifiers

The code generator has a number of modifiers built-in that can be used to modify
the value of a tag before it is inserted. Modifiers are invoked by appending a :
onto the end of the tag name and then the name of the modifier. Further modifiers
can be added with another : and modifier name. If the modifier takes an
argument, the argument is specified by appending an = to the end of the modifier
name followed by the value of the argument.

### x-snake: Snake case

The x-snake modifier takes a field name or similar value and converts it to
snake case, defined as words separated by underscores. The snake case modifier
takes an argument whose first character can be "u" or "l", where "u" means that
all alphabetic characters will be converted to upper case and "l" means that all
alphabetic characters will be converted to lower case. Any characters after the
first in the argument will be used as the separator between words, with _ used
as the separator if no additional characters are given.

Examples:

- "HelloWorld":x-snake=l -> "hello_world"
- "HelloWorld":x-snake=u -> "HELLO_WORLD"
- "myValue1234":x-snake=l -> "my_value1234"
- "HelloWorld":x-snake=l- -> "hello-world"
- "SomeChildFields":x-snake=l()-> -> "some()->child()->fields"

### x-camel: Camel case

The x-camel modifier takes a field name or similar value and converts it to
camel case, defined as the first letter of every word capitalized. The camel
case modifier takes an argument whose value can be "u" or "l", where "u" means
that the first letter of the first word should be capitalized while "l" means
that it should be lowercase.

Examples:

- "hello_world":x-camel=l -> "helloWorld"
- "hello_world":x-camel=u -> "HelloWorld"
- "hello_123_WorldONE":x-camel=l -> "hello123WorldOne"

### x-trim: Trim trailing text

The x-trim modifier removes some trailing text from the value if the value
matches. The trim modifier takes as an argument the text that is expected to be
at the end of the value and should be removed.

Examples:

- "HelloWorld":x-trim=World -> "Hello"
- "HelloWorld":x-trim=Hello -> "HelloWorld"

### x-replace: Replace strings

The x-replace modifier replaces all instances of one string in the value with
another string. The replace modifier takes as an argument the from and to
strings, separated by a comma.

Examples:

- "One.Two.Three":x-replace=.,- -> "One-Two-Three"
- "One.Two.Three":x-replace=T,A-T -> "One.A-Two.A-Three"

### x-type: Convert to platform types

The x-type modifier is the only place where platform-specific knowledge is
allowed. It is used to convert protobuf types into platform-specific types. It
is hardcoded with a mapping for each platform. The type modifier takes as an
argument the platform to convert the type to.

Examples:

- "int64":x-type=js -> "number"
- "bytes":x-type=js -> "string"
