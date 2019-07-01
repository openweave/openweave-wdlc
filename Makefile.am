#
#    Copyright (c) 2019 Google LLC. All Rights Reserved.
#    Copyright (c) 2016-2018 Nest Labs Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

#
#    Description:
#      This file is the GNU automake template for the Weave Data
#      Language (WDL) Compiler (WDLC).
#

include $(abs_top_nlbuild_autotools_dir)/automake/pre.am

.DEFAULT_GOAL                            := all

AM_MAKEFLAGS                              = --no-print-directory --silent

SUBDIRS                                   = \
    third_party                             \
    include                                 \
    backend                                 \
    codegen                                 \
    test                                    \
    $(NULL)

EXTRA_DIST                                = \
    .default-version                        \
    bootstrap                               \
    bootstrap-configure                     \
    build/scripts/install_python_modules.sh \
    build/scripts/setup_compiler.sh         \
    build/scripts/setup_venv.sh             \
    build/scripts/update_googleapis.sh      \
    $(srcdir)/third_party/nlbuild-autotools \
    wdl/data_access.proto                   \
    wdl/vendors.proto                       \
    wdl/wdl_options.proto                   \
    wdlc.sh.in \
    weave/common/command_response_status.proto \
    weave/common/identifiers.proto \
    weave/common/resource_type.proto \
    weave/common/string_ref.proto \
    weave/common/time.proto \
    weave/common/units.proto \
    $(NULL)

BUILT_SOURCES                             = \
    .local-version                          \
    $(NULL)

DISTCLEANFILES                            = \
    .local-version                          \
    $(NULL)

dist_tar_ARCHIVE                          = $(TAR) -ch --format=posix -f -

dist_tgz_ARCHIVE                          = $(dist_tar_ARCHIVE)
dist_tgz_COMPRESS                         = $(GZIP) --best -c

dist_txz_ARCHIVE                          = $(dist_tar_ARCHIVE)
dist_txz_COMPRESS                         = $(XZ) --extreme -c

TGZ_EXTENSION                            := .tar.gz
TXZ_EXTENSION                            := .tar.xz

BINDIST_TARGETS                          ?= bindist-tgz bindist-xz

#
# Package version files:
#
# .default-version - The default package version. This file is ALWAYS checked
#                    in and should always represent the current baseline
#                    version of the package.
#
# .dist-version    - The distributed package version. This file is NEVER
#                    checked in within the upstream repository, is auto-
#                    generated, and is only found in the package distribution.
#
# .local-version   - The current source code controlled package version. This
#                    file is NEVER checked in within the upstream repository,
#                    is auto-generated, and can always be found in both the
#                    build tree and distribution.
#
# When present, the .local-version file is preferred first, the
# .dist-version second, and the .default-version last.
#

# VERSION_FILE should be and is intentionally an immediate (:=) rather
# than a deferred (=) variable to ensure the value binds once and only once
# for a given MAKELEVEL even as .local-version and .dist-version are created
# during makefile execution.

VERSION_FILE                      := $(if $(wildcard $(builddir)/.local-version),$(builddir)/.local-version,$(if $(wildcard $(srcdir)/.dist-version),$(srcdir)/.dist-version,$(srcdir)/.default-version))

#
# Override autotool's default notion of the package version variables.
# This ensures that when we create a source distribution the
# version is always the current version, not the package bootstrap
# version.
#
# The two-level variables and the check against MAKELEVEL ensures that
# not only can the package version be overridden from the command line
# but also when the version is NOT overridden that we bind the version
# once and only once across potential sub-makes to prevent the version
# from flapping as VERSION_FILE changes.
#

export MAYBE_WDLC_VERSION := $(if $(filter 0,$(MAKELEVEL)),$(shell $(CAT) $(VERSION_FILE) 2> /dev/null),$(MAYBE_WDLC_VERSION))

VERSION                   ?= $(MAYBE_WDLC_VERSION)
WDLC_VERSION               = $(VERSION)
PACKAGE_VERSION            = $(WDLC_VERSION)

