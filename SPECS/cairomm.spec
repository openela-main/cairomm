%global so_version 1
%global apiver 1.0

# “Let mm-common-get copy some files to untracked/”, i.e., replace scripts from
# the tarball with those from mm-common. This is (potentially) required if
# building an autotools-generated tarball with meson, or vice versa.
%bcond_without maintainer_mode

Name:           cairomm
Summary:        C++ API for the cairo graphics library
Version:        1.14.2
Release:        10%{?dist}

URL:            https://www.cairographics.org
License:        LGPLv2+

%global src_base https://www.cairographics.org/releases
Source0:        %{src_base}/%{name}-%{version}.tar.xz
# No keyring with authorized GPG signing keys is published
# (https://gitlab.freedesktop.org/freedesktop/freedesktop/-/issues/331), but we
# are able to verify the signature using the key for Kjell Ahlstedt from
# https://gitlab.freedesktop.org/freedesktop/freedesktop/-/issues/290.
Source1:        %{src_base}/cairomm-%{version}.tar.xz.asc
Source2:        https://gitlab.freedesktop.org/freedesktop/freedesktop/uploads/0ac64e9582659f70a719d59fb02cd037/gpg_key.pub

BuildRequires:  gnupg2

BuildRequires:  gcc-c++
BuildRequires:  meson

BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(sigc++-2.0)
BuildRequires:  pkgconfig(fontconfig)

# Everything mentioned in data/cairomm*.pc.in, except the Quartz and Win32
# libraries that do not apply to this platform:
BuildRequires:  pkgconfig(cairo-ft)
BuildRequires:  pkgconfig(cairo-pdf)
BuildRequires:  pkgconfig(cairo-png)
BuildRequires:  pkgconfig(cairo-ps)
BuildRequires:  pkgconfig(cairo-svg)
BuildRequires:  pkgconfig(cairo-xlib)
BuildRequires:  pkgconfig(cairo-xlib-xrender)

%if %{with maintainer_mode}
# mm-common-get
BuildRequires:  mm-common
%endif

BuildRequires:  perl-interpreter
BuildRequires:  perl(Getopt::Long)
BuildRequires:  doxygen
# dot
BuildRequires:  graphviz
# xsltproc
BuildRequires:  libxslt
BuildRequires:  pkgconfig(mm-common-libstdc++)

# For tests:
BuildRequires:  boost-devel

# Based on discussion in
# https://src.fedoraproject.org/rpms/pangomm/pull-request/2, cairomm will
# continue to provide API/ABI version 1.0 indefinitely, with the cairomm1.16
# package providing the new 1.16 API/ABI series. This virtual Provides is
# therefore no longer required, as dependent packages requiring the 1.0 API/ABI
# may safely require cairomm and its subpackages.
Provides:       %{name}%{apiver}%{?_isa} = %{version}-%{release}

%description
This library provides a C++ interface to cairo.

The API/ABI version series is %{apiver}.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

Provides:       %{name}%{apiver}-devel%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for developing
applications that use %{name}.

The API/ABI version series is %{apiver}.


%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch
Requires:       libstdc++-docs
Requires:       libsigc++20-doc

Provides:       %{name}%{apiver}-doc = %{version}-%{release}

%description    doc
Documentation for %{name} can be viewed either through the devhelp
documentation browser or through a web browser at
%{_datadir}/doc/%{name}-%{apiver}/.

The API/ABI version series is %{apiver}.


%prep
# Import developer’s public GPG key to a keyring that we can use for signature
# verification.
workdir="$(mktemp --directory)"
gpg2 --homedir="${workdir}" --yes --import '%{SOURCE2}'
gpg2 --homedir="${workdir}" --export --export-options export-minimal \
    > %{name}.gpg
rm -rf "${workdir}"

%{gpgverify} \
    --keyring='%{name}.gpg' --signature='%{SOURCE1}' --data='%{SOURCE0}'

%autosetup
# We must remove the jQuery/jQueryUI bundle with precompiled/minified/bundled
# JavaScript that is in untracked/docs/reference/html/jquery.js, since such
# sources are banned in Fedora. (Note also that the bundled JavaScript had a
# different license.) We also remove the tag file, which triggers a rebuild of
# the documentation. While we are at it, we might as well rebuild the devhelp
# XML too.
rm -rf untracked/docs/reference/html
rm untracked/docs/reference/%{name}-%{apiver}.tag \
   untracked/docs/reference/%{name}-%{apiver}.devhelp2


