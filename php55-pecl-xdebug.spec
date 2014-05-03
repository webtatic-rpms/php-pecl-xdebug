%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}

# Build ZTS extension or only NTS
%global with_zts      1

%define basepkg   php55w
%define pecl_name xdebug

Name:           %{basepkg}-pecl-xdebug
Version:        2.2.5
Release:        1%{?dist}
Summary:        PECL package for debugging PHP scripts

License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/xdebug
Source0:        http://pecl.php.net/get/xdebug-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  automake %{basepkg}-devel %{basepkg}-pear >= 1:1.4.9-1.2

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
%setup -qc
[ -f package2.xml ] || mv package.xml package2.xml
mv package2.xml %{pecl_name}.xml

%if %{with_zts}
cp -r %{pecl_name}-%{version} %{pecl_name}-%{version}-zts
%endif


%build
pushd %{pecl_name}-%{version}
phpize
%configure --enable-xdebug --with-php-config=%{_bindir}/php-config
CFLAGS="$RPM_OPT_FLAGS" make

# Build debugclient
pushd debugclient
cp %{_datadir}/automake-1.?*/depcomp .
chmod +x configure
%configure %{config_flags}
CFLAGS="$RPM_OPT_FLAGS" make
popd
popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts
zts-phpize
%configure --enable-xdebug --with-php-config=%{_bindir}/zts-php-config
CFLAGS="$RPM_OPT_FLAGS" make
popd
%endif


%install
rm -rf $RPM_BUILD_ROOT

pushd %{pecl_name}-%{version}

# install NZTS extension
make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install debugclient
install -d $RPM_BUILD_ROOT%{_bindir}
install -pm 755 debugclient/debugclient $RPM_BUILD_ROOT%{_bindir}

# install config file
install -d $RPM_BUILD_ROOT%{php_inidir}
cat > $RPM_BUILD_ROOT%{php_inidir}/%{pecl_name}.ini << 'EOF'
; Enable xdebug extension module
zend_extension=%{php_extdir}/%{pecl_name}.so
EOF

popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts

# install ZTS extension
make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install config file
install -d $RPM_BUILD_ROOT%{php_ztsinidir}
cat > $RPM_BUILD_ROOT%{php_ztsinidir}/%{pecl_name}.ini << 'EOF'
; Enable xdebug extension module
zend_extension=%{php_ztsextdir}/%{pecl_name}.so
EOF

popd
%endif


# Install XML package description
install -d $RPM_BUILD_ROOT%{pecl_xmldir}
install -pm 644 %{pecl_name}.xml $RPM_BUILD_ROOT%{pecl_xmldir}/%{pecl_name}.xml


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
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
%doc %{pecl_name}-%{version}/{CREDITS,LICENSE,NEWS,README}
%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{_bindir}/debugclient
%{pecl_xmldir}/%{pecl_name}.xml
%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Sat May 03 2014 Andy Thompson <andy@webtatic.com> 2.2.5-1
- Add ZTS extension compilation

* Sat Jul 20 2013 Andy Thompson <andy@webtatic.com> 2.2.3-2
- Add ZTS extension compilation

* Fri May 24 2013 Andy Thompson <andy@webtatic.com> 2.2.3-1
- branch from php54w-pecl-xdebug