WDLC_VERSION_REGEXP       := \([0-9]\{1,\}\)\.\([0-9]\{1,\}\)\.*\([0-9]\{1,\}\)*\(a\|b\|d\|rc\)*\([0-9]\{1,\}\)*-*\(.*\)*$$
WDLC_VERSION_EXTRACT       = $(shell echo "$(WDLC_VERSION)" | $(SED) -n -e "s/$(WDLC_VERSION_REGEXP)/\$1/gp")
WDLC_VERSION_MAJOR         = $(call WDLC_VERSION_EXTRACT,1)
WDLC_VERSION_MINOR         = $(call WDLC_VERSION_EXTRACT,2)
WDLC_VERSION_PATCH         = $(call WDLC_VERSION_EXTRACT,3)
WDLC_VERSION_STATUS        = $(call WDLC_VERSION_EXTRACT,4)
WDLC_VERSION_BUILD         = $(call WDLC_VERSION_EXTRACT,5)
WDLC_VERSION_EXTRA         = $(call WDLC_VERSION_EXTRACT,6)

WDLC_BINDIR_COMPONENT      = $(subst ${exec_prefix}/,,${bindir})
WDLC_DATADIR_COMPONENT     = $(subst ${prefix}/,,${datadir})
WDLC_INCLUDEDIR_COMPONENT  = $(subst ${prefix}/,,${includedir})
WDLC_LIBDIR_COMPONENT      = $(subst ${exec_prefix}/,,${libdir})

WDLC_DIRVERSION            = -$(WDLC_VERSION_MAJOR).$(WDLC_VERSION_MINOR)
WDLC_VERSIONDIR_COMPONENT  = wdlc$(WDLC_DIRVERSION)

WDLC_BINDIR                = $(WDLC_BINDIR_COMPONENT)/$(WDLC_VERSIONDIR_COMPONENT)
WDLC_DATADIR               = $(WDLC_DATADIR_COMPONENT)/$(WDLC_VERSIONDIR_COMPONENT)
WDLC_INCLUDEDIR            = $(WDLC_INCLUDEDIR_COMPONENT)/$(WDLC_VERSIONDIR_COMPONENT)
WDLC_LIBDIR                = $(WDLC_LIBDIR_COMPONENT)/$(WDLC_VERSIONDIR_COMPONENT)

WDLC_CODEGENDIR            = $(WDLC_DATADIR)/codegen

BUILDDIR                  := build
RESULTSDIR                := $(BUILDDIR)/results
SCRIPTSDIR                := $(BUILDDIR)/scripts

BACKEND_TARGET             = $(RESULTSDIR)/$(WDLC_LIBDIR)/gwvc
WDLC_TARGET                = $(RESULTSDIR)/$(WDLC_BINDIR)/wdlc

WDLC_LINK_TARGET           = $(RESULTSDIR)/$(WDLC_BINDIR_COMPONENT)/wdlc
WDLC_LINK_SOURCE           = $(WDLC_VERSIONDIR_COMPONENT)/wdlc
WDLC_LINK_COMMAND          = $(LN_S) -f "$(WDLC_LINK_SOURCE)" "$(1)"

DEVICE_CPP_INPUTS          = \
    codegen/weave-device-cpp/templates/common.macros \
    codegen/weave-device-cpp/templates/copyright.inc \
    codegen/weave-device-cpp/templates/enum.common.h \
    codegen/weave-device-cpp/templates/event_struct.cpp.inc \
    codegen/weave-device-cpp/templates/event_struct.h.inc \
    codegen/weave-device-cpp/templates/resource.cpp.h \
    codegen/weave-device-cpp/templates/struct.cpp \
    codegen/weave-device-cpp/templates/struct.cpp.h \
    codegen/weave-device-cpp/templates/trait.c.h \
    codegen/weave-device-cpp/templates/trait.cpp \
    codegen/weave-device-cpp/templates/trait.cpp.h \
    codegen/weave-device-cpp/templates/typespace.c.h \
    codegen/weave-device-cpp/templates/typespace.cpp \
    codegen/weave-device-cpp/templates/typespace.cpp.h \
    $(NULL)

DEVICE_CPP_RESULTS         = $(addprefix $(RESULTSDIR)/$(WDLC_DATADIR)/,$(DEVICE_CPP_INPUTS))

TARGETS                    =            \
    $(BACKEND_TARGET)                   \
    $(WDLC_TARGET)                      \
    $(WDLC_LINK_TARGET)                 \
    $(DEVICE_CPP_RESULTS)               \
    $(NULL)

