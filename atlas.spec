%define enable_native_atlas 0

Name:           atlas
Version:        3.8.3
Release:        8%{?dist}
Summary:        Automatically Tuned Linear Algebra Software

Group:          System Environment/Libraries
License:        BSD
URL:            http://math-atlas.sourceforge.net/
Source0:        http://downloads.sourceforge.net/math-atlas/%{name}%{version}.tar.bz2
Source1:        PPRO32.tgz
Source2:        K7323DNow.tgz
Source3:        README.Fedora
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
Obsoletes:	%name-header = %version-%release

%description devel
This package contains the static libraries and headers for development
with ATLAS (Automatically Tuned Linear Algebra Software).

%define types base

%if "%{?enable_native_atlas}" == "0"
############## Subpackages for architecture extensions #################
#
%ifarch %{ix86}
%define types base 3dnow sse sse2 sse3

%package 3dnow
Summary:        ATLAS libraries for 3DNow extensions
Group:          System Environment/Libraries

%description 3dnow
This package contains the ATLAS (Automatically Tuned Linear Algebra
Software) libraries compiled with optimizations for the 3DNow extension
to the ix86 architecture. Fedora also produces ATLAS build with SSE, SSE2
and SSE3 extensions.

%package 3dnow-devel
Summary:        Development libraries for ATLAS with 3DNow extensions
Group:          Development/Libraries
Requires:       %{name}-3dnow = %{version}-%{release}
Obsoletes:	%name-header = %version-%release

%description 3dnow-devel
This package contains headers and shared and static versions of the ATLAS
(Automatically Tuned Linear Algebra Software) libraries compiled with
optimizations for the 3DNow extensions to the ix86 architecture.

%package sse
Summary:        ATLAS libraries for SSE extensions
Group:          System Environment/Libraries

%description sse
This package contains the ATLAS (Automatically Tuned Linear Algebra
Software) libraries compiled with optimizations for the SSE(1) extensions
to the ix86 architecture. Fedora also produces ATLAS build with SSE2 and SSE3
extensions.

%package sse-devel
Summary:        Development libraries for ATLAS with SSE extensions
Group:          Development/Libraries
Requires:       %{name}-sse = %{version}-%{release}
Obsoletes:	%name-header = %version-%release

%description sse-devel
This package contains headers and shared and static versions of the ATLAS
(Automatically Tuned Linear Algebra Software) libraries compiled with
optimizations for the SSE(1) extensions to the ix86 architecture.

%package sse2
Summary:        ATLAS libraries for SSE2 extensions
Group:          System Environment/Libraries

%description sse2
This package contains the ATLAS (Automatically Tuned Linear Algebra
Software) libraries compiled with optimizations for the SSE2
extensions to the ix86 architecture. Fedora also produces ATLAS build with
SSE(1) and SSE3 extensions.

%package sse2-devel
Summary:        Development libraries for ATLAS with SSE2 extensions
Group:          Development/Libraries
Requires:       %{name}-sse2 = %{version}-%{release}
Obsoletes:	%name-header = %version-%release

%description sse2-devel
This package contains shared and static versions of the ATLAS
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
Obsoletes:	%name-header = %version-%release

%description sse3-devel
This package contains shared and static versions of the ATLAS
(Automatically Tuned Linear Algebra Software) libraries compiled with
optimizations for the sse3 extensions to the ix86 architecture.

%endif
%endif

%ifarch x86_64 ppc64 s390x
%define mode 64
%else
%define mode 32
%endif

%prep
%setup -q -n ATLAS
%patch0 -p0 -b .shared
cp %{SOURCE1} CONFIG/ARCHS/
cp %{SOURCE2} CONFIG/ARCHS/
cp %{SOURCE3} doc

%build
for type in %{types}; do
	if [ "$type" = "base" ]; then
		libname=atlas
	else
		libname=atlas-${type}
	fi
	mkdir -p %{_arch}_${type}
	pushd %{_arch}_${type}
	../configure -b %{mode} -D c -DWALL -Fa alg '-g -Wa,--noexecstack -fPIC'\
	--prefix=%{buildroot}%{_prefix}			\
	--incdir=%{buildroot}%{_includedir}		\
	--libdir=%{buildroot}%{_libdir}/${libname}	\
	--with-netlib-lapack=%{_libdir}/liblapack_pic.a

