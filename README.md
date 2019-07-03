[![OpenWeave][ow-logo]][ow-wdlc-repo]
<br/>
<br/>
[![Build Status][ow-wdlc-travis-svg]][ow-wdlc-travis]

---

# What is OpenWeave?

<img src="https://github.com/openweave/openweave-core/raw/master/doc/images/ow-logo-weave.png" width="200px" align="right">

Weave is the network application layer that provides a secure, reliable
communications backbone for Nest's products. OpenWeave is the open source
release of Weave.

At Google, we believe the core technologies that underpin connected
home products need to be open and accessible. Alignment around common
fundamentals will help products securely and seamlessly communicate
with one another. Google's first open source release was our
implementation of Thread, OpenThread. OpenWeave can run on OpenThread,
other IPv6-bearing network links, or Bluetooth Low Energy, and is
another step in the direction of making our core technologies more
widely available.

# What is OpenWeave WDLC?

This package makes available the Weave Data Language (WDL) compiler
(WDLC). WDL is Weave's publish and subscribe schema language. The WDLC
compiler can be used to compile (i.e., validate and code generate)
schema written against the WDL specification.

Some notable features of WDLC include:

  * Generate code against user-provided, language- and run time-specific
    templates that conform to WDL template syntax.
  * Compare a body of schema against a previous revision of schema to run
    additional validations.

[ow-wdlc-repo]: https://github.com/openweave/openweave-wdlc
[ow-logo]: https://github.com/openweave/openweave-core/raw/master/doc/images/ow-logo.png
[ow-logo-weave]: https://github.com/openweave/openweave-core/raw/master/doc/images/ow-logo-weave.png
[ow-wdlc-travis]: https://travis-ci.org/openweave/openweave-wdlc
[ow-wdlc-travis-svg]: https://travis-ci.org/openweave/openweave-wdlc.svg?branch=master

# Getting started with OpenWeave WDLC

## Building WDLC

If you are not using a prebuilt distribution of WDLC, building WDLC
should be a straightforward, two-step process:

    % ./configure
    % make

Although not strictly necessary, the additional step of sanity checking
the build results is recommended:

    % make check

The `configure` step can also set the installation prefix, overriding
the default "/usr/local". Creating an arbitrarily relocatable WDLC
installation might, for example, specify `--prefix=/`. See "Installing
WDLC" below for more information.

### Dependencies

The `configure` step recognizes and accepts both the `PROTOC` and `PYTHON`
enviroment variables, which may also be specified after `configure` on
the command line. These may be used to override the instance of the
Google Protocol Buffers (protobuf) Compiler, protoc, and the Python
interpreter, python, respectively, otherwise found via the PATH
environment variable.