%build
%meson \
  -Dmaintainer-mode=%{?with_maintainer_mode:true}%{?!with_maintainer_mode:false} \
  -Dbuild-documentation=true \
  -Dbuild-examples=false \
  -Dbuild-tests=true \
  -Dboost-shared=true \
  -Dwarnings=max
%meson_build


%install
%meson_install
find %{buildroot} -type f -name '*.la' -print -delete

install -t %{buildroot}%{_datadir}/doc/%{name}-%{apiver} -m 0644 -p \
    AUTHORS ChangeLog MAINTAINERS NEWS README
cp -rp examples %{buildroot}%{_datadir}/doc/%{name}-%{apiver}/


%check
%meson_test


%files
%license COPYING
%{_libdir}/lib%{name}-%{apiver}.so.%{so_version}
%{_libdir}/lib%{name}-%{apiver}.so.%{so_version}.*


%files devel
%{_includedir}/%{name}-%{apiver}
%{_libdir}/lib%{name}-%{apiver}.so
%{_libdir}/pkgconfig/%{name}-%{apiver}.pc
%{_libdir}/pkgconfig/%{name}-*-%{apiver}.pc
%{_libdir}/%{name}-%{apiver}


%files doc
%license COPYING
%doc %{_datadir}/doc/%{name}-%{apiver}/
%doc %{_datadir}/devhelp/


%changelog
* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.14.2-10
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 1.14.2-9
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Sat Feb 20 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-8
- Verify source with new strong signatures from upstream

* Thu Feb 18 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-7
- Working (but weak, dependent on SHA1) source signature verification
- Added API/ABI version to descriptions

* Wed Feb 17 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-6
- Fix typo %%{_?isa} for %%{?_isa} in virtual Provides
- Tidy up BR’s, including dropping make

* Mon Feb 15 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-5
- Update comments based on the new plan for the version 1.16 API/ABI

* Thu Feb 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-4
- Prepare for future upgrade to API/ABI version 1.16 by introducing virtual
  Provides for a name for API/ABI version 1.0: cairomm1.0. This will be the name
  of a future package that continues to provide API/ABI version 1.0 after the
  upgrade.

* Thu Feb 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-3
- Switch from autotools to meson; enable the tests, since the meson build system
  permits us to use a shared boost library
- Install examples in the -doc subpackage

* Thu Feb 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-2
- Restore removal of pre-built documentation with its minified JS bundle

* Thu Feb 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.2-1
- Update to 1.14.2; this adds new APIs, but is ABI-backwards-compatible

* Thu Feb 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.12.2-1
- Update to 1.12.2

* Thu Feb 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.12.0-16
- Switch URLs from HTTP to HTTPS
- Rough out code to verify source tarball signatures, and document why we
  cannot yet do so