bindist_tgz_TARGETS        = ${top_builddir}/${PACKAGE}-${nl_filtered_host}-$(VERSION)$(TGZ_EXTENSION)

bindist_xz_TARGETS         = ${top_builddir}/${PACKAGE}-${nl_filtered_host}-$(VERSION)$(TXZ_EXTENSION)

CHECK_TMPDIR              := $(shell mktemp -u -d /tmp/tmp.$(PACKAGE)-$(VERSION)XXXXXX)

#
# check-file-.local-version
#
# Speculatively regenerate .local-version and check to see if it needs
# to be updated.
#
# If WDLC_VERSION has been supplied anywhere other than in this file
# (which is implicitly the contents of .local-version), then use that;
# otherwise, attempt to generate it from the SCM system.
#
# This is called from $(call check-file,.local-version).
#
define check-file-.local-version
if [ "$(origin WDLC_VERSION)" != "file" ]; then        \
    echo "$(WDLC_VERSION)" > "$(2)";                   \
else                                                   \
    $(abs_top_nlbuild_autotools_dir)/scripts/mkversion \
        -b "$(WDLC_VERSION)" "$(top_srcdir)"           \
        > "$(2)";                                      \
fi
endef

#
# check-file-.dist-version
#
# Speculatively regenerate .dist-version and check to see if it needs
# to be updated.
#
# This is called from $(call check-file,.dist-version).
#
define check-file-.dist-version
$(CAT) "$(1)" > "$(2)"
endef

#
# A convenience target to allow package users to easily rerun the
# package configuration according to the current configuration.
#
.PHONY: reconfigure
reconfigure: $(builddir)/config.status
	$(AM_V_at)$(<) --recheck

#
# Version file regeneration rules.
#
.PHONY: force

$(builddir)/.local-version: $(srcdir)/.default-version force

$(distdir)/.dist-version: $(builddir)/.local-version force

$(distdir)/.dist-version $(builddir)/.local-version:
	$(call check-file,$(@F))

dist distcheck distdir install-headers: $(BUILT_SOURCES)

dist-hook: $(distdir)/.dist-version

dist srcdist: | announce-version

srcdist: dist

$(RESULTSDIR)/$(WDLC_CODEGENDIR)/%: codegen/% | $(RESULTSDIR)/$(WDLC_CODEGENDIR)
	$(NL_V_PROGRESS) "COPY" "$(@)"
	$(NL_V_AT)install -D -m 0444 "$(<)" "$(@)"

.PHONY: $(PACKAGE)
$(PACKAGE): all

.PHONY: all
all: .local-version $(TARGETS)

# Announce the version of wdlc being built or installed every time.

all install: | announce-version

.PHONY: announce-version
announce-version:
	$(NL_PROGRESS) "VERSION" "$(WDLC_VERSION)"

# Create a convenience link from the versioned wldc binary directory
# to the build results binary directory.

$(WDLC_LINK_TARGET): $(WDLC_TARGET) | $(RESULTSDIR)/$(WDLC_BINDIR_COMPONENT)
	$(NL_V_PROGRESS) "LN" "$(@)"
	$(NL_V_AT)$(call WDLC_LINK_COMMAND,$(@))

# Preprocess the compiler front end script, substituting specific
# directories and the version.

$(WDLC_TARGET): wdlc.sh.in | $(RESULTSDIR)/$(WDLC_BINDIR)
	$(NL_V_PROGRESS) "COPY" "$(@)"
	$(NL_V_AT)$(SED) \
	    -e "s,@WDLC_BINDIR@,${WDLC_BINDIR},g" \
	    -e "s,@WDLC_DATADIR@,${WDLC_DATADIR},g" \
	    -e "s,@WDLC_INCLUDEDIR@,${WDLC_INCLUDEDIR},g" \
	    -e "s,@WDLC_LIBDIR@,${WDLC_LIBDIR},g" \
	    -e "s,@WDLC_VERSION@,${WDLC_VERSION},g" \
	    < "$(<)" > "$(@)"
	$(NL_V_AT)chmod 775 "$(@)"

# The setup script needs to run protoc, make sure it exists first.

$(top_srcdir)/$(SCRIPTSDIR)/setup_compiler.sh: $(shell which $(PROTOC))

# Run the setup script for the balance of the wdlc build.