WDLC depends on and requires a version of protoc between
[3.5.1](https://github.com/protocolbuffers/protobuf/releases/tag/v3.5.1)
and
[3.7.1](https://github.com/protocolbuffers/protobuf/releases/tag/v3.7.1),
inclusive and python 2.7. Python later than 2.7, including Python 3,
is not supported by WDLC at this time.

In addition, the following Python packages are required:

  * virtualenv
  * pip

If you want to modify or otherwise maintain the OpenWeave WDLC build
system, see "Maintaining WDLC" below for more information.

#### Linux

On Debian-based Linux distributions such as Ubuntu, these collective
dependencies can be satisfied with the following:

    % sudo apt-get install protobuf-compiler python2.7 python-pip python-virtualenv

#### Mac OS X

On Mac OS X, these collective dependencies can be installed and satisfied using
[Brew](https://brew.sh/):

    % brew install protobuf

Mac OS X, including Mojave, supports Python 2.7 by default. However, the Python
pip and virtualenv dependencies can be installed and satisfied as follows:

  * [pip](https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py)
  * [virtualenv](https://virtualenv.pypa.io/en/stable/installation)

## Installing WDLC

To install WDLC for your use simply invoke:

    % make install

to install WDLC in the location indicated by the --prefix `configure`
option (default "/usr/local"). If you intended an arbitrarily
relocatable WDLC installation and passed `--prefix=/` to `configure`,
then you might use DESTDIR to, for example install WDLC in your user
directory:

    % make DESTIDIR="${HOME}" install

Note that WDLC allows the installation of multiple minor versions of
itself in parallel with "versioned" directories under bin, include,
lib, and share. For example, for WDLC version 1.0.7:

  * *${DESTDIR}${prefix}bin/wdlc-1.0*
  * *${DESTDIR}${prefix}include/wdlc-1.0*
  * *${DESTDIR}${prefix}lib/wdlc-1.0*
  * *${DESTDIR}${prefix}share/wdlc-1.0*

where the actual WDLC executable would be found under
`${DESTDIR}${prefix}bin/wdlc-1.0/wdlc`.

If it would not overwrite an existing installation, WDLC will also
install a non-versioned convenience binary symbolic link to
`${DESTDIR}${prefix}bin/wdlc`.

## Using WDLC

Please run `wdlc --help` to see a full list of options.

*Validate device identity trait:*

    % wdlc --check --output ./build -I ~/schema/openweave-schema-vendor-common ~/schema/openweave-schema-vendor-common/weave/trait/description/device_identity_trait.proto

*Code-generate for Weave Device C++:*

    % wdlc --gen weave-device-cpp --output ./build -I ~/schema/openweave-schema-vendor-common ~/schema/openweave-schema-vendor-common/weave/trait/description/device_identity_trait.proto

*Code-generate using base protoc C++ template:*

    % wdlc --gen cpp --output ./build -I ~/schema/openweave-schema-vendor-common ~/schema/openweave-schema-vendor-common/weave/trait/description/device_identity_trait.proto

*Validate all traits in a given folder:*

    % wdlc --check --output ./build -I ~/schema/openweave-schema-vendor-common ~/schema/openweave-schema-vendor-common/weave/trait/located

*Code-generate schema + dependencies:*

    % wdlc -I ~/openweave-schema-vendor-nest -I ~/openweave-schema-vendor-common --gen weave-device-cpp --gen_dependencies --output ./build ~/openweave-schema-vendor-nest/nest/resource/nest_detect_resource.proto ~/openweave-schema-vendor-nest/nest/resource/nest_guard_resource.proto

## Maintaining WDLC

If you want to maintain, enhance, extend, or otherwise modify WDLC, it
is likely you will need to change its build system, based on GNU
autotools, in some circumstances.

After any change to the WDLC build system, including any *Makefile.am*
files or the *configure.ac* file, you must run the `bootstrap` or
`bootstrap-configure` (which runs both `bootstrap` and `configure` in
one shot) script to update the build system.

### Dependencies

Due to its leverage of GNU autotools, if you want to modify or
otherwise maintain the OpenWeave WDLC build system, the following
additional packages are required and are invoked by `bootstrap`:

  * autoconf
  * automake
  * libtool

#### Linux

On Debian-based Linux distributions such as Ubuntu, these dependencies
can be satisfied with the following:

    % sudo apt-get install autoconf automake libtool

#### Mac OS X

On Mac OS X, these dependencies can be installed and satisfied using
[Brew](https://brew.sh/):

    % brew install autoconf automake libtool

## Implementation Details

Today, WDLC leverages the Google Protocol Buffers (protobuf) Compiler
(protoc) as its backend with a custom Python plugin used to interpret
the protoc intermediate output and then to subsequently validate and
code generate against input schema.

Code generation, today, is handled via the Python Jinja2 module, using
a template format specific to WDL.

# Need help?

There are numerous avenues for OpenWeave support:
* Bugs and feature requests — [submit to the Issue Tracker](https://github.com/openweave/openweave-core/issues)
* Stack Overflow — [post questions using the openweave tag](http://stackoverflow.com/questions/tagged/openweave)
* Google Groups — discussion and announcements at [openweave-users](https://groups.google.com/forum/#!forum/openweave-users)

The openweave-users Google Group is the recommended place for users to
discuss OpenWeave and interact directly with the OpenWeave team.

# Directory Structure

The OpenWeave WDLC repository is structured as follows:

| File / Folder | Contents |
|----|----|
| `aclocal.m4` | GNU autotools auto-generated file containing autoconf macros used by the OpenWeave WDLC build system. |
| `backend` | The compiler backend that effects the actual parsing, validation, and code generation. |
| `bootstrap` | GNU autotools bootstrap script for the OpenWeave WDLC build system. |
| `bootstrap-configure` | Convenience script that will bootstrap the OpenWeave WDLC build system, via `bootstrap`, and invoke `configure`.|
| `build/` | OpenWeave WDLC-specific build system support content.|
| `CHANGELOG` | Description of changes to OpenWeave from release-to-release.|
| `configure` | GNU autotools configuration script for OpenWeave.|
| `configure.ac` | GNU autotools configuration script source file for OpenWeave WDLC.|
| `CONTRIBUTING.md` | Guidelines for contributing to OpenWeave WDLC.|
| `.default-version` | Default OpenWeave WDLC version if none is available via source code control tags, `.dist-version`, or `.local-version`.|
| `include` | GNU autotools configuration header (unused).|
| `LICENSE` | OpenWeave WDLC license file (Apache 2.0).|
| `Makefile.am` | Top-level GNU automake makefile source.|
| `Makefile.in` | Top-level GNU autoconf makefile source.|
| `README.md` | This file.|
| `test/` | Test schema used to exercise and validate WDL syntax code generation.|
| `third_party/` | Third-party code used by OpenWeave WDLC.|
| `wdl/` | Core WDL schema data types and defintions.|
| `wdlc.sh.in` | WDL front end implementation template.|
| `weave/` | Additional, common WDL schema data types and definitions.|

# Contributing

We would love for you to contribute to OpenWeave WDLC and help make it even
better than it is today! See the [CONTRIBUTING.md](./CONTRIBUTING.md)
file for more information.

# Versioning

OpenWeave WDLC follows the [Semantic Versioning guidelines](http://semver.org/) for release cycle transparency and to maintain backwards compatibility.

# License

**License and the Weave and OpenWeave Brands**

The OpenWeave software is released under the [Apache 2.0
license](./LICENSE), which does not extend a license for the use of
the Weave and OpenWeave name and marks beyond what is required for
reasonable and customary use in describing the origin of the software
and reproducing the content of the NOTICE file.

The Weave and OpenWeave name and word (and other trademarks, including
logos and logotypes) are property of Google LLC. Please refrain
from making commercial use of the Weave and OpenWeave names and word
marks and only use the names and word marks to accurately reference
this software distribution. Do not use the names and word marks in any
way that suggests you are endorsed by or otherwise affiliated with
Nest without first requesting and receiving a written license from us
to do so. See our [Trademarks and General
Principles](https://nest.com/legal/ip-and-other-notices/tm-list/) page
for additional details. Use of the Weave and OpenWeave logos and
logotypes is strictly prohibited without a written license from us to
do so.