* Thu Feb 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.12.0-15
- Spec file style tweaks
- Macro-ize documentation path in description
- Simplified summaries and descriptions
- Use make macros (https://src.fedoraproject.org/rpms/cairomm/pull-request/1)
- Drop obsolete %%ldconfig_scriptlets macro
- Much stricter file globs, including so-version
- Stop requiring the base package from the -doc package
- Migrate top-level text file documentation to the -doc subpackage
- BR mm-common; at minimum, this lets us find tags for libstdc++ documentation;
  require libstdc++-docs from the -doc subpackage, since we are now able to
  find the tag file in configure
- Remove bundled jQuery/jQueryUI from prebuilt documentation, and rebuild the
  documentation ourselves
- Add a note explaining why we cannot run the tests
- Drop explicit/manual lib Requires on cairo/libsigc++20
- Drop version requirements in BRs
- Rebuild autotools-generated files

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Feb 04 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.12.0-7
- Switch to %%ldconfig_scriptlets

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Sep 22 2015 Kalev Lember <klember@redhat.com> - 1.12.0-1
- Update to 1.12.0
- Drop manual requires that are automatically handled by pkgconfig dep gen
- Use license macro for COPYING
- Tighten -devel subpackage deps with the _isa macro
- Use make_install macro

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.10.0-11
- Rebuilt for GCC 5 C++11 ABI change

* Sat Mar 07 2015 Kalev Lember <kalevlember@gmail.com> - 1.10.0-10
- Rebuilt for gcc5 ABI change

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-4
- Rebuilt for c++ ABI breakage

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 06 2011 Adam Jackson <ajax@redhat.com> - 1.10.0-2
- Rebuild for new libpng

* Fri Jul 29 2011 Kalev Lember <kalevlember@gmail.com> - 1.10.0-1
- Update to 1.10.0
- Have the -doc subpackage depend on the base package
- Modernize the spec file
- Really own /usr/share/devhelp directory

* Mon Feb 21 2011 Haïkel Guémar <hguemar@fedoraproject.org> - 1.9.8-2
- fix documentation location
- co-own /usr/share/devhelp

* Mon Feb 14 2011 Haïkel Guémar <hguemar@fedoraproject.org> - 1.9.8-1
- upstream 1.9.8
- fix issues with f15/rawhide (RHBZ #676878)
- drop gtk-doc dependency (RHBZ #604169)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jul 14 2010 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.9.1-1
- New upstream release
- Removed html docs from -devel package
- Seperated requires into one per line
- Fixed devhelp docs

* Tue Nov 17 2009 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.8.4-1
- New upstream release
- Added cairommconfig.h file
- Added doc subpackage

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.8.0-1
- Update to 1.8.0
- Added libsigc++20-devel dependency

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Aug 29 2008 Denis Leroy <denis@poolshark.org> - 1.6.2-1
- Update to upstream 1.6.2
- atsui patch upstreamed

* Sun Mar 23 2008 Denis Leroy <denis@poolshark.org> - 1.5.0-1
- Update to 1.5.0
- Added patch from Mamoru Tasaka to fix font type enum (#438600)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.4.4-2
- Autorebuild for GCC 4.3

* Fri Aug 17 2007 Denis Leroy <denis@poolshark.org> - 1.4.4-1
- Update to upstream version 1.4.4
- Fixed License tag

* Fri Jul 20 2007 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.4.2-1
- New upstream release
- Changed install to preserve timestamps
- Removed mv of docs/reference and include files directly

* Wed Jan 17 2007 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.2.4-1
- New release

* Sat Oct 14 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.2.2-1
- New upstream release

* Sun Aug 27 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.2.0-4
- Bumped release for make tag

* Sun Aug 27 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.2.0-3
- Bumped release for mass rebuild

* Sun Aug 20 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.2.0-2
- Bumped release for make tag

* Sun Aug 20 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.2.0-1
- New upstream release
- Updated summary and description

* Thu Aug  3 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 1.1.10-1
- First release for cairo 1.2
- Adjusted cairo dependencies for new version
- Docs were in html, moved to reference/html

* Sun Apr  9 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.6.0-1
- New upstream version should fix the upstream issues like AUTHORS and README
- Added pkgconfig to cairomm BuildRequires and cairomm-devel Requires
- Replaced makeinstall
- Fixed devel package description
- Modified includedir syntax
- docs included via the mv in install and in the devel files as html dir

* Sun Mar  5 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-10
- Removed duplicate Group tag in devel
- Disabled docs till they're fixed upstream

* Sun Mar  5 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-9
- Removed requires since BuildRequires is present
- Cleaned up Source tag

* Fri Feb 24 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-7
- Fixed URL and SOURCE tags
- Fixed header include directory

* Fri Feb 24 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-6
- Fixed URL tag

* Wed Feb 22 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-5
- Remove epoch 'leftovers'

* Wed Feb 22 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-4
- Cleanup for FE

* Wed Feb 22 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-3
- Added pre-release alphatag

* Wed Feb 22 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-2
- Updated to current cairomm CVS
- Added documentation to devel package

* Fri Feb 03 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.5.0-1
- Updated to current cairomm CVS

* Fri Jan 27 2006 Rick L Vinyard Jr <rvinyard@cs.nmsu.edu> - 0.4.0-1
- Initial creation from papyrus.spec.in

