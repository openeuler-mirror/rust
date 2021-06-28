%global rust_arches x86_64 i686 armv7hl aarch64 ppc64 ppc64le s390x
%{!?channel: %global channel stable}
%global bootstrap_rust 1.50.0
%global bootstrap_cargo 1.50.0
%global bootstrap_channel 1.50.0
%global bootstrap_date 2021-02-11
%bcond_with llvm_static
%bcond_with bundled_llvm
%bcond_without bundled_libgit2
%bcond_with disabled_libssh2
%bcond_without curl_http2
%bcond_without lldb
Name:                rust
Version:             1.51.0
Release:             4
Summary:             The Rust Programming Language
License:             (ASL 2.0 or MIT) and (BSD and MIT)
URL:                 https://www.rust-lang.org
ExclusiveArch:       %{rust_arches}
%if "%{channel}" == "stable"
%global rustc_package rustc-%{version}-src
%else
%global rustc_package rustc-%{channel}-src
%endif
Source0:             https://static.rust-lang.org/dist/%{rustc_package}.tar.xz
Source1:             rustc-%{version}-src.tar.xz.aa
Source2:             rustc-%{version}-src.tar.xz.ab

Patch0001:           0001-Revert-Auto-merge-of-79547.patch
Patch0002:           rustc-1.51.0-backport-pr81741.patch
Patch0003:           rustc-1.51.0-backport-pr82289.patch
Patch0004:           rustc-1.51.0-backport-pr82292.patch
Patch0005:           rustc-1.51.0-backport-pr81910.patch
Patch0006:           rustc-1.51.0-backport-pr81728.patch
Patch0007:           rustc-1.51.0-backport-pr83629.patch
Patch0008:           rustc-1.48.0-disable-libssh2.patch
Patch0009:           rustc-1.51.0-disable-http2.patch
Patch0010:           clippy-driver-usage-should-user-friendly.patch
Patch0011:           cargo-help-clippy-should-have-description-to-user.patch
Patch0012:           fix-a-println-wrong-format.patch
%{lua: function rust_triple(arch)
  local abi = "gnu"
  if arch == "armv7hl" then
    arch = "armv7"
    abi = "gnueabihf"
  elseif arch == "ppc64" then
    arch = "powerpc64"
  elseif arch == "ppc64le" then
    arch = "powerpc64le"
  elseif arch == "riscv64" then
    arch = "riscv64gc"
  end
  return arch.."-unknown-linux-"..abi
end}
%global rust_triple %{lua: print(rust_triple(rpm.expand("%{_target_cpu}")))}
%if %defined bootstrap_arches
%{lua: do
  local bootstrap_arches = {}
  for arch in string.gmatch(rpm.expand("%{bootstrap_arches}"), "%S+") do
    table.insert(bootstrap_arches, arch)
  end
  local base = rpm.expand("https://static.rust-lang.org/dist/%{bootstrap_date}"
                          .."/rust-%{bootstrap_channel}")
  local target_arch = rpm.expand("%{_target_cpu}")
  for i, arch in ipairs(bootstrap_arches) do
    print(string.format("Source%d: %s-%s.tar.xz\n",
                        i, base, rust_triple(arch)))
    if arch == target_arch then
      rpm.define("bootstrap_source "..i)
    end
  end
end}
%endif
%ifarch %{bootstrap_arches}
%global bootstrap_root rust-%{bootstrap_channel}-%{rust_triple}
%global local_rust_root %{_builddir}/%{bootstrap_root}/usr
Provides:            bundled(%{name}-bootstrap) = %{bootstrap_rust}
%else
BuildRequires:       cargo >= %{bootstrap_cargo}
BuildRequires:       (%{name} >= %{bootstrap_rust} with %{name} <= %{version})
%global local_rust_root %{_prefix}
%endif
BuildRequires:       make gcc gcc-c++ ncurses-devel curl curl-devel pkgconfig(libcurl) pkgconfig(liblzma)
BuildRequires:       pkgconfig(openssl) pkgconfig(zlib) pkgconfig(libssh2) >= 1.6.0
%global python python3
BuildRequires:       %{python}
%if %with bundled_llvm
BuildRequires:       cmake3 >= 3.4.3
Provides:            bundled(llvm) = 11.0.1
%else
BuildRequires:       cmake >= 2.8.11
%if %defined llvm
%global llvm_root %{_libdir}/%{llvm}
%else
%global llvm llvm
%global llvm_root %{_prefix}
%endif
BuildRequires:       %{llvm}-devel >= 9.0
%if %with llvm_static
BuildRequires:       %{llvm}-static libffi-devel
%endif
%endif
BuildRequires:       procps-ng gdb
Provides:            rustc = %{version}-%{release}
Provides:            rustc%{?_isa} = %{version}-%{release}
Requires:            %{name}-std-static%{?_isa} = %{version}-%{release}
Requires:            /usr/bin/cc
%global _privatelibs lib(.*-[[:xdigit:]]{16}*|rustc.*)[.]so.*
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$
%global __provides_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$
%global __requires_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$
%global _find_debuginfo_opts --keep-section .rustc
%global rustflags -Clink-arg=-Wl,-z,relro,-z,now
%if %{without bundled_llvm}
%if "%{llvm_root}" == "%{_prefix}" || 0%{?scl:1}
%global llvm_has_filecheck 1
%endif
%endif
%description
Rust is a systems programming language that runs blazingly fast, prevents
segfaults, and guarantees thread safety.
This package includes the Rust compiler and documentation generator.

