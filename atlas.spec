%define enable_native_atlas 0

Name:           atlas
Version:        3.8.2
Release:        4%{?dist}
Summary:        Automatically Tuned Linear Algebra Software

Group:          System Environment/Libraries
License:        BSD
URL:            http://math-atlas.sourceforge.net/
Source0:        http://prdownloads.sourceforge.net/math-atlas/%{name}%{version}.tar.bz2
Source1:        README.Fedora
Patch0:		atlas-fedora_shared.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  gcc-gfortran lapack-devel

%description
The ATLAS (Automatically Tuned Linear Algebra Software) project is an
ongoing research effort focusing on applying empirical techniques in
order to provide portable performance. At present, it provides C and
Fortran77 interfaces to a portably efficient BLAS implementation, as
well as a few routines from LAPACK.

The performance improvements in ATLAS are obtained largely via
compile-time optimizations and tend to be specific to a given hardware
configuration. In order to package ATLAS for Fedora some compromises
are necessary so that good performance can be obtained on a variety
of hardware. This set of ATLAS binary packages is therefore not
necessarily optimal for any specific hardware configuration.  However,
the source package can be used to compile customized ATLAS packages;
see the documentation for information.

%package devel
Summary:        Development libraries for ATLAS
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description devel
This package contains the static libraries and headers for development
with ATLAS (Automatically Tuned Linear Algebra Software).

%define types base

%if "%{?enable_native_atlas}" == "0"
############## Subpackages for architecture extensions #################
#
# Because a set of ATLAS libraries is a ~5 MB package, separate packages
# are created for SSE, SSE2, and SSE3 extensions to ix86.

%ifarch i386
%define types sse sse2 sse3

%package sse
Summary:        ATLAS libraries for SSE extensions
Group:          System Environment/Libraries
Obsoletes:	%{name}-3dnow < 3.7
Provides:	%{name}-3dnow = %{version}-%{release}

%description sse
This package contains the ATLAS (Automatically Tuned Linear Algebra
Software) libraries compiled with optimizations for the SSE(1) extensions
to the ix86 architecture. Fedora also produces ATLAS build with SSE2 and SSE3
extensions.

%package sse-devel
Summary:        Development libraries for ATLAS with SSE extensions
Group:          Development/Libraries
Requires:       %{name}-sse = %{version}-%{release}
Obsoletes:	%{name}-3dnow-devel < 3.7
Provides:	%{name}-3dnow-devel = %{version}-%{release}

%description sse-devel
This package contains headers and static versions of the ATLAS
(Automatically Tuned Linear Algebra Software) libraries compiled with
optimizations for the SSE(1) extensions to the ix86 architecture.

%package sse2
Summary:        ATLAS libraries for SSE2 extensions
Group:          System Environment/Libraries
Obsoletes:	%{name} < 3.7
Provides:	%{name} = %{version}-%{release}

%description sse2
This package contains the ATLAS (Automatically Tuned Linear Algebra
Software) libraries compiled with optimizations for the SSE2
extensions to the ix86 architecture. Fedora also produces ATLAS build with
SSE(1) and SSE3 extensions.

%package sse2-devel
Summary:        Development libraries for ATLAS with SSE2 extensions
Group:          Development/Libraries
Requires:       %{name}-sse2 = %{version}-%{release}
Obsoletes:	%{name}-devel < 3.7
Provides:	%{name}-devel = %{version}-%{release}

%description sse2-devel
This package contains headers and static versions of the ATLAS
(Automatically Tuned Linear Algebra Software) libraries compiled with
optimizations for the SSE2 extensions to the ix86 architecture.

%package sse3
Summary:        ATLAS libraries for 3DNow extensions
Group:          System Environment/Libraries

%description sse3
This package contains the ATLAS (Automatically Tuned Linear Algebra
Software) libraries compiled with optimizations for the SSE3.
Fedora also produces ATLAS build with SSE(1) and SSE2 extensions.

