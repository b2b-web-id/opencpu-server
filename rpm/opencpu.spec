Name: opencpu
Version: 1.5.2
Release: rpm0
Source: opencpu-server-%{version}.tar.gz
License: Apache2
Summary: The OpenCPU system for embedded scientific computing and reproducible research.
Group: Applications/Internet
Buildroot: %{_tmppath}/%{name}-buildroot
URL: http://www.opencpu.org
BuildRequires: R-devel >= 3.0.2
BuildRequires: glibc-devel
BuildRequires: libcurl-devel
BuildRequires: protobuf-devel
BuildRequires: openssl-devel
BuildRequires: libxml2-devel
BuildRequires: libicu-devel
BuildRequires: libssh2-devel
BuildRequires: pkgconfig
BuildRequires: make
Requires: opencpu-server

%description
The OpenCPU system exposes an HTTP API for embedded scientific computing with R. This provides reliable and scalable foundations for integrating R based analysis and visualization modules into pipelines, web applications or big data infrastructures. The OpenCPU server can run either as a single-user development server within the interactive R session, or as a high performance multi-user cloud server that builds on Linux, Nginx and rApache.

%package lib
Summary: OpenCPU package library.
Group: Applications/Internet
Requires: R-devel >= 3.0.2
Requires: make
Requires: wget
Requires: unzip
Requires: protobuf
Requires: libcurl-devel
Requires: openssl-devel
Requires: libxml2-devel
Requires: libicu-devel
Requires: libssh2-devel
Autoreq: no

%description lib
This RPM package contains a frozen library of platform specific builds of R packages required by the OpenCPU system.

%package server
Summary: The OpenCPU API server.
Group: Applications/Internet
Requires: opencpu-lib
Requires: rapache
Requires: mod_ssl
Requires: MTA
Requires: /usr/sbin/semanage
Requires: /usr/sbin/semodule
Requires: /usr/sbin/sestatus
Requires: /usr/bin/checkmodule
Requires: /usr/bin/semodule_package

%description server
The OpenCPU cloud server builds on R and Apache2 (httpd) to expose the OpenCPU HTTP API.

%prep
%setup -n opencpu-server-%{version}

%build
NO_APPARMOR=1 make library

%install
# For opencpu-lib:
mkdir -p  %{buildroot}/usr/lib/opencpu/library
cp -Rf opencpu-lib/build/* %{buildroot}/usr/lib/opencpu/library/
cp -f opencpu-lib/symlinks/* %{buildroot}%{_libdir}/R/library/
# For opencpu-server:
sed -i s/www-data/apache/g opencpu-server/cron.d/opencpu
sed -i s/www-data/apache/g opencpu-server/scripts/cleanocpu.sh
mkdir -p %{buildroot}/etc/httpd/conf.d
mkdir -p %{buildroot}/etc/cron.d
mkdir -p %{buildroot}/usr/lib/opencpu/scripts
mkdir -p %{buildroot}/usr/lib/opencpu/rapache
mkdir -p %{buildroot}/usr/lib/opencpu/selinux
mkdir -p %{buildroot}/etc/opencpu
mkdir -p %{buildroot}/var/log/opencpu
cp -Rf opencpu-server/sites-available/* %{buildroot}/etc/httpd/conf.d/
cp -Rf opencpu-server/cron.d/* %{buildroot}/etc/cron.d/
cp -Rf opencpu-server/scripts/* %{buildroot}/usr/lib/opencpu/scripts/
cp -Rf opencpu-server/rapache/* %{buildroot}/usr/lib/opencpu/rapache/
cp -Rf opencpu-server/selinux/* %{buildroot}/usr/lib/opencpu/selinux/
cp -Rf opencpu-server/conf/* %{buildroot}/etc/opencpu/
cp -Rf server.conf %{buildroot}/etc/opencpu/

%post server
chmod +x /usr/lib/opencpu/scripts/*.sh
touch /var/log/opencpu/access.log
touch /var/log/opencpu/error.log
SELINUX_ENABLED=$(sestatus | grep "SELinux.status.*enabled")
#1 means first install
if [ "$1" = 1 ] && [ "$SELINUX_ENABLED" ]; then
  setsebool -P httpd_setrlimit=1 httpd_can_network_connect_db=1 httpd_can_network_connect=1 httpd_can_sendmail=1 httpd_read_user_content=1 || true
  semanage port -a -t http_port_t -p tcp 8004 || true
  checkmodule -M -m -o opencpu.mod /usr/lib/opencpu/selinux/opencpu.te || true
  semodule_package -o opencpu.pp -m opencpu.mod
  semodule -i opencpu.pp
fi
apachectl restart || true

%postun server
#0 means uninstall
if [ "$1" = 0 ] ; then
  rm -Rf /etc/opencpu
  rm -Rf /var/log/opencpu
  semanage port -d -t http_port_t -p tcp 8004 || true
  semodule -r opencpu || true
fi
apachectl restart || true

%files

%files lib
/usr/lib/opencpu/library
%{_libdir}/R/library

%files server
/usr/lib/opencpu/scripts
/usr/lib/opencpu/rapache
/usr/lib/opencpu/selinux
/etc/cron.d
/etc/httpd/conf.d
%dir /var/log/opencpu
%config(noreplace) /etc/opencpu/*