$(BACKEND_TARGET): $(top_srcdir)/$(SCRIPTSDIR)/setup_compiler.sh | $(RESULTSDIR)
	$(NL_V_PROGRESS) "SETUP" "wdlc"
	$(NL_V_AT)$(<) \
	    --protoc "$(PROTOC)" \
	    --python "$(PYTHON)" \
	    --requirement "$(top_srcdir)/backend/pip-install-requirements.txt" \
	    --bindir "$(WDLC_BINDIR)" \
	    --datadir "$(WDLC_DATADIR)" \
	    --includedir "$(WDLC_INCLUDEDIR)" \
	    --libdir "$(WDLC_LIBDIR)" \
	    --srcdir "$(top_srcdir)" \
	    --output "$(RESULTSDIR)"

# A final step of the compiler set-up process is running the compiler
# backend schema validation. Running that validation requires the
# runtime Python "trampoline" script, setup.sh. Make sure that exists
# before running setup_compiler.sh.

$(top_srcdir)/$(SCRIPTSDIR)/setup_compiler.sh: $(RESULTSDIR)/$(WDLC_LIBDIR)/setup.sh

# Preprocess the compiler backend Python trampoline script,
# substituting specific directories.

$(RESULTSDIR)/$(WDLC_LIBDIR)/setup.sh: backend/setup.sh | $(RESULTSDIR)/$(WDLC_LIBDIR)
	$(NL_V_PROGRESS) "COPY" "$(@)"
	$(NL_V_AT)$(SED) \
            -e "s,@WDLC_DATADIR@,${WDLC_DATADIR},g" \
            -e "s,@WDLC_INCLUDEDIR@,${WDLC_INCLUDEDIR},g" \
	    < "$(<)" > "$(@)"
	$(NL_V_AT)chmod 664 "$(@)"

#
# Directory Creation
#

$(RESULTSDIR)/$(WDLC_BINDIR): | $(RESULTSDIR)

$(RESULTSDIR)/$(WDLC_DATADIR): | $(RESULTSDIR)

$(RESULTSDIR)/$(WDLC_LIBDIR): | $(RESULTSDIR)

$(RESULTSDIR)/$(WDLC_CODEGENDIR): | $(RESULTSDIR)

$(RESULTSDIR)/$(WDLC_BINDIR_COMPONENT): | $(RESULTSDIR)

$(RESULTSDIR) $(RESULTSDIR)/$(WDLC_BINDIR) $(RESULTSDIR)/$(WDLC_DATADIR) $(RESULTSDIR)/$(WDLC_LIBDIR) $(RESULTSDIR)/$(WDLC_CODEGENDIR) $(RESULTSDIR)/$(WDLC_BINDIR_COMPONENT): | announce-version
	$(call nl-create-dir,$(@))

$(DESTDIR) $(DESTDIR)${exec_prefix}/$(WDLC_BINDIR) $(DESTDIR)${prefix}/$(WDLC_DATADIR) $(DESTDIR)${prefix}/$(WDLC_INCLUDEDIR) $(DESTDIR)${exec_prefix}/$(WDLC_LIBDIR): | announce-version
	$(call nl-create-dir,$(@))

#
# check-reference <templates> <directory>
#
# This compares the generated code for <templates> in the specified
# <directory> against the reference for those templates.
#
define wdlc-check-reference
$(call nl-create-dir,$(2))
$(NL_V_PROGRESS) "WDLC" "$(1)"
$(NL_V_AT)$(WDLC_TARGET) -g "$(top_srcdir)/codegen/$(1)/templates" --add-test --gen-dependencies -o "$(2)" || $(RM) -r "$(2)"
$(NL_V_PROGRESS) "DIFF" "$(top_srcdir)/codegen/$(1)/reference $(2)"
$(NL_V_AT)$(DIFF) -q -aruN "$(top_srcdir)/codegen/$(1)/reference" "$(2)"
$(call nl-remove-dir,$(2))
endef # wdlc-check-reference