%package sse3-devel
Summary:        Development libraries for ATLAS with 3DNow extensions
Group:          Development/Libraries
Requires:       %{name}-sse3 = %{version}-%{release}

%description sse3-devel
This package contains headers and static versions of the ATLAS
(Automatically Tuned Linear Algebra Software) libraries compiled with
optimizations for the sse3 extensions to the ix86 architecture.

%endif
%endif

%ifarch x86_64 ppc64
%define mode 64
%else
%define mode 32
%endif

%prep
%setup -q -n ATLAS
%patch0 -p0 -b .shared
cp %{SOURCE1} doc

%build
for type in %{types}; do
	if [ "$type" = "base" ]; then
		libname=atlas
	else
		libname=atlas-${type}
	fi
	mkdir -p %{_arch}_${type}
	pushd %{_arch}_${type}
	../configure -b %{mode} -D c -DWALL -Fa alg '-Wa,--noexecstack -fPIC'\
	--prefix=%{buildroot}%{_prefix}			\
	--incdir=%{buildroot}%{_includedir}		\
	--libdir=%{buildroot}%{_libdir}/${libname}	\
	--with-netlib-lapack=%{_libdir}/liblapack_pic.a

	if [ "$type" = "sse" ]; then
		sed -i 's#ARCH =.*#ARCH = PIII32SSE1#' Make.inc
		sed -i 's#-DATL_SSE3 -DATL_SSE2##' Make.inc 
	elif [ "$type" = "sse2" ]; then
		sed -i 's#ARCH =.*#ARCH = P432SSE2#' Make.inc
		sed -i 's#-DATL_SSE3##' Make.inc 
	elif [ "$type" = "sse3" ]; then
		sed -i 's#ARCH =.*#ARCH = P4E32SSE3#' Make.inc
	fi
	make build
	cd lib
	make shared
	make ptshared
	popd
done