%package std-static
Summary:             Standard library for Rust
%description std-static
This package includes the standard libraries for building applications
written in Rust.

%package debugger-common
Summary:             Common debugger pretty printers for Rust
BuildArch:           noarch
%description debugger-common
This package includes the common functionality for %{name}-gdb and %{name}-lldb.

%package gdb
Summary:             GDB pretty printers for Rust
BuildArch:           noarch
Requires:            gdb %{name}-debugger-common = %{version}-%{release}
%description gdb
This package includes the rust-gdb script, which allows easier debugging of Rust
programs.

%package lldb
Summary:             LLDB pretty printers for Rust
BuildArch:           noarch
Requires:            lldb %{python}-lldb
Requires:            %{name}-debugger-common = %{version}-%{release}

%description lldb
This package includes the rust-lldb script, which allows easier debugging of Rust
programs.

%package -n cargo
Summary:             Rust's package manager and build tool
%if %with bundled_libgit2
Provides:            bundled(libgit2) = 1.1.0
%endif
BuildRequires:       git
Requires:            rust
Obsoletes:           cargo-vendor <= 0.1.23
Provides:            cargo-vendor = %{version}-%{release}
%description -n cargo
Cargo is a tool that allows Rust projects to declare their various dependencies
and ensure that you'll always get a repeatable build.

%package -n rustfmt
Summary:             Tool to find and fix Rust formatting issues
Requires:            cargo
Obsoletes:           rustfmt-preview < 1.0.0
Provides:            rustfmt-preview = %{version}-%{release}
Conflicts:           rustfmt-preview < 1.0.0
%description -n rustfmt
A tool for formatting Rust code according to style guidelines.

%package -n rls
Summary:             Rust Language Server for IDE integration
%if %with bundled_libgit2
Provides:            bundled(libgit2) = 1.1.0
%endif
Requires:            rust-analysis %{name}%{?_isa} = %{version}-%{release}
Obsoletes:           rls-preview < 1.31.6
Provides:            rls-preview = %{version}-%{release}
Conflicts:           rls-preview < 1.31.6

%description -n rls
The Rust Language Server provides a server that runs in the background,
providing IDEs, editors, and other tools with information about Rust programs.
It supports functionality such as 'goto definition', symbol search,
reformatting, and code completion, and enables renaming and refactorings.

%package -n clippy
Summary:             Lints to catch common mistakes and improve your Rust code
Requires:            cargo %{name}%{?_isa} = %{version}-%{release}
Obsoletes:           clippy-preview <= 0.0.212
Provides:            clippy-preview = %{version}-%{release}
Conflicts:           clippy-preview <= 0.0.212
%description -n clippy
A collection of lints to catch common mistakes and improve your Rust code.