#
# update-reference <templates>
#
# This updates the reference generated code for a given set of templates.
#
define wdlc-update-reference
$(NL_V_PROGRESS) "RM" "codegen/$(1)/reference"
$(call nl-remove-dir,"codegen/$(1)/reference")
$(NL_V_PROGRESS) "MKDIR" "codegen/$(1)/reference"
$(call nl-create-dir,"codegen/$(1)/reference")
$(NL_V_AT)$(WDLC_TARGET) -g "$(top_srcdir)/codegen/$(1)/templates" --add-test --gen-dependencies -o "$(top_srcdir)/codegen/$(1)/reference"
endef # wdlc-update-reference

.PHONY: check
check: check-reference

.PHONY: check-reference
check-reference: check-reference-weave-device-cpp

.PHONY: update-reference-%
update-reference-%:
	$(call wdlc-update-reference,$(*))

check-reference-%: $(TARGETS) | $(top_srcdir)/codegen/%/reference $(top_srcdir)/codegen/%/templates
	$(call wdlc-check-reference,$(*),$(CHECK_TMPDIR))

# For installation, ensure that the wdlc and protoc binaries
# dependencies are satisfied: everything else falls out of those.
#
# In addition, conditionally create a symbolic link from the versioned
# wdlc binary directory to the configured binary directory if doing so
# would not overwrite anything.

.PHONY: install
install: $(TARGETS) | $(DESTDIR) $(DESTDIR)${exec_prefix}/$(WDLC_BINDIR) $(DESTDIR)${prefix}/$(WDLC_DATADIR) $(DESTDIR)${prefix}/$(WDLC_INCLUDEDIR) $(DESTDIR)${exec_prefix}/$(WDLC_LIBDIR)
	$(NL_V_PROGRESS) "INSTALL" "$(DESTDIR)"
	$(NL_V_AT)cp -Rf $(RESULTSDIR)/$(WDLC_BINDIR)/. $(DESTDIR)${exec_prefix}/$(WDLC_BINDIR)/.
	$(NL_V_AT)cp -Rf $(RESULTSDIR)/$(WDLC_DATADIR)/. $(DESTDIR)${prefix}/$(WDLC_DATADIR)/.
	$(NL_V_AT)cp -Rf $(RESULTSDIR)/$(WDLC_INCLUDEDIR)/. $(DESTDIR)${prefix}/$(WDLC_INCLUDEDIR)/.
	$(NL_V_AT)cp -Rf $(RESULTSDIR)/$(WDLC_LIBDIR)/. $(DESTDIR)${exec_prefix}/$(WDLC_LIBDIR)/.
	$(NL_V_AT)target="$(DESTDIR)${bindir}/wdlc"; \
	command="$(call WDLC_LINK_COMMAND,$${target})"; \
	if [ ! -e "$${target}" ] && [ ! -L "$${target}" ]; then \
	    $(_NL_PROGRESS) "LN" "$${target}"; \
	    $${command}; \
	else \
	    if [ -L "$${target}" ]; then \
		description="symbolic link"; \
		source=`readlink $${target}`; \
		newest=`printf "$${source}\n$(WDLC_LINK_SOURCE)\n" | $(SED) -e 's/^ *//' -e 's/\/.\+$$//' | $(SORT) -t '-' -k2V,2V | tail -n 1`; \
		if [ "$${newest}" = "$(WDLC_VERSIONDIR_COMPONENT)" ]; then \
		    what="an older or equivalent version of "; \
		else \
		    what="a newer version of "; \
		fi; \
	    else \
		description="file"; \
		what=""; \
	    fi; \
	    echo "--------------------------------------------------------------------------------"; \
	    echo "NOTE: There is an existing $${description} at '$${target}' for $${what}wdlc that will not be replaced.\n\nIf you would like to have a link to this installation of wdlc in '${exec_prefix}', please run:\n\n    $${command}\n"; \
	    echo "--------------------------------------------------------------------------------"; \
	fi

.PHONY: uninstall-local
uninstall-local:
	$(NL_V_PROGRESS) "UNINSTALL" "$(DESTDIR)"
	$(NL_V_AT)$(RM) -r $(DESTDIR)${exec_prefix}/$(WDLC_BINDIR)
	$(NL_V_AT)$(RM) -r $(DESTDIR)${prefix}/$(WDLC_DATADIR)
	$(NL_V_AT)$(RM) -r $(DESTDIR)${prefix}/$(WDLC_INCLUDEDIR)
	$(NL_V_AT)$(RM) -r $(DESTDIR)${exec_prefix}/$(WDLC_LIBDIR)

