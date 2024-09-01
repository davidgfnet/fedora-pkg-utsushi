%{!?upstream:   %define upstream utsushi}
%{!?uversion:   %define uversion 839d06a5a80b353cb604eb9f7d352a1648ab1fdf}

Name:           utsushi
Version:        3.65.0
Release:        2%{?dist}
Summary:        Next Generation Image Acquisition Utilities

Vendor:         SEIKO EPSON CORPORATION
License:        GPLv3+
URL:            https://gitlab.com/utsushi/utsushi
Source0:        https://gitlab.com/utsushi/utsushi/-/archive/%{uversion}/utsushi-%{uversion}.tar.gz
Patch0:         utsushi.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       GraphicsMagick

BuildRequires:  gcc-c++, gettext-devel, git, libxslt
BuildRequires:  pkgconfig, libtool-ltdl-devel, libtool, autoconf, autoconf-archive
BuildRequires:  sane-backends-devel, libjpeg-devel
BuildRequires:  libtiff-devel, GraphicsMagick
BuildRequires:  boost-devel
BuildRequires:  systemd-devel
BuildRequires:  libusb1-devel, GraphicsMagick-c++-devel

%description
This software provides applications to easily turn hard-copy documents
and imagery into formats that are more amenable to computer processing.

Included are a native driver for a number of EPSON scanners and a
compatibility driver to interface with software built around the SANE
standard.


%if ! 0%{?_enable_debug_packages}
%debug_package
%endif

%prep
%setup -q -n %{upstream}-%{uversion}
%patch -P 0 -p1
./bootstrap

%define CXX CXX='%{__cxx} -std=c++11 -Wno-deprecated-declarations'
%define udev_d %(pkg-config --variable=udevdir udev)

%build
export CFLAGS="${CFLAGS} -Wno-alloc-size-larger-than"
export CXXFLAGS="${CXXFLAGS} -Wno-alloc-size-larger-than"
%configure \
    --with-jpeg \
    --with-tiff \
    --with-sane \
    --with-magick \
    --with-magick-pp \
    --disable-static \
    --with-udev-confdir=%{udev_d} \
    %{?CXX}
make %{?_smp_mflags} BACKEND_NAME=%{name}

%install
rm -rf %{buildroot}
make install BACKEND_NAME=%{name} DESTDIR=%{buildroot}
mv %{buildroot}%{udev_d}/rules.d/%{upstream}-esci.rules \
   %{buildroot}%{udev_d}/rules.d/70-%{name}.rules
rm -rf %{buildroot}%{_includedir}
%find_lang %{upstream}

%clean
rm -rf %{buildroot}


%define have_sane_dll_d %(test -d %{_sysconfdir}/sane.d/dll.d && echo true)

%files -f %{upstream}.lang
%defattr(-,root,root,-)
%doc NEWS README AUTHORS
%doc COPYING
%{_bindir}/%{name}
%{_libdir}/%{upstream}/
%if "%{_libdir}" != "%{_libexecdir}"
%{_libexecdir}/%{upstream}/
%endif
%{_libdir}/sane/libsane-%{name}.*
%{_datadir}/%{upstream}/
%config(noreplace) %{_sysconfdir}/%{name}/combo.conf
%if "true" == "%{have_sane_dll_d}"
%{_sysconfdir}/sane.d/dll.d/%{name}
%endif
%{udev_d}/rules.d/70-%{name}.rules


%if "true" != "%{have_sane_dll_d}"
#
#  Modify SANE's dll.conf during (un)installation
#
%post
dll=%{_sysconfdir}/sane.d/dll.conf
if [ -n "`grep '^[ \t]*#[ \t#]*%{name}' ${dll}`" ]
then                            # uncomment existing entry
    sed -i 's,^[ \t]*#[ \t#]*\(%{name}\),\1,' ${dll}
elif [ -z "`grep %{name} ${dll}`" ]
then                            # append brand new entry
    echo %{name} >> ${dll}
fi

%preun
if [ $1 = 0 ]
then                            # comment out existing entry
    dll=%{_sysconfdir}/sane.d/dll.conf
    if [ -n "`grep '^[ \t]*%{name}' ${dll}`" ]
    then
        sed -i 's,^[ \t]*\(%{name}\),#\1,' ${dll}
    fi
fi
%endif


%changelog
* Thu Dec 22 2020 Seiko Epson <linux-printer@epson.jp> - 3.65.0-1
- new upstream