%package src
Summary:             Sources for the Rust standard library
BuildArch:           noarch
%description src
This package includes source files for the Rust standard library.  It may be
useful as a reference for code completion tools in various editors.

%package analysis
Summary:             Compiler analysis data for the Rust standard library
Requires:            rust-std-static%{?_isa} = %{version}-%{release}
%description analysis
This package contains analysis data files produced with rustc's -Zsave-analysis
feature for the Rust standard library. The RLS (Rust Language Server) uses this
data to provide information about the Rust standard library.

%package help
Summary:     Help documents for rust

Provides:    %{name}-doc = %{version}-%{release} %{name}-cargo-doc = %{version}-%{release}
Obsoletes:   %{name}-doc < %{version}-%{release} %{name}-cargo-doc < %{version}-%{release}

%description help
Man pages and other related help documents for rust.

%prep
cd ../SOURCES
cat %{SOURCE1} %{SOURCE2} | tar xJ
cd ..

%ifarch %{bootstrap_arches}
%setup -q -n %{bootstrap_root} -T -b %{bootstrap_source}
./install.sh --components=cargo,rustc,rust-std-%{rust_triple} \
  --prefix=%{local_rust_root} --disable-ldconfig
test -f '%{local_rust_root}/bin/cargo'
test -f '%{local_rust_root}/bin/rustc'
%endif
%setup -q -n %{rustc_package}
%patch0001 -p1
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1
%patch0005 -p1
%patch0006 -p1
%patch0007 -p1
%if %with disabled_libssh2
%patch0008 -p1
%endif
%if %without curl_http2
%patch0009 -p1
rm -rf vendor/libnghttp2-sys/
%endif
%if "%{python}" != "python3"
sed -i.try-python -e '/^try python3 /i try "%{python}" "$@"' ./configure
%endif
%if %without bundled_llvm
rm -rf src/llvm-project/
mkdir -p src/llvm-project/libunwind/
%endif
%patch0010 -p1
%patch0011 -p1
%patch0012 -p1
rm -rf vendor/curl-sys/curl/
rm -rf vendor/jemalloc-sys/jemalloc/
rm -rf vendor/libssh2-sys/libssh2/
rm -rf vendor/libz-sys/src/zlib/
rm -rf vendor/libz-sys/src/zlib-ng/
rm -rf vendor/lzma-sys/xz-*/
rm -rf vendor/openssl-src/openssl/
%if %without bundled_libgit2
rm -rf vendor/libgit2-sys/libgit2/
%endif
%if %with disabled_libssh2
rm -rf vendor/libssh2-sys/
%endif
sed -i.lzma -e '/LZMA_API_STATIC/d' src/bootstrap/tool.rs
%if %{without bundled_llvm} && %{with llvm_static}
sed -i.ffi -e '$a #[link(name = "ffi")] extern {}' \
  src/librustc_llvm/lib.rs
%endif
find vendor -name .cargo-checksum.json \
  -exec sed -i.uncheck -e 's/"files":{[^}]*}/"files":{ }/' '{}' '+'
find -name '*.rs' -type f -perm /111 -exec chmod -v -x '{}' '+'
%global rust_env RUSTFLAGS="%{rustflags}"
%if 0%{?cmake_path:1}
%global rust_env %{rust_env} PATH="%{cmake_path}:$PATH"
%endif
%if %without bundled_libgit2
%global rust_env %{rust_env} LIBGIT2_SYS_USE_PKG_CONFIG=1
%endif
%if %without disabled_libssh2
%global rust_env %{rust_env} LIBSSH2_SYS_USE_PKG_CONFIG=1
%endif

%build
export %{rust_env}
%global common_libdir %{_prefix}/lib
%global rustlibdir %{common_libdir}/rustlib
%ifarch %{arm} %{ix86} s390x
%define enable_debuginfo --debuginfo-level=0 --debuginfo-level-std=2
%else
%define enable_debuginfo --debuginfo-level=2
%endif
%ifnarch %{power64}
%define codegen_units_std --set rust.codegen-units-std=1
%endif
ncpus=$(/usr/bin/getconf _NPROCESSORS_ONLN)
max_cpus=$(( ($(free -g | awk '/^Mem:/{print $2}') + 1) / 2 ))
if [ "$max_cpus" -ge 1 -a "$max_cpus" -lt "$ncpus" ]; then
  ncpus="$max_cpus"