%ifarch %{ix86}
	if [ "$type" = "base" ]; then
		sed -i 's#ARCH =.*#ARCH = PPRO32#' Make.inc
		sed -i 's#-DATL_SSE3 -DATL_SSE2 -DATL_SSE1##' Make.inc 
		sed -i 's#-mfpmath=sse -msse3#-mfpmath=387#' Make.inc 
	elif [ "$type" = "3dnow" ]; then
		sed -i 's#ARCH =.*#ARCH = K7323DNow#' Make.inc
		sed -i 's#-DATL_SSE3 -DATL_SSE2 -DATL_SSE1##' Make.inc 
		sed -i 's#-mfpmath=sse -msse3#-mfpmath=387#' Make.inc 
	elif [ "$type" = "sse" ]; then
		sed -i 's#ARCH =.*#ARCH = PIII32SSE1#' Make.inc
		sed -i 's#-DATL_SSE3 -DATL_SSE2##' Make.inc 
		sed -i 's#-msse3#-msse#' Make.inc 
	elif [ "$type" = "sse2" ]; then
		sed -i 's#ARCH =.*#ARCH = P432SSE2#' Make.inc
		sed -i 's#-DATL_SSE3##' Make.inc 
		sed -i 's#-msse3#-msse2#' Make.inc 
	elif [ "$type" = "sse3" ]; then
		sed -i 's#ARCH =.*#ARCH = P4E32SSE3#' Make.inc
	fi
%endif
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

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%ifarch %{ix86} && %if "%{?enable_native_atlas}" == "0"

%post -n atlas-3dnow -p /sbin/ldconfig

%postun -n atlas-3dnow -p /sbin/ldconfig

%post -n atlas-sse -p /sbin/ldconfig

%postun -n atlas-sse -p /sbin/ldconfig

%post -n atlas-sse2 -p /sbin/ldconfig

%postun -n atlas-sse2 -p /sbin/ldconfig

%post -n atlas-sse3 -p /sbin/ldconfig

%postun -n atlas-sse3 -p /sbin/ldconfig

%endif

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

%ifarch %{ix86} && %if "%{?enable_native_atlas}" == "0"

%files 3dnow
%defattr(-,root,root,-)
%doc doc/README.Fedora
%dir %{_libdir}/atlas-3dnow
%{_libdir}/atlas-3dnow/*.so.*
%config(noreplace) /etc/ld.so.conf.d/atlas-3dnow.conf

%files 3dnow-devel
%defattr(-,root,root,-)
%doc doc
%{_libdir}/atlas-3dnow/*.so
%{_libdir}/atlas-3dnow/*.a
%{_includedir}/atlas
%{_includedir}/*.h

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
%{_libdir}/atlas-sse2/*.so.*
%config(noreplace) /etc/ld.so.conf.d/atlas-sse2.conf

%files sse2-devel
%defattr(-,root,root,-)
%doc doc
%{_libdir}/atlas-sse2/*.so
%{_libdir}/atlas-sse2/*.a
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
* Sat Sep 26 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-8
- Use the new arch. default for Pentium PRO (Fedora bug #510498)
- (Re-)Introduce 3dNow subpackage
- Revert the last change, it doesn't solve the problem. 

* Tue Aug 04 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-7
- Create a -header subpackage to avoid multilib conflicts (BZ#508565). 

* Tue Aug 04 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-6
- Add '-g' to build flag to allow proper genration of debuginfo subpackages (Fedora bug #509813)
- Build for F12

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 02 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-4
- Use the right -msse* option for the -sse* subpackages (Fedora bug #498715)

* Tue Apr 21 2009 Karsten Hopp <karsten@redhat.com> 3.8.3-3.1
- add s390x to 64 bit archs

* Fri Feb 27 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-3
- Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Feb 22 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-1
- Update to version 3.8.3

* Sun Dec 21 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-5
- Link in appropriate libs when creating shared libs, reported by Orcan 'oget' Ogetbil (BZ#475411)

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