bindist-tgz: $(bindist_tgz_TARGETS)

bindist-xz: $(bindist_xz_TARGETS)

#
# Produce prebuilt binaries for the architecture of the current build
# machine and package them up for distribution.
#
$(PACKAGE)dist bindist: .local-version $(BINDIST_TARGETS) | announce-version
	$(call nl-remove-dir,$(distdir))

#
# Stage the binary distribution files to a distribution directory
#
# We want to create relocatable distributions, so elide exec_prefix
# and prefix.
#
bindist-stage:
	$(call nl-remove-dir,$(distdir))
	$(call nl-create-dir,$(distdir))
	$(NL_V_PROGRESS) "MAKE" "install"
	$(NL_V_AT)$(NL_V_MAKE_S) DESTDIR=$(distdir) exec_prefix="" prefix="" install

#
# Produce prebuilt wdlc architecture-dependent binaries for the
# architecture of the current build machine and package them up for
# distribution in tar-gzip format.
#
${top_builddir}/${PACKAGE}-${nl_filtered_host}-$(VERSION)$(TGZ_EXTENSION): bindist-stage
	$(NL_V_PROGRESS_TGZ)
	$(NL_V_AT)$(dist_tgz_ARCHIVE) $(distdir) | $(dist_tgz_COMPRESS) > "$(@)"

#
# Produce prebuilt wdlc architecture-dependent binaries for the
# architecture of the current build machine and package them up for
# distribution in tar-xz format.
#
${top_builddir}/${PACKAGE}-${nl_filtered_host}-$(VERSION)$(TXZ_EXTENSION): stage
	$(NL_V_PROGRESS_TXZ)
	$(NL_V_AT)$(dist_txz_ARCHIVE) $(distdir) | $(dist_txz_COMPRESS) > "$(@)"

.PHONY: clean
clean:
	$(NL_V_PROGRESS) "CLEAN" "$(RESULTSDIR)"
	-$(NL_V_AT)$(RM) -r $(RESULTSDIR)

.PHONY: distclean-local
distclean-local:
	$(NL_V_PROGRESS) "CLEAN" "$(RESULTSDIR)"
	-$(NL_V_AT)$(RM) -r $(RESULTSDIR)

define PrintPackageHelp
$(NL_V_AT)echo "  all"
$(NL_V_AT)echo "  $(PACKAGE)"
$(NL_V_AT)echo "    Generate all configured build artifacts for this package."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  check"
$(NL_V_AT)echo "    Generate all configured build artifacts and run all unit "
$(NL_V_AT)echo "    and functional tests for this package."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  clean"
$(NL_V_AT)echo "    Remove all configured build artifacts."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  bindist"
$(NL_V_AT)echo "  $(PACKAGE)dist"
$(NL_V_AT)echo "    Generate a host-architecture-specific, versioned binary archive"
$(NL_V_AT)echo "    distributions of this package. The number and format of the"
$(NL_V_AT)echo "    created distributions is controlled by BINDIST_TARGETS (default:"
$(NL_V_AT)echo "    $(BINDIST_TARGETS))."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  dist"
$(NL_V_AT)echo "  srcdist"
$(NL_V_AT)echo "    Generate a versioned source archive distributions of this package."
$(NL_V_AT)echo "    The number and format of the created distributions is controlled by"
$(NL_V_AT)echo "    DIST_TARGETS (default: $(DIST_TARGETS))."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  distcheck"
$(NL_V_AT)echo "    Generate a versioned source archive distribution of this package and"
$(NL_V_AT)echo "    sanity check the resulting distribution by running 'make check' on it for"
$(NL_V_AT)echo "    this package."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  distclean"
$(NL_V_AT)echo "    Remove all configured build artifacts and build configuration."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  install"
$(NL_V_AT)echo "    Generate all configured build artifacts for this package and install them"
$(NL_V_AT)echo "    on the build host system."
$(NL_V_AT)echo ""
$(NL_V_AT)echo "  uninstall"
$(NL_V_AT)echo "    Remove all configured build artifacts for this package from the build host"
$(NL_V_AT)echo "    system."
$(NL_V_AT)echo ""
endef # PrintPackageHelp

help-hook:
	$(call PrintPackageHelp)

include $(abs_top_nlbuild_autotools_dir)/automake/post.am