fi
%configure --disable-option-checking \
  --libdir=%{common_libdir} \
  --build=%{rust_triple} --host=%{rust_triple} --target=%{rust_triple} \
  --python=%{python} \
  --local-rust-root=%{local_rust_root} \
  %{!?with_bundled_llvm: --llvm-root=%{llvm_root} \
    %{!?llvm_has_filecheck: --disable-codegen-tests} \
    %{!?with_llvm_static: --enable-llvm-link-shared } } \
  --disable-rpath \
  %{enable_debuginfo} \
  --enable-extended \
  --tools=analysis,cargo,clippy,rls,rustfmt,src \
  --enable-vendor \
  --enable-verbose-tests \
  %{?codegen_units_std} \
  --release-channel=%{channel}
%{python} ./x.py build -j "$ncpus" --stage 2
%{python} ./x.py doc --stage 2

%install
export %{rust_env}
DESTDIR=%{buildroot} %{python} ./x.py install
%if "%{_libdir}" != "%{common_libdir}"
mkdir -p %{buildroot}%{_libdir}
find %{buildroot}%{common_libdir} -maxdepth 1 -type f -name '*.so' \
  -exec mv -v -t %{buildroot}%{_libdir} '{}' '+'
%endif
find %{buildroot}%{_libdir} -maxdepth 1 -type f -name '*.so' \
  -exec chmod -v +x '{}' '+'
(cd "%{buildroot}%{rustlibdir}/%{rust_triple}/lib" &&
 find ../../../../%{_lib} -maxdepth 1 -name '*.so' |
 while read lib; do
   if [ -f "${lib##*/}" ]; then
     # make sure they're actually identical!
     cmp "$lib" "${lib##*/}"
     ln -v -f -s -t . "$lib"
   fi
 done)
