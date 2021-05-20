%global __python %{__python3}
%global vd_rc %{?v_rc:0.%{?v_rc}.}
%global debug_package %{nil}
%global _use_internal_dependency_generator 0
%global __find_provides %{_sourcedir}/find-provides %__find_provides


Summary: High-performance HTTP accelerator
Name:    varnish-maxwait
Version: %{versiontag}
Release: %{?vd_rc}%{releasetag}%{?dist}
License: BSD
Group:   System Environment/Daemons
URL:     https://www.varnish-cache.org/
Source:  %{srcname}.tgz

BuildRequires: diffutils
BuildRequires: gcc
BuildRequires: jemalloc-devel
BuildRequires: libedit-devel
BuildRequires: make
BuildRequires: ncurses-devel
BuildRequires: pcre-devel
BuildRequires: pcre2-devel
BuildRequires: pkgconfig
BuildRequires: python3
BuildRequires: python3-sphinx

Requires: gcc
Requires: logrotate
%systemd_requires
%if 0%{?rhel} >= 8
Requires: redhat-rpm-config
%endif

Provides:  varnish-maxwait-libs%{?_isa} = %{version}-%{release}
Provides:  varnish-maxwait-libs = %{version}-%{release}
Obsoletes: varnish-maxwait-libs
Obsoletes: varnish-libs

Provides:  varnish-maxwait-docs = %{version}-%{release}
Obsoletes: varnish-maxwait-docs
Obsoletes: varnish-docs

Provides:  varnish-maxwait-debuginfo%{?_isa} = %{version}-%{release}
Provides:  varnish-maxwait-debuginfo = %{version}-%{release}
Obsoletes: varnish-maxwait-debuginfo
Obsoletes: varnish-debuginfo


%description
This is Varnish Cache, a high-performance HTTP accelerator.

Varnish Cache stores web pages in memory so web servers don't have to
create the same web page over and over again. Varnish Cache serves
pages much faster than any application server; giving the website a
significant speed up.

Documentation wiki and additional information about Varnish Cache is
available on: https://www.varnish-cache.org/


%package devel
Summary:   Development files for %{name}
Group:     System Environment/Libraries
Requires:  %{name}%{?_isa} = %{version}-%{release}
Requires:  pkgconfig
Requires:  python(abi) >= 3.4
Provides:  varnish-maxwait-libs-devel%{?_isa} = %{version}-%{release}
Provides:  varnish-maxwait-libs-devel = %{version}-%{release}
Obsoletes: varnish-maxwait-libs-devel
Obsoletes: varnish-libs-devel


%description devel
Development files for %{name}
Varnish Cache is a high-performance HTTP accelerator


%prep
%setup -q -n %{srcname}


%build
%configure --localstatedir=/var/lib
%make_build V=1


%check
%if 0%{?nocheck} == 0
%make_build check VERBOSE=1
%endif


%install
export DONT_STRIP=1
%make_install

find %{buildroot}/%{_libdir}/ -name '*.la' -exec rm -f {} ';'

mkdir -p %{buildroot}/var/lib/varnish
mkdir -p %{buildroot}/var/log/varnish
mkdir -p %{buildroot}/var/run/varnish
mkdir -p %{buildroot}%{_datadir}/varnish
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/
install -D -m 0644 etc/example.vcl %{buildroot}%{_sysconfdir}/varnish/default.vcl
install -D -m 0644 %{_sourcedir}/varnish.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/varnish

mkdir -p %{buildroot}%{_unitdir}
install -D -m 0644 %{_sourcedir}/varnish.service %{buildroot}%{_unitdir}/varnish.service
install -D -m 0644 %{_sourcedir}/varnishncsa.service %{buildroot}%{_unitdir}/varnishncsa.service
install -D -m 0755 %{_sourcedir}/varnishreload %{buildroot}%{_sbindir}/varnishreload

echo %{_libdir}/varnish > %{buildroot}%{_sysconfdir}/ld.so.conf.d/varnish-%{_arch}.conf


%clean
rm -rf %{buildroot}


%files
%{_sbindir}/*
%{_bindir}/*
%{_libdir}/*.so.*
%{_libdir}/varnish
%{_var}/lib/varnish
%{_mandir}/man1/*.1*
%{_mandir}/man3/*.3*
%{_mandir}/man7/*.7*
%{_docdir}/varnish/
%{_datadir}/varnish
%{_unitdir}/*
%attr(-,varnishlog,varnish) %{_var}/log/varnish
%exclude %{_datadir}/varnish/vmodtool*
%exclude %{_datadir}/varnish/vsctool*
%doc README*
%doc LICENSE
%doc doc/html
%doc doc/changes*.html
%doc doc/changes*.rst
%dir %{_sysconfdir}/varnish/
%config(noreplace) %{_sysconfdir}/varnish/default.vcl
%config(noreplace) %{_sysconfdir}/logrotate.d/varnish
%config %{_sysconfdir}/ld.so.conf.d/varnish-%{_arch}.conf


%files devel
%{_libdir}/lib*.so
%{_includedir}/varnish
%{_libdir}/pkgconfig/varnishapi.pc
%{_datadir}/varnish/vmodtool*
%{_datadir}/varnish/vsctool*
%{_datadir}/aclocal/*


%pre
getent group varnish >/dev/null ||
groupadd -r varnish

getent passwd varnishlog >/dev/null ||
useradd -r -g varnish -d /dev/null -s /sbin/nologin \
	-c "varnishlog user" varnishlog

getent passwd varnish >/dev/null ||
useradd -r -g varnish -d /var/lib/varnish -s /sbin/nologin \
	-c "Varnish Cache" varnish

exit 0


%post
/sbin/ldconfig
%systemd_post varnish varnishncsa


%preun
%systemd_preun varnish varnishncsa


%postun
/sbin/ldconfig
%systemd_postun_with_restart varnish varnishncsa


%changelog
* Thu May 20 2021 Geoff Simmons <geoff@uplex.de> - 6.6.0-1
- RPM for varnish-maxwait, Varnish 6.6.0 with the req_total_timeout
  parameter and maxwait feature for ESI includes.
