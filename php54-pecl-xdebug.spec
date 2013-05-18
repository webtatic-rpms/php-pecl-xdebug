%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?php_extdir: %{expand: %%global php_extdir %(php-config --extension-dir)}}

%define pecl_name xdebug

Name:           php54w-pecl-xdebug
Version:        2.2.2
Release:        1%{?dist}
Summary:        PECL package for debugging PHP scripts

License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/xdebug
Source0:        http://pecl.php.net/get/xdebug-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  automake php54w-devel php54w-pear >= 1:1.4.9-1.2

%if 0%{?fedora}
%define config_flags --with-libedit
BuildRequires:  libedit-devel
%else
%define config_flags --without-libedit
%endif

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Provides:       php-pecl(Xdebug) = %{version}

%if 0%{?php_zend_api}
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
%else
Requires:       php-api = %{php_apiver}
%endif

%description
The Xdebug extension helps you debugging your script by providing a lot
of valuable debug information.


%prep
%setup -qcn xdebug-%{version}
[ -f package2.xml ] || mv package.xml package2.xml
mv package2.xml %{pecl_name}-%{version}/%{pecl_name}.xml
cd xdebug-%{version}


%build
cd xdebug-%{version}
phpize
%configure --enable-xdebug
CFLAGS="$RPM_OPT_FLAGS" make

# Build debugclient
pushd debugclient
cp %{_datadir}/automake-1.?*/depcomp .
chmod +x configure
%configure %{config_flags}
CFLAGS="$RPM_OPT_FLAGS" make
popd


%install
cd xdebug-%{version}
rm -rf $RPM_BUILD_ROOT
make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install debugclient
install -d $RPM_BUILD_ROOT%{_bindir}
install -pm 755 debugclient/debugclient $RPM_BUILD_ROOT%{_bindir}

# install config file
install -d $RPM_BUILD_ROOT%{_sysconfdir}/php.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/php.d/xdebug.ini << 'EOF'
; Enable xdebug extension module
zend_extension=%{php_extdir}/xdebug.so
EOF

# install doc files
install -d docs
install -pm 644 CREDITS LICENSE NEWS README docs

# Install XML package description
install -d $RPM_BUILD_ROOT%{pecl_xmldir}
install -pm 644 %{pecl_name}.xml $RPM_BUILD_ROOT%{pecl_xmldir}/%{name}.xml


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc xdebug-%{version}/docs/*
%config(noreplace) %{_sysconfdir}/php.d/xdebug.ini
%{php_extdir}/xdebug.so
%{_bindir}/debugclient
%{pecl_xmldir}/%{name}.xml


%changelog
* Sat May 18 2013 Andy Thompson <andy@webtatic.com> 2.2.2-1
- update to 2.2.2

* Sun Jul 22 2012 Andy Thompson <andy@webtatic.com> 2.2.1-1
- branch from php53-pecl-xdebug
- update to 2.2.1