find %{buildroot}%{rustlibdir} -maxdepth 1 -type f -exec rm -v '{}' '+'
find %{buildroot}%{rustlibdir} -type f -name '*.orig' -exec rm -v '{}' '+'
find %{buildroot}%{rustlibdir}/src -type f -name '*.py' -exec rm -v '{}' '+'
rm -f %{buildroot}%{_docdir}/%{name}/README.md
rm -f %{buildroot}%{_docdir}/%{name}/COPYRIGHT
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE-APACHE
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE-MIT
rm -f %{buildroot}%{_docdir}/%{name}/LICENSE-THIRD-PARTY
rm -f %{buildroot}%{_docdir}/%{name}/*.old
find %{buildroot}%{_docdir}/%{name}/html -empty -delete
find %{buildroot}%{_docdir}/%{name}/html -type f -exec chmod -x '{}' '+'
mkdir -p %{buildroot}%{_datadir}/cargo/registry
mkdir -p %{buildroot}%{_docdir}/cargo
ln -sT ../rust/html/cargo/ %{buildroot}%{_docdir}/cargo/html
%if %without lldb
rm -f %{buildroot}%{_bindir}/rust-lldb
rm -f %{buildroot}%{rustlibdir}/etc/lldb_*
%endif
rm -f %{buildroot}%{rustlibdir}/%{rust_triple}/bin/rust-ll*

%check
export %{rust_env}
%{python} ./x.py test --no-fail-fast --stage 2 || :
%{python} ./x.py test --no-fail-fast --stage 2 cargo || :
%{python} ./x.py test --no-fail-fast --stage 2 clippy || :
%{python} ./x.py test --no-fail-fast --stage 2 rls || :
%{python} ./x.py test --no-fail-fast --stage 2 rustfmt || :
%ldconfig_scriptlets

%files
%license COPYRIGHT LICENSE-APACHE LICENSE-MIT
%license %{_docdir}/%{name}/html/*.txt
%doc README.md
%{_bindir}/rustc
%{_bindir}/rustdoc
%{_libdir}/*.so
%dir %{rustlibdir}
%dir %{rustlibdir}/%{rust_triple}
%dir %{rustlibdir}/%{rust_triple}/lib
%{rustlibdir}/%{rust_triple}/lib/*.so

%files std-static
%dir %{rustlibdir}
%dir %{rustlibdir}/%{rust_triple}
%dir %{rustlibdir}/%{rust_triple}/lib
%{rustlibdir}/%{rust_triple}/lib/*.rlib

%files debugger-common
%dir %{rustlibdir}
%dir %{rustlibdir}/etc
%{rustlibdir}/etc/rust_*.py*

%files gdb
%{_bindir}/rust-gdb
%{rustlibdir}/etc/gdb_*
%exclude %{_bindir}/rust-gdbgui
%if %with lldb

%files lldb
%{_bindir}/rust-lldb
%{rustlibdir}/etc/lldb_*
%endif

%files -n cargo
%license src/tools/cargo/LICENSE-APACHE src/tools/cargo/LICENSE-MIT src/tools/cargo/LICENSE-THIRD-PARTY
%doc src/tools/cargo/README.md
%{_bindir}/cargo
%{_libexecdir}/cargo*
%{_sysconfdir}/bash_completion.d/cargo
%{_datadir}/zsh/site-functions/_cargo
%dir %{_datadir}/cargo
%dir %{_datadir}/cargo/registry

%files -n rustfmt
%{_bindir}/rustfmt
%{_bindir}/cargo-fmt
%doc src/tools/rustfmt/{README,CHANGELOG,Configurations}.md
%license src/tools/rustfmt/LICENSE-{APACHE,MIT}

%files -n rls
%{_bindir}/rls
%doc src/tools/rls/{README.md,COPYRIGHT,debugging.md}
%license src/tools/rls/LICENSE-{APACHE,MIT}

%files -n clippy
%{_bindir}/cargo-clippy
%{_bindir}/clippy-driver
%doc src/tools/clippy/{README.md,CHANGELOG.md}
%license src/tools/clippy/LICENSE-{APACHE,MIT}

%files src
%dir %{rustlibdir}
%{rustlibdir}/src

%files analysis
%{rustlibdir}/%{rust_triple}/analysis/

%files help
%dir %{_docdir}/%{name}
%dir %{_docdir}/cargo
%dir %{_docdir}/%{name}/html
%docdir %{_docdir}/%{name}
%docdir %{_docdir}/cargo
%{_docdir}/%{name}/html/*/
%{_docdir}/%{name}/html/*.html
%{_docdir}/%{name}/html/*.css
%{_docdir}/%{name}/html/*.js
%{_docdir}/%{name}/html/*.png
%{_docdir}/%{name}/html/*.svg
%{_docdir}/%{name}/html/*.woff
%license %{_docdir}/%{name}/html/*.md
%{_docdir}/cargo/html
%{_mandir}/man1/rustc.1*
%{_mandir}/man1/rustdoc.1*
%{_mandir}/man1/cargo*.1*

%changelog
* Thu 24 Jun 2021 sunguoshuai <sunguoshuai@huawei.com> - 1.51.0-4
- fix a println wrong format

* Thu 24 Jun 2021 sunguoshuai <sunguoshuai@huawei.com> - 1.51.0-3
- cargo help clippy should have description to user

* Wed 23 Jun 2021 sunguoshuai <sunguoshuai@huawei.com> - 1.51.0-2
- clippy-driver usage should user friendly

* Fri May 07 2021 wangyue <wangyue92@huawei.com> - 1.51.0-1
- Update to 1.51.0

* Mon Nov 30 2020 Jeffery.Gao <gaojianxing@huawei.com> - 1.45.2-2
- fix upgrade error

* Mon Sep 21 2020 Jeffery.Gao <gaojianxing@huawei.com> - 1.45.2-1
- Update to 1.45.2

* Mon Apr 17 2020 zhujunhao <zhujunhao8@huawei.com> - 1.29.1-4
- add llvm in rust

* Thu Dec 5 2019 wutao <wutao61@huawei.com> - 1.29.1-3
- Package init