%install
rm -rf %{buildroot}
for type in %{types}; do
	pushd %{_arch}_${type}
	make DESTDIR=%{buildroot} install
	if [ "$type" = "base" ]; then
		cp -pr lib/*.so* %{buildroot}%{_libdir}/atlas/
	else
		cp -pr lib/*.so* %{buildroot}%{_libdir}/atlas-${type}/
	fi
	popd

	mkdir -p %{buildroot}/etc/ld.so.conf.d
	if [ "$type" = "base" ]; then
		echo "%{_libdir}/atlas"		\
		> %{buildroot}/etc/ld.so.conf.d/atlas-%{_arch}.conf
	else
		echo "%{_libdir}/atlas-${type}"	\
		> %{buildroot}/etc/ld.so.conf.d/atlas-${type}.conf
	fi
done
%ifarch i386 && %if "%{?enable_native_atlas}" == "0"
cp -pr %{buildroot}%{_libdir}/atlas-sse2 %{buildroot}%{_libdir}/atlas
echo "%{_libdir}/atlas"	>> %{buildroot}/etc/ld.so.conf.d/atlas-sse2.conf
%endif

%clean
rm -rf %{buildroot}

%ifnarch i386 || %if "%{?enable_native_atlas}" == "1"

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc doc/README.Fedora
%dir %{_libdir}/atlas
%{_libdir}/atlas/*.so.*
%config(noreplace) /etc/ld.so.conf.d/atlas-%{_arch}.conf

%files devel
%defattr(-,root,root,-)
%doc doc
%{_libdir}/atlas/*.so
%{_libdir}/atlas/*.a
%{_includedir}/atlas
%{_includedir}/*.h

%else

%post -n atlas-sse -p /sbin/ldconfig

%postun -n atlas-sse -p /sbin/ldconfig

%post -n atlas-sse2 -p /sbin/ldconfig

%postun -n atlas-sse2 -p /sbin/ldconfig

%post -n atlas-sse3 -p /sbin/ldconfig

%postun -n atlas-sse3 -p /sbin/ldconfig

%files sse
%defattr(-,root,root,-)
%doc doc/README.Fedora
%dir %{_libdir}/atlas-sse
%{_libdir}/atlas-sse/*.so.*
%config(noreplace) /etc/ld.so.conf.d/atlas-sse.conf

%files sse-devel
%defattr(-,root,root,-)
%doc doc
%{_libdir}/atlas-sse/*.so
%{_libdir}/atlas-sse/*.a
%{_includedir}/atlas
%{_includedir}/*.h

%files sse2
%defattr(-,root,root,-)
%doc doc/README.Fedora
%dir %{_libdir}/atlas-sse2
%dir %{_libdir}/atlas
%{_libdir}/atlas-sse2/*.so.*
%{_libdir}/atlas/*.so.*
%config(noreplace) /etc/ld.so.conf.d/atlas-sse2.conf
%config(noreplace) /etc/ld.so.conf.d/atlas.conf

%files sse2-devel
%defattr(-,root,root,-)
%doc doc
%{_libdir}/atlas-sse2/*.so
%{_libdir}/atlas-sse2/*.a
%{_libdir}/atlas/*.so
%{_libdir}/atlas/*.a
%{_includedir}/atlas
%{_includedir}/*.h

%files sse3
%defattr(-,root,root,-)
%doc doc/README.Fedora
%dir %{_libdir}/atlas-sse3
%{_libdir}/atlas-sse3/*.so.*
%config(noreplace) /etc/ld.so.conf.d/atlas-sse3.conf

%files sse3-devel
%defattr(-,root,root,-)
%doc doc
%{_libdir}/atlas-sse3/*.so
%{_libdir}/atlas-sse3/*.a
%{_includedir}/atlas
%{_includedir}/*.h

%endif

%changelog
* Tue Dec 16 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-4
- Don't symlink the atlas libdir on i386, cause upgrade issue (BZ#476787)
- Fix options passed to gcc when making shared libs

* Tue Dec 16 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-3
- Use 'gcc -shared' to build shared libs instead of stock 'ld'

* Sat Dec 13 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-2
- Properly obsolete/provide older subpackages that are no longer packaged.

* Mon Sep 01 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-1
- Upgrade to ver 3.8.2 with refined build procedures.

* Thu Feb 28 2008 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-15
- Disable altivec package--it is causing illegal instructions during build.

* Thu Feb 28 2008 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-14
- Enable compilation on alpha (bug 426086).
- Patch for compilation on ia64 (bug 432744).

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.6.0-13
- Autorebuild for GCC 4.3

* Mon Jun  4 2007 Orion Poplawski <orion@cora.nwra.com> 3.6.0-12
- Rebuild for ppc64

* Fri Sep  8 2006 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-11
- Rebuild for FC6.
- Remove outdated comments from spec file.

* Mon Feb 13 2006 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-10
- Rebuild for Fedora Extras 5.
- Add --noexecstack to compilation of assembly kernels. These were
  previously marked executable, which caused problems with selinux.

* Mon Dec 19 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-9
- Rebuild for gcc 4.1.

* Mon Oct 10 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-8
- Make all devel subpackages depend on their non-devel counterparts.
- Add /etc/ld.so.conf.d files for -sse and -3dnow, because they don't
  seem to get picked up automatically.

* Wed Oct 05 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-7
- Forgot to add the new patch to sources.

* Tue Oct 04 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-6
- Use new Debian patch, and enable shared libs (they previously failed
  to build on gcc 4).
- Minor updates to description and README.Fedora file.
- Fix buildroot name to match FE preferred form.
- Fixes for custom optimized builds.
- Add dist tag.

* Wed Sep 28 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-5
- fix files lists.

* Mon Sep 26 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-4
- generate library symlinks earlier for the benefit of later linking steps.

* Wed Sep 14 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-3
- Change lapack dependency to lapack-devel, and use lapack_pic.a for
  building liblapack.so.

* Wed Sep 14 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-2
- Add "bit" macro to correctly build on x86_64.

* Tue Aug 16 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-1
- Initial version.
